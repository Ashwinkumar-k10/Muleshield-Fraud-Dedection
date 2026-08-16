import os
import json
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
import sys

# Ensure modeling preprocessor module is accessible
sys.path.append('.')
from modeling.preprocessor import MuleShieldPreprocessor

def main():
    print("====================================================")
    print("      MULESHIELD AI — PRODUCTION INFERENCE SCRIPT   ")
    print("====================================================")

    # 1. Paths to Production Artifacts
    model_path = 'modeling/mule_shield_model.json'
    preprocessor_path = 'modeling/preprocessor.pkl'
    config_path = 'modeling/model_config.json'
    data_path = 'data_copy.csv'  # or 'DataSet.csv'

    # 2. Load Saved Production Artifacts
    print("\n[1/4] Loading production artifacts from modeling/...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    threshold = config.get('decision_threshold', 0.9934)
    print(f" -> Decision Threshold Loaded: {threshold:.4f}")

    preprocessor = joblib.load(preprocessor_path)
    print(" -> MuleShieldPreprocessor pipeline loaded successfully.")

    model = xgb.XGBClassifier()
    model.load_model(model_path)
    print(" -> XGBoost model (native JSON) loaded successfully.")

    # 3. Load Raw Account Data
    print(f"\n[2/4] Loading raw data from {data_path}...")
    raw_df = pd.read_csv(data_path, engine='pyarrow')
    if 'Unnamed: 0' in raw_df.columns:
        raw_df = raw_df.drop(columns=['Unnamed: 0'])
    print(f" -> Loaded {len(raw_df)} total rows.")

    # 4. Transform Data via Saved Preprocessor
    print("\n[3/4] Preprocessing & aligning features...")
    processed_df = preprocessor.transform(raw_df)
    print(f" -> Preprocessed matrix shape: {processed_df.shape}")

    # 5. Execute Model Predictions
    print("\n[4/4] Running XGBoost Inference...")
    probabilities = model.predict_proba(processed_df)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    # Assign Risk Tiers
    tiers = []
    actions = []
    for prob in probabilities:
        if prob <= 0.35:
            tiers.append("Low")
            actions.append("Routine monitoring")
        elif prob <= 0.59:
            tiers.append("Medium")
            actions.append("Enhanced monitoring")
        elif prob <= 0.79:
            tiers.append("High")
            actions.append("Analyst investigation")
        else:
            tiers.append("Critical")
            actions.append("Immediate freeze+STR")

    # Output Results Table
    results_df = pd.DataFrame({
        'Account_ID': raw_df.index,
        'Risk_Score': probabilities.round(4),
        'Risk_Tier': tiers,
        'Flagged_Mule': predictions,
        'Action': actions
    })

    print("\n====================================================")
    print("            PREDICTION RESULTS SUMMARY              ")
    print("====================================================")
    print(f"Total Accounts Evaluated:   {len(results_df)}")
    print(f"Critical Risk Mules (>=0.8): {sum(results_df['Risk_Tier'] == 'Critical')}")
    print(f"High Risk Cases (0.6-0.79):  {sum(results_df['Risk_Tier'] == 'High')}")
    print(f"Cleared Low Risk Accounts:   {sum(results_df['Risk_Tier'] == 'Low')}")

    print("\nSample Top 15 Flagged Accounts:")
    critical_sample = results_df.sort_values(by='Risk_Score', ascending=False).head(15)
    print(critical_sample.to_string(index=False))

    # Save outputs
    output_file = 'modeling/production_predictions.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\n[OK] Full predictions saved to: {output_file}")

if __name__ == '__main__':
    main()
