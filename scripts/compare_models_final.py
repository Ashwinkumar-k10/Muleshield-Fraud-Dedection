import sys
sys.path.append('.')
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.metrics import precision_recall_curve, auc, f1_score, precision_score, recall_score
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from imblearn.over_sampling import SMOTE
import joblib
import json

from modeling.preprocessor import MuleShieldPreprocessor

DATA_PATH = 'data_copy.csv'
TARGET_COL = 'F3924'

print("Loading raw CSV data...")
df_raw = pd.read_csv(DATA_PATH, engine='pyarrow')
if 'Unnamed: 0' in df_raw.columns:
    df_raw = df_raw.drop(columns=['Unnamed: 0'])

y_raw = df_raw[TARGET_COL]
X_raw = df_raw.drop(columns=[TARGET_COL])

print("Preprocessing dataset...")
preprocessor = MuleShieldPreprocessor()
X_processed = preprocessor.fit_transform(X_raw)

print("Clustering near-duplicates for group-aware split...")
X_norm = normalize(X_processed.fillna(0).values, norm='l2', axis=1)
sim_matrix = cosine_similarity(X_norm)
adj_matrix = csr_matrix(sim_matrix > 0.99)
n_components, groups = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)

pos_weight = (len(y_raw) - sum(y_raw)) / sum(y_raw)

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced', n_jobs=-1),
    'XGBoost': xgb.XGBClassifier(
        tree_method='hist',
        scale_pos_weight=pos_weight,
        max_depth=3,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        learning_rate=0.05,
        n_estimators=200,
        random_state=42
    )
}

def evaluate_models_group_cv(X_data, y_data, groups, n_splits=5, n_repeats=5):
    results = {m: {'pr_auc': [], 'f1': [], 'recall': [], 'precision': []} for m in models.keys()}
    
    fold_count = 1
    for repeat in range(n_repeats):
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42 + repeat)
        
        for train_idx, val_idx in cv.split(X_data, y_data, groups=groups):
            X_tr, y_tr = X_data.iloc[train_idx], y_data.iloc[train_idx]
            X_va, y_va = X_data.iloc[val_idx], y_data.iloc[val_idx]
            
            # SMOTE on train
            smote = SMOTE(random_state=42)
            X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
            
            # Scaler for LR
            scaler = StandardScaler()
            X_tr_scaled = scaler.fit_transform(X_tr_res)
            X_va_scaled = scaler.transform(X_va)
            X_tr_unscaled_tr = scaler.transform(X_tr) # for LR threshold tuning on un-SMOTEd train fold
            
            for name, model_inst in models.items():
                if name == 'Logistic Regression':
                    model_inst.fit(X_tr_scaled, y_tr_res)
                    y_prob_tr = model_inst.predict_proba(X_tr_unscaled_tr)[:, 1]
                    y_prob_va = model_inst.predict_proba(X_va_scaled)[:, 1]
                else:
                    model_inst.fit(X_tr_res, y_tr_res)
                    y_prob_tr = model_inst.predict_proba(X_tr)[:, 1]
                    y_prob_va = model_inst.predict_proba(X_va)[:, 1]
                    
                # Threshold tuning on train fold
                p_tr, r_tr, t_tr = precision_recall_curve(y_tr, y_prob_tr)
                f1_tr = 2 * r_tr * p_tr / (r_tr + p_tr + 1e-10)
                best_idx = np.argmax(f1_tr)
                best_thresh = t_tr[best_idx] if best_idx < len(t_tr) else 0.5
                
                # Val metrics
                p_va, r_va, t_va = precision_recall_curve(y_va, y_prob_va)
                pr_auc_va = auc(r_va, p_va)
                y_pred_va = (y_prob_va >= best_thresh).astype(int)
                
                results[name]['pr_auc'].append(pr_auc_va)
                results[name]['f1'].append(f1_score(y_va, y_pred_va))
                results[name]['recall'].append(recall_score(y_va, y_pred_va))
                results[name]['precision'].append(precision_score(y_va, y_pred_va, zero_division=0))
                
            if fold_count % 5 == 0:
                print(f"Completed {fold_count}/{n_splits*n_repeats} folds...")
            fold_count += 1
            
    summary = {}
    for m in results:
        summary[m] = {k: (np.mean(v), np.std(v)) for k, v in results[m].items()}
        
    return summary

print("Running 5x5 Group-Aware CV for LR, RF, and XGBoost...")
final_summary = evaluate_models_group_cv(X_processed, y_raw, groups)

print("\n" + "="*80)
print("3-MODEL COMPARISON TABLE (Group-Aware 5x5 CV):")
print(f"{'Model':<22} | {'PR-AUC (Mean ± Std)':<22} | {'F1 (Mean ± Std)':<22} | {'Recall (Mean ± Std)':<22} | {'Precision (Mean ± Std)'}")
print("-" * 115)

for m, metrics in final_summary.items():
    pr = f"{metrics['pr_auc'][0]:.4f} ± {metrics['pr_auc'][1]:.4f}"
    f1 = f"{metrics['f1'][0]:.4f} ± {metrics['f1'][1]:.4f}"
    rec = f"{metrics['recall'][0]:.4f} ± {metrics['recall'][1]:.4f}"
    prec = f"{metrics['precision'][0]:.4f} ± {metrics['precision'][1]:.4f}"
    print(f"{m:<22} | {pr:<22} | {f1:<22} | {rec:<22} | {prec}")

with open('model_comparison_results.json', 'w') as f:
    json.dump({m: {k: [float(v[0]), float(v[1])] for k, v in metrics.items()} for m, metrics in final_summary.items()}, f, indent=2)
