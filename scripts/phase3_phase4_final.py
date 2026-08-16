import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedGroupKFold
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import shap
import json
import joblib

FLAGGED_FEATURES = ['F115', 'F321', 'F527', 'F531', 'F670', 'F1692', 'F2082', 'F2122', 'F2582', 'F2678', 'F2737', 'F2956', 'F3043', 'F3836', 'F3887', 'F3889', 'F3891', 'F3894']

print("Loading data...")
df = pd.read_parquet('processed_data.parquet')
y = df['F3924']
X = df.drop(columns=['F3924'])

# Drop leaked columns (F2230, F3888, and empty string column)
leaky_cols = [c for c in X.columns if c.startswith('F2230_') or c.startswith('F3888_') or c == '']
X_clean = X.drop(columns=leaky_cols)
print(f"Cleaned feature matrix shape: {X_clean.shape}")

# Save clean X and y for dashboard
X_clean.to_parquet('X_clean.parquet')

# Group clustering for group-aware split
X_norm = normalize(X_clean.fillna(0).values, norm='l2', axis=1)
sim_matrix = cosine_similarity(X_norm)
adj_matrix = csr_matrix(sim_matrix > 0.99)
n_components, groups = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)

# Split into Train and Test using StratifiedGroupKFold
cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
train_idx, test_idx = next(cv.split(X_clean, y, groups=groups))

X_tr, y_tr = X_clean.iloc[train_idx], y.iloc[train_idx]
X_te, y_te = X_clean.iloc[test_idx], y.iloc[test_idx]

# Save test set for dashboard & scoring
X_te.to_parquet('X_test_clean.parquet')
pd.DataFrame(y_te).to_parquet('y_test_clean.parquet')

print(f"Train shape: {X_tr.shape}, Test shape: {X_te.shape}")

# Train full model on train set with SMOTE
smote = SMOTE(random_state=42)
X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)

pos_weight = (len(y_tr) - sum(y_tr)) / sum(y_tr)
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

# Save final clean model
model.save_model('clean_model.xgb')

# --- PHASE 3: SHAP EXPLAINABILITY ---
print("\n--- PHASE 3: SHAP EXPLAINABILITY ---")
# Compute SHAP values using XGBoost Booster pred_contribs
dtest = xgb.DMatrix(X_te)
shap_matrix = model.get_booster().predict(dtest, pred_contribs=True)
shap_values = shap_matrix[:, :-1] # Exclude bias column

# Save SHAP values
np.save('shap_values_clean.npy', shap_values)

mean_abs_shap = np.abs(shap_values).mean(axis=0)
top10_idx = np.argsort(mean_abs_shap)[::-1][:10]
top10_features = X_te.columns[top10_idx].tolist()

print("Top 10 Global SHAP Features:")
for i, f in enumerate(top10_features):
    print(f"  {i+1}. {f} (Impact: {mean_abs_shap[top10_idx[i]]:.4f})")

# Check overlap with organiser's 18 flagged features
overlap_count = 0
overlap_list = []
for tf in top10_features:
    base = tf.split('_')[0]
    if base in FLAGGED_FEATURES:
        overlap_count += 1
        overlap_list.append(tf)

print(f"\nSHAP vs. Organiser Flagged Features Overlap: {overlap_count}/10")
print(f"Overlapping features: {overlap_list}")

# --- PHASE 4: RISK SCORING TABLE ---
print("\n--- PHASE 4: RISK SCORING TABLE ---")
probs = model.predict_proba(X_te)[:, 1]

def get_tier_action(prob):
    if prob <= 0.35:
        return "Low", "Routine monitoring"
    elif prob <= 0.59:
        return "Medium", "Enhanced monitoring"
    elif prob <= 0.79:
        return "High", "Analyst investigation"
    else:
        return "Critical", "Immediate freeze+STR"

# Pick 10 sample test instances (5 positives if available, 5 negatives)
pos_indices = np.where(y_te == 1)[0]
neg_indices = np.where(y_te == 0)[0]

sample_pos = pos_indices[:5] if len(pos_indices) >= 5 else pos_indices
sample_neg = neg_indices[:(10 - len(sample_pos))]
sample_indices = np.concatenate([sample_pos, sample_neg])

results_table = []
print(f"{'Acc Index':<10} | {'Score':<6} | {'Tier':<8} | {'Top 3 SHAP Drivers':<45} | {'Recommended Action'}")
print("-" * 110)

for idx in sample_indices:
    acc_id = X_te.index[idx]
    p = probs[idx]
    tier, action = get_tier_action(p)
    
    sv = shap_values[idx]
    top3_idx = np.argsort(np.abs(sv))[::-1][:3]
    top3_feats = X_te.columns[top3_idx].tolist()
    
    feats_str = ", ".join(top3_feats)
    print(f"{acc_id:<10} | {p:.4f} | {tier:<8} | {feats_str:<45} | {action}")
    
    results_table.append({
        'account_index': int(acc_id),
        'score': float(p),
        'tier': tier,
        'top_features': top3_feats,
        'action': action
    })

with open('risk_scoring_clean.json', 'w') as f:
    json.dump({
        'overlap_count': int(overlap_count),
        'overlap_list': overlap_list,
        'top10_features': top10_features,
        'scoring_table': results_table
    }, f)

print("\nPhase 3 & Phase 4 processing completed successfully.")
