import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import precision_recall_curve, auc, f1_score, precision_score, recall_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from imblearn.over_sampling import SMOTE
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import json

TARGET_COL = 'F3924'

print("Loading processed data...")
df = pd.read_parquet('processed_data.parquet')

y = df[TARGET_COL]
X = df.drop(columns=[TARGET_COL])

missing_cols = [c for c in X.columns if c.endswith('_ismissing')]

# ---------------------------------------------------------
# 1. GROUP-AWARE DEDUPLICATION
# ---------------------------------------------------------
print("\n--- 1. GROUP-AWARE DEDUPLICATION ---")
# Normalize features
X_norm = normalize(X.fillna(0).values, norm='l2', axis=1)

# Compute full pairwise cosine similarity (9082 x 9082)
print("Computing pairwise cosine similarity...")
sim_matrix = cosine_similarity(X_norm)

# Create adjacency matrix for sim > 0.99
# We don't include self edges implicitly by >0.99 since they are 1.0
adj_matrix = csr_matrix(sim_matrix > 0.99)

# Find connected components to form groups
n_components, labels = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)
groups = labels

print(f"Total distinct groups (clusters): {n_components}")

# Real unique fraud cases
pos_groups = np.unique(groups[y == 1])
print(f"Raw positive rows: {sum(y == 1)}")
print(f"Distinct positive-class clusters: {len(pos_groups)}")


# ---------------------------------------------------------
# 2 & 3. GROUP-AWARE 5x5 REPEATED STRATIFIED CV
# ---------------------------------------------------------
print("\n--- 2 & 3. GROUP-AWARE REPEATED CV ABLATION TEST ---")

def run_group_cv(X_data, y_data, groups, n_splits=5, n_repeats=5):
    metrics = {'pr_auc': [], 'f1': [], 'recall': [], 'precision': []}
    
    pos_weight = (len(y_data) - sum(y_data)) / sum(y_data)
    
    fold_count = 1
    for repeat in range(n_repeats):
        # We use StratifiedGroupKFold with shuffle to get different splits per repeat
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42 + repeat)
        
        for train_idx, val_idx in cv.split(X_data, y_data, groups=groups):
            X_tr, y_tr = X_data.iloc[train_idx], y_data.iloc[train_idx]
            X_va, y_va = X_data.iloc[val_idx], y_data.iloc[val_idx]
            
            # SMOTE on train (ignoring groups inside SMOTE generation is fine, 
            # since the leak risk is between train and val, which is now protected by GroupKFold)
            smote = SMOTE(random_state=42)
            X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
            
            model = xgb.XGBClassifier(
                tree_method='hist', 
                # device='cuda',
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
            
            # Tune threshold on TRAIN set to prevent leakage
            y_prob_tr = model.predict_proba(X_tr)[:, 1]
            p_tr, r_tr, t_tr = precision_recall_curve(y_tr, y_prob_tr)
            f1_scores_tr = 2 * r_tr * p_tr / (r_tr + p_tr + 1e-10)
            best_idx = np.argmax(f1_scores_tr)
            best_thresh = t_tr[best_idx] if best_idx < len(t_tr) else 0.5
            
            # Predict on VAL set
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

print("Running Group-Aware CV WITH all features...")
res_with = run_group_cv(X, y, groups)

print("\nRunning Group-Aware CV WITHOUT missingness indicators...")
X_no_missing = X.drop(columns=missing_cols)
res_without = run_group_cv(X_no_missing, y, groups)

print("\n=== GROUP-AWARE RESULTS ===")
print("WITH Missingness Indicators:")
for k, (mean, std) in res_with.items():
    print(f"  {k}: {mean:.4f} ± {std:.4f}")

print("\nWITHOUT Missingness Indicators:")
for k, (mean, std) in res_without.items():
    print(f"  {k}: {mean:.4f} ± {std:.4f}")

# Save to json for reporting
with open('group_ablation_results.json', 'w') as f:
    json.dump({
        'groups': {
            'total_groups': int(n_components),
            'raw_pos': int(sum(y == 1)),
            'distinct_pos': int(len(pos_groups))
        },
        'with_missing': res_with,
        'without_missing': res_without
    }, f)

print("Group-Aware ablation analysis complete.")
