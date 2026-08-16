import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import precision_recall_curve, auc, f1_score, precision_score, recall_score
from sklearn.metrics.pairwise import cosine_similarity
from imblearn.over_sampling import SMOTE
import json

TARGET_COL = 'F3924'

print("Loading processed data...")
df = pd.read_parquet('processed_data.parquet')

y = df[TARGET_COL]
X = df.drop(columns=[TARGET_COL])

# Identify missingness columns
missing_cols = [c for c in X.columns if c.endswith('_ismissing')]

# ---------------------------------------------------------
# 2. INVESTIGATE WHY MISSINGNESS IS PREDICTIVE
# ---------------------------------------------------------
print("\n--- 2. MISSINGNESS INVESTIGATION ---")
# Total missingness count per row
row_missing_count = X[missing_cols].sum(axis=1)

# Correlation with target
corr = np.corrcoef(row_missing_count, y)[0, 1]
print(f"Correlation between row total missingness count and target: {corr:.4f}")

# Mean missingness % for positive vs negative
mean_miss_pos = row_missing_count[y == 1].mean() / len(missing_cols)
mean_miss_neg = row_missing_count[y == 0].mean() / len(missing_cols)
print(f"Mean missingness % for Positive rows (Mule): {mean_miss_pos:.2%}")
print(f"Mean missingness % for Negative rows (Clean): {mean_miss_neg:.2%}")


# ---------------------------------------------------------
# 4. CHECK FOR NEAR-DUPLICATE ROWS
# ---------------------------------------------------------
print("\n--- 4. DUPLICATE ROW CHECK ---")
exact_dupes = X.duplicated().sum()
print(f"Exact duplicate rows in dataset (excluding target): {exact_dupes}")

# For cosine similarity, doing all pairs on 11k features might OOM. 
# Let's sample or use PCA if it's too big, but 9k x 11k float32 is ~400MB.
# Pairwise similarity matrix is 9k x 9k float32 = 324MB. Fits in memory!
# We'll normalize X first to make it faster
from sklearn.preprocessing import normalize
X_norm = normalize(X.fillna(0).values, norm='l2', axis=1)
# Compute max similarity to any other row (ignoring self)
# We can do this in chunks to avoid large memory spikes
max_sims = []
chunk_size = 1000
for i in range(0, X_norm.shape[0], chunk_size):
    chunk = X_norm[i:i+chunk_size]
    sim = cosine_similarity(chunk, X_norm)
    # Set self-similarity to 0
    for j in range(sim.shape[0]):
        sim[j, i+j] = 0.0
    max_sims.append(sim.max(axis=1))
max_sims = np.concatenate(max_sims)
near_dupes = (max_sims > 0.99).sum()
print(f"Rows with cosine similarity > 0.99 to another row: {near_dupes}")


# ---------------------------------------------------------
# 1 & 3. 5x5 REPEATED K-FOLD CV (WITH AND WITHOUT MISSINGNESS)
# ---------------------------------------------------------
print("\n--- 1 & 3. REPEATED CV ABLATION TEST ---")

def run_cv(X_data, y_data, n_splits=5, n_repeats=5):
    rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=42)
    metrics = {'pr_auc': [], 'f1': [], 'recall': [], 'precision': []}
    
    pos_weight = (len(y_data) - sum(y_data)) / sum(y_data)
    
    fold = 1
    for train_idx, val_idx in rskf.split(X_data, y_data):
        X_tr, y_tr = X_data.iloc[train_idx], y_data.iloc[train_idx]
        X_va, y_va = X_data.iloc[val_idx], y_data.iloc[val_idx]
        
        # SMOTE on train
        smote = SMOTE(random_state=42)
        X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
        
        model = xgb.XGBClassifier(
            tree_method='hist', 
            device='cuda',
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
        
        y_prob = model.predict_proba(X_va)[:, 1]
        p, r, t = precision_recall_curve(y_va, y_prob)
        pr_auc = auc(r, p)
        
        # Max F1 threshold tuning
        f1_scores = 2 * r * p / (r + p + 1e-10)
        best_idx = np.argmax(f1_scores)
        best_thresh = t[best_idx] if best_idx < len(t) else 0.5
        
        y_pred = (y_prob >= best_thresh).astype(int)
        metrics['pr_auc'].append(pr_auc)
        metrics['f1'].append(f1_score(y_va, y_pred))
        metrics['recall'].append(recall_score(y_va, y_pred))
        metrics['precision'].append(precision_score(y_va, y_pred, zero_division=0))
        
        if fold % 5 == 0:
            print(f"Completed {fold}/{n_splits*n_repeats} folds...")
        fold += 1
        
    return {k: (np.mean(v), np.std(v)) for k, v in metrics.items()}

print("Running CV WITH all features...")
res_with = run_cv(X, y)

print("\nRunning CV WITHOUT missingness indicators...")
X_no_missing = X.drop(columns=missing_cols)
res_without = run_cv(X_no_missing, y)

print("\n=== RESULTS ===")
print("WITH Missingness Indicators:")
for k, (mean, std) in res_with.items():
    print(f"  {k}: {mean:.4f} ± {std:.4f}")

print("\nWITHOUT Missingness Indicators:")
for k, (mean, std) in res_without.items():
    print(f"  {k}: {mean:.4f} ± {std:.4f}")

# Save to json for reporting
with open('ablation_results.json', 'w') as f:
    json.dump({
        'missingness': {
            'corr': float(corr),
            'pos_pct': float(mean_miss_pos),
            'neg_pct': float(mean_miss_neg)
        },
        'dupes': {
            'exact': int(exact_dupes),
            'near': int(near_dupes)
        },
        'with_missing': res_with,
        'without_missing': res_without
    }, f)

print("Ablation analysis complete.")
