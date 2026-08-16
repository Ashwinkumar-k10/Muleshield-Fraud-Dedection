import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import json
import os

import sys
sys.path.append('.')

from modeling.preprocessor import MuleShieldPreprocessor

print("--- VERIFYING MODELING ARTIFACTS ---")

preprocessor_path = 'modeling/preprocessor.pkl'
assert os.path.exists(preprocessor_path), f"Missing {preprocessor_path}"
preprocessor = joblib.load(preprocessor_path)
print("[OK] Preprocessor loaded successfully.")

schema_path = 'modeling/feature_schema.json'
assert os.path.exists(schema_path), f"Missing {schema_path}"
with open(schema_path, 'r') as f:
    feature_schema = json.load(f)
print(f"[OK] Feature schema loaded successfully ({len(feature_schema)} features).")

config_path = 'modeling/model_config.json'
assert os.path.exists(config_path), f"Missing {config_path}"
with open(config_path, 'r') as f:
    config = json.load(f)
threshold = config['decision_threshold']
print(f"[OK] Model config loaded successfully (Decision Threshold: {threshold:.4f}).")

model_path = 'modeling/mule_shield_model.json'
assert os.path.exists(model_path), f"Missing {model_path}"
model = xgb.XGBClassifier()
model.load_model(model_path)
print("[OK] XGBoost model loaded successfully.")

raw_df = pd.read_csv('data_copy.csv', engine='pyarrow')
raw_sample_row = raw_df.iloc[[9003]]

processed_row = preprocessor.transform(raw_sample_row)

assert list(processed_row.columns) == feature_schema, "Processed columns do not match feature schema!"
print("[OK] Preprocessor transformation aligns exactly with feature schema.")

prob = float(model.predict_proba(processed_row)[0, 1])

def get_tier_action(prob):
    if prob <= 0.35:
        return "Low", "Routine monitoring"
    elif prob <= 0.59:
        return "Medium", "Enhanced monitoring"
    elif prob <= 0.79:
        return "High", "Analyst investigation"
    else:
        return "Critical", "Immediate freeze+STR"

tier, action = get_tier_action(prob)

print("\n--- INFERENCE VERIFICATION TEST RESULT ---")
print(f"Sample Account Index: 9003")
print(f"Raw Input Shape: {raw_sample_row.shape}")
print(f"Processed Input Shape: {processed_row.shape}")
print(f"Predicted Risk Score: {prob:.4f}")
print(f"Decision Threshold: {threshold:.4f}")
print(f"Assigned Tier: {tier}")
print(f"Recommended Action: {action}")

assert prob > threshold, "Expected positive account 9003 to exceed threshold!"
assert tier == "Critical", "Expected positive account 9003 to be Critical!"

print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY! Artifacts are ready for backend integration.")
