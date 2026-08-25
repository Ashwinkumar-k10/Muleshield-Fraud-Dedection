import os
import sys
import json
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import precision_recall_curve, auc, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from imblearn.over_sampling import SMOTE
import xgboost as xgb

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modeling.preprocessor import MuleShieldPreprocessor

# 1. Load Raw Data
raw_csv_path = os.path.join('data', 'data_copy.csv')
print("Loading raw dataset from:", raw_csv_path, flush=True)
df_raw = pd.read_csv(raw_csv_path, engine='pyarrow')
account_ids = df_raw.iloc[:, 0].values

y_raw = df_raw['F3924'].astype(int).values
X_raw = df_raw.drop(columns=['F3924'])

# 2. Preprocess & Feature Audit
preprocessor = MuleShieldPreprocessor()
X_processed = preprocessor.fit_transform(X_raw)

# Drop post-incident resolution flags & date proxies
post_incident_base_cols = ['F3898', 'F3899', 'F3912', 'F3913', 'F3914', 'F3915']
post_inc_cols = [c for c in X_processed.columns if any(c.startswith(p) for p in post_incident_base_cols)]
if 'F2230' in X_processed.columns:
    post_inc_cols.append('F2230')
if 'F3888' in X_processed.columns:
    post_inc_cols.append('F3888')

X_clean = X_processed.drop(columns=post_inc_cols)

# Domain Feature Engineering
if 'F2122' in X_clean.columns and 'F670' in X_clean.columns:
    X_clean['BANK_FE_CASH_TO_UPI_RATIO'] = X_clean['F2122'] / (X_clean['F670'].abs() + 1.0)
if 'F2582' in X_clean.columns and 'F2737' in X_clean.columns:
    X_clean['BANK_FE_UPI_TO_TOTAL_DEV_RATIO'] = X_clean['F2582'] / (X_clean['F2737'].abs() + 1.0)
if 'F3887' in X_clean.columns and 'F3894' in X_clean.columns:
    X_clean['BANK_FE_TENURE_AGE_RATIO'] = X_clean['F3887'] / (X_clean['F3894'].abs() + 1.0)

# Convert all columns to float32 numeric
for c in X_clean.columns:
    X_clean[c] = pd.to_numeric(X_clean[c], errors='coerce').fillna(0.0).astype(np.float32)

print(f"Sanitized Feature Matrix: {X_clean.shape[0]} rows, {X_clean.shape[1]} features.", flush=True)

# 3. Group Clustering (>0.99 similarity)
X_norm = normalize(X_clean.values, norm='l2', axis=1)
sim_matrix = cosine_similarity(X_norm)
adj_matrix = csr_matrix(sim_matrix > 0.99)
n_components, groups = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)
print(f"Group isolation: {len(np.unique(groups))} clusters across {len(groups)} accounts.", flush=True)

# 4. Out-Of-Fold Pass (5-Fold Stratified Group CV)
cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
pos_weight = float(len(y_raw) - sum(y_raw)) / float(sum(y_raw))

params = {
    'max_depth': 3,
    'min_child_weight': 3,
    'gamma': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 1.0,
    'learning_rate': 0.05,
    'scale_pos_weight': pos_weight,
    'n_estimators': 200,
    'tree_method': 'hist',
    'random_state': 42,
    'eval_metric': 'logloss'
}

oof_preds = np.zeros(len(df_raw))
oof_folds = np.zeros(len(df_raw), dtype=int)
fold_pr_aucs = []

for fold, (train_idx, val_idx) in enumerate(cv.split(X_clean, y_raw, groups=groups)):
    X_tr, y_tr = X_clean.iloc[train_idx].values, y_raw[train_idx]
    X_va, y_va = X_clean.iloc[val_idx].values, y_raw[val_idx]
    
    # SMOTE fit ONLY on train
    sampler = SMOTE(random_state=42)
    X_tr_res, y_tr_res = sampler.fit_resample(X_tr, y_tr)
    
    model = xgb.XGBClassifier(**params)
    model.fit(X_tr_res, y_tr_res)
    
    val_probs = model.predict_proba(X_va)[:, 1]
    oof_preds[val_idx] = val_probs
    oof_folds[val_idx] = fold + 1
    
    p_f, r_f, _ = precision_recall_curve(y_va, val_probs)
    fold_pr_aucs.append(auc(r_f, p_f))

p_o, r_o, _ = precision_recall_curve(y_raw, oof_preds)
overall_oof_pr_auc = auc(r_o, p_o)
mean_fold_pr_auc = np.mean(fold_pr_aucs)
std_fold_pr_auc = np.std(fold_pr_aucs)

