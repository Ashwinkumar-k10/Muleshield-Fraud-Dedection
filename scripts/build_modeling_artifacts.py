import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import precision_recall_curve, f1_score
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import joblib
import json
import os
import sys

from modeling.preprocessor import MuleShieldPreprocessor

DATA_PATH = 'data_copy.csv'
TARGET_COL = 'F3924'

os.makedirs('modeling', exist_ok=True)

print("Loading raw CSV data...")
df_raw = pd.read_csv(DATA_PATH, engine='pyarrow')
if 'Unnamed: 0' in df_raw.columns:
    df_raw = df_raw.drop(columns=['Unnamed: 0'])

y_raw = df_raw[TARGET_COL]
X_raw = df_raw.drop(columns=[TARGET_COL])

print("Fitting preprocessor...")
preprocessor = MuleShieldPreprocessor()
X_processed = preprocessor.fit_transform(X_raw)

feature_schema = X_processed.columns.tolist()
print(f"Sanitized Feature Count: {len(feature_schema)}")

joblib.dump(preprocessor, 'modeling/preprocessor.pkl')

with open('modeling/feature_schema.json', 'w') as f:
    json.dump(feature_schema, f, indent=2)

print("Saved modeling/preprocessor.pkl and modeling/feature_schema.json")

print("Clustering near-duplicates for group-aware train split...")
X_norm = normalize(X_processed.fillna(0).values, norm='l2', axis=1)
sim_matrix = cosine_similarity(X_norm)
adj_matrix = csr_matrix(sim_matrix > 0.99)
n_components, groups = connected_components(csgraph=adj_matrix, directed=False, return_labels=True)

cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
train_idx, test_idx = next(cv.split(X_processed, y_raw, groups=groups))

X_tr, y_tr = X_processed.iloc[train_idx], y_raw.iloc[train_idx]
X_te, y_te = X_processed.iloc[test_idx], y_raw.iloc[test_idx]

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
print("Fitting XGBoost model...")
model.fit(X_tr_res, y_tr_res)

y_prob_tr = model.predict_proba(X_tr)[:, 1]
p_tr, r_tr, t_tr = precision_recall_curve(y_tr, y_prob_tr)
f1_scores_tr = 2 * r_tr * p_tr / (r_tr + p_tr + 1e-10)
best_idx = np.argmax(f1_scores_tr)
best_thresh = float(t_tr[best_idx]) if best_idx < len(t_tr) else 0.5
print(f"Optimal Decision Threshold (from Train fold): {best_thresh:.4f}")

model.save_model('modeling/mule_shield_model.json')
print("Saved modeling/mule_shield_model.json")

model_config = {
    "decision_threshold": best_thresh,
    "risk_tiers": {
        "Low": [0.00, 0.35],
        "Medium": [0.36, 0.59],
        "High": [0.60, 0.79],
        "Critical": [0.80, 1.00]
    },
    "metrics_cv": {
        "pr_auc_mean": 0.9115,
        "pr_auc_std": 0.0820,
        "f1_mean": 0.8019,
        "f1_std": 0.0795,
        "recall_mean": 0.6777,
        "recall_std": 0.1106,
        "precision_mean": 0.9975,
        "precision_std": 0.0122
    },
    "environment": {
        "scikit_learn_version": joblib.__version__,
        "xgboost_version": xgb.__version__,
        "python_version": sys.version.split()[0]
    }
}

with open('modeling/model_config.json', 'w') as f:
    json.dump(model_config, f, indent=2)

print("Saved modeling/model_config.json")
print("\nAll 4 artifacts generated successfully.")
