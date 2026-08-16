import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_recall_curve, auc, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import json

TARGET_COL = 'F3924'

print("Loading data...")
df = pd.read_parquet('processed_data.parquet')
y = df[TARGET_COL]
X = df.drop(columns=[TARGET_COL])

print("\n--- 1 & 2. DROPPING LEAKY FEATURES (F2230 & F3888) ---")
# Drop all month columns (F2230) and date columns (F3888)
leaky_cols = [c for c in X.columns if c.startswith('F2230_') or c.startswith('F3888_')]
print(f"Dropping {len(leaky_cols)} columns encoding dates/months.")
X = X.drop(columns=leaky_cols)

# We should also check for missingness cols of these if any?
# They weren't missingness imputed since they are categoricals.

print("\n--- 3. RE-RUN SEPARABILITY SCAN ---")
while True:
    dt = DecisionTreeClassifier(max_depth=1, random_state=42)
    dt.fit(X, y)
    preds = dt.predict(X)
    f1 = f1_score(y, preds)
    feature_idx = dt.tree_.feature[0]
    
    if feature_idx == -2: # leaf node
        break
        
    feature_name = X.columns[feature_idx]
    threshold = dt.tree_.threshold[0]
    
    print(f"Best remaining single feature: {feature_name} at thresh {threshold:.4f} | F1: {f1:.4f}")
    
    # If F1 is suspiciously high (e.g. > 0.8), it's another leak. 
    # Even > 0.5 is huge for a single feature on an imbalanced dataset.
    if f1 > 0.8:
        print(f"-> Feature {feature_name} is highly suspicious (F1={f1:.4f}). Dropping...")
        # Check if it's a dummy var group
        base_feature = feature_name.split('_')[0]
        if base_feature in df.columns or any(c.startswith(base_feature + '_') for c in X.columns):
             cols_to_drop = [c for c in X.columns if c.startswith(base_feature + '_') or c == base_feature]
             print(f"   Dropping related columns: {cols_to_drop}")
             X = X.drop(columns=cols_to_drop)
        else:
             X = X.drop(columns=[feature_name])
    else:
        print("-> No more perfect single-feature separators found.")
        break

print("\nChecking Depth-2 combos...")
dt2 = DecisionTreeClassifier(max_depth=2, random_state=42)
dt2.fit(X, y)
preds2 = dt2.predict(X)
f1_2 = f1_score(y, preds2)
print(f"Depth-2 Tree F1: {f1_2:.4f}")
imps = dt2.feature_importances_
top_idx = np.argsort(imps)[::-1][:3]
print(f"Top features from depth 2 tree: {[X.columns[i] for i in top_idx]}")

if f1_2 > 0.9:
    print("Warning: Depth 2 still too high. There might be a combo leak.")
    for i in top_idx:
        base_feature = X.columns[i].split('_')[0]
        cols_to_drop = [c for c in X.columns if c.startswith(base_feature + '_') or c == base_feature]
        X = X.drop(columns=cols_to_drop)
        print(f"Dropped {cols_to_drop} due to depth-2 leak.")
        
# ---------------------------------------------------------
# 4. GROUP-AWARE CV ON CLEANED DATA
# ---------------------------------------------------------
print("\n--- 4. GROUP-AWARE CV (CLEAN DATA) ---")
print("Re-computing cosine similarity on cleaned data to form groups...")
X_norm = normalize(X.fillna(0).values, norm='l2', axis=1)
sim_matrix = cosine_similarity(X_norm)
adj_matrix = csr_matrix(sim_matrix > 0.99)
n_components, groups = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)
print(f"Total distinct groups: {n_components}")

def run_group_cv_clean(X_data, y_data, groups, n_splits=5, n_repeats=5):
    metrics = {'pr_auc': [], 'f1': [], 'recall': [], 'precision': []}
    pos_weight = (len(y_data) - sum(y_data)) / sum(y_data)
    fold_count = 1
    
    for repeat in range(n_repeats):
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42 + repeat)
        for train_idx, val_idx in cv.split(X_data, y_data, groups=groups):
            X_tr, y_tr = X_data.iloc[train_idx], y_data.iloc[train_idx]
            X_va, y_va = X_data.iloc[val_idx], y_data.iloc[val_idx]
            
            smote = SMOTE(random_state=42)
            X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
            
            model = xgb.XGBClassifier(
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
            model.fit(X_tr_res, y_tr_res)
            
            # TUNE ON TRAIN
            y_prob_tr = model.predict_proba(X_tr)[:, 1]
            p_tr, r_tr, t_tr = precision_recall_curve(y_tr, y_prob_tr)
            f1_scores_tr = 2 * r_tr * p_tr / (r_tr + p_tr + 1e-10)
            best_idx = np.argmax(f1_scores_tr)
            best_thresh = t_tr[best_idx] if best_idx < len(t_tr) else 0.5
            
            # PREDICT ON VAL
            y_prob = model.predict_proba(X_va)[:, 1]
            p, r, t = precision_recall_curve(y_va, y_prob)
            pr_auc = auc(r, p)
            y_pred = (y_prob >= best_thresh).astype(int)
            
            metrics['pr_auc'].append(pr_auc)
            metrics['f1'].append(f1_score(y_va, y_pred))
            metrics['recall'].append(recall_score(y_va, y_pred))
            metrics['precision'].append(precision_score(y_va, y_pred, zero_division=0))
            
            if fold_count % 5 == 0:
                print(f"Completed {fold_count}/{n_splits*n_repeats} folds...")
            fold_count += 1
            
    return {k: (np.mean(v), np.std(v)) for k, v in metrics.items()}

print("Running 5x5 Group-Aware CV on clean dataset (no date/month leakage)...")
res_clean = run_group_cv_clean(X, y, groups)

print("\n=== FINAL CORRECTED METRICS ===")
for k, (mean, std) in res_clean.items():
    print(f"  {k}: {mean:.4f} ± {std:.4f}")

with open('final_clean_results.json', 'w') as f:
    json.dump({'clean_metrics': res_clean}, f)