print("\n==========================================", flush=True)
print("PART A.1 — OUT-OF-FOLD (OOF) RESULTS", flush=True)
print("==========================================", flush=True)
print(f"Overall OOF PR-AUC:              {overall_oof_pr_auc:.4f}", flush=True)
print(f"5-Fold Mean ± Std PR-AUC:       {mean_fold_pr_auc:.4f} ± {std_fold_pr_auc:.4f}", flush=True)

# Compute baseline confusion matrix at threshold 0.9899
cm_09899 = confusion_matrix(y_raw, (oof_preds >= 0.9899).astype(int))
tn_09899, fp_09899, fn_09899, tp_09899 = cm_09899.ravel()
p_09899 = precision_score(y_raw, (oof_preds >= 0.9899).astype(int))
r_09899 = recall_score(y_raw, (oof_preds >= 0.9899).astype(int))
f1_09899 = f1_score(y_raw, (oof_preds >= 0.9899).astype(int))

print(f"OOF Metrics @ Threshold 0.9899: Precision={p_09899:.4f}, Recall={r_09899:.4f}, F1={f1_09899:.4f}, FP={fp_09899}, FN={fn_09899}, TP={tp_09899}, TN={tn_09899}", flush=True)

oof_df = pd.DataFrame({
    'account_id': account_ids,
    'true_label': y_raw,
    'oof_probability': oof_preds,
    'fold': oof_folds
})
oof_df.to_csv("scratch/oof_predictions.csv", index=False)
print("Saved OOF predictions to scratch/oof_predictions.csv", flush=True)

# PART A.2 — THRESHOLD ANALYSIS TABLE
target_thresholds = [0.50, 0.70, 0.90, 0.95, 0.97, 0.98, 0.985, 0.9899, 0.99, 0.995]
print("\n==========================================", flush=True)
print("PART A.2 — OOF THRESHOLD ANALYSIS TABLE", flush=True)
print("==========================================", flush=True)
print(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'FP Count':<10} | {'FN Count':<10} | {'TP':<6} | {'TN':<6}", flush=True)
print("-" * 75, flush=True)

for t in target_thresholds:
    preds = (oof_preds >= t).astype(int)
    cm = confusion_matrix(y_raw, preds)
    tn, fp, fn, tp = cm.ravel()
    p = precision_score(y_raw, preds, zero_division=0)
    r = recall_score(y_raw, preds, zero_division=0)
    f1 = f1_score(y_raw, preds, zero_division=0)
    print(f"{t:<10.4f} | {p:<10.4f} | {r:<10.4f} | {f1:<10.4f} | {fp:<10} | {fn:<10} | {tp:<6} | {tn:<6}", flush=True)

# PART A.3 — MISSING-VALUE STRESS TEST
print("\n==========================================", flush=True)
print("PART A.3 — MISSING-VALUE STRESS TEST", flush=True)
print("==========================================", flush=True)
np.random.seed(42)
X_stress = X_clean.copy()
num_cells = X_stress.size
num_nulls = int(0.10 * num_cells)

flat_indices = np.random.choice(num_cells, size=num_nulls, replace=False)
row_idx, col_idx = np.unravel_index(flat_indices, X_stress.shape)

values = X_stress.values.astype(np.float32)
for r, c in zip(row_idx, col_idx):
    values[r, c] = np.nan
X_stress_df = pd.DataFrame(values, columns=X_stress.columns, index=X_stress.index)

oof_stress_preds = np.zeros(len(df_raw))

for fold, (train_idx, val_idx) in enumerate(cv.split(X_clean, y_raw, groups=groups)):
    X_tr, y_tr = X_clean.iloc[train_idx].values, y_raw[train_idx]
    X_va_stress = X_stress_df.iloc[val_idx].values
    
    sampler = SMOTE(random_state=42)
    X_tr_res, y_tr_res = sampler.fit_resample(X_tr, y_tr)
    
    model = xgb.XGBClassifier(**params)
    model.fit(X_tr_res, y_tr_res)
    
    oof_stress_preds[val_idx] = model.predict_proba(X_va_stress)[:, 1]

p_s, r_s, _ = precision_recall_curve(y_raw, oof_stress_preds)
stress_pr_auc = auc(r_s, p_s)
degradation = overall_oof_pr_auc - stress_pr_auc

print(f"Baseline OOF PR-AUC:               {overall_oof_pr_auc:.4f}", flush=True)
print(f"Stress Test OOF PR-AUC (10% Nulls): {stress_pr_auc:.4f}", flush=True)
print(f"Degradation:                        -{degradation:.4f} ({-degradation*100:.2f}%)", flush=True)
print("ROBUSTNESS TEST — NOT hidden validation", flush=True)
