import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import json
import os
import sys

# Ensure root is in path to import modeling preprocessor
sys.path.append('.')
from modeling.preprocessor import MuleShieldPreprocessor

class MuleShieldRiskEngine:
    def __init__(self, modeling_dir='modeling'):
        self.model_path = os.path.join(modeling_dir, 'mule_shield_model.json')
        self.schema_path = os.path.join(modeling_dir, 'feature_schema.json')
        self.preprocessor_path = os.path.join(modeling_dir, 'preprocessor.pkl')
        self.config_path = os.path.join(modeling_dir, 'model_config.json')

        print("Loading MuleShield Risk Engine artifacts...")
        self.preprocessor = joblib.load(self.preprocessor_path)
        with open(self.schema_path, 'r') as f:
            self.feature_schema = json.load(f)
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.model = xgb.XGBClassifier()
        self.model.load_model(self.model_path)
        self.decision_threshold = self.config.get('decision_threshold', 0.9934)
        print(f"Risk Engine initialized successfully. Decision threshold: {self.decision_threshold:.4f}")

    def get_tier_action(self, prob: float):
        if prob <= 0.35:
            return "Low", "Routine monitoring"
        elif prob <= 0.59:
            return "Medium", "Enhanced monitoring"
        elif prob <= 0.79:
            return "High", "Analyst investigation"
        else:
            return "Critical", "Immediate freeze+STR"

    def predict_raw_row(self, raw_row_df: pd.DataFrame):
        processed_df = self.preprocessor.transform(raw_row_df)
        prob = float(self.model.predict_proba(processed_df)[0, 1])
        tier, action = self.get_tier_action(prob)
        return {
            "risk_score": round(prob, 4),
            "tier": tier,
            "action": action,
            "exceeds_threshold": prob >= self.decision_threshold
        }

risk_engine = MuleShieldRiskEngine()
