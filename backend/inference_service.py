from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import xgboost as xgb
import sys
import os

sys.path.append('.')
from backend.risk_engine import MuleShieldRiskEngine

app = Flask(__name__)
CORS(app)

risk_engine = None
load_error = None

try:
    risk_engine = MuleShieldRiskEngine()
except Exception as e:
    load_error = str(e)
    print(f"Error loading model artifacts: {e}")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP"}), 200

@app.route("/ready", methods=["GET"])
def ready():
    if risk_engine is not None and load_error is None:
        return jsonify({"status": "READY"}), 200
    else:
        return jsonify({"status": "NOT_READY", "error": load_error or "Inference engine not initialized"}), 503

@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    if risk_engine is None:
        return jsonify({"error": "Inference engine is not ready", "detail": load_error}), 503

    data = request.json or {}
    account_features = data.get("account_features")
    
    if not account_features:
        return jsonify({"error": "Missing 'account_features' payload"}), 400

    try:
        raw_df = pd.DataFrame([account_features])
        
        # Transform features
        processed_df = risk_engine.preprocessor.transform(raw_df)
        
        # Predict probability
        prob = float(risk_engine.model.predict_proba(processed_df)[0, 1])
        tier, action = risk_engine.get_tier_action(prob)
        
        # Explanations
        explanation = None
        if data.get("explain", False) or True: # Return explanations by default
            booster = risk_engine.model.get_booster()
            dmat = xgb.DMatrix(processed_df)
            contribs = booster.predict(dmat, pred_contribs=True)
            
            contrib_dict = dict(zip(processed_df.columns, contribs[0][:-1]))
            sorted_contribs = sorted(contrib_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            explanation = [
                {"feature": k, "contribution": float(v)} 
                for k, v in sorted_contribs[:3]
            ]

        return jsonify({
            "risk_score": round(prob, 4),
            "tier": tier,
            "action": action,
            "exceeds_threshold": prob >= risk_engine.decision_threshold,
            "explanation": explanation
        }), 200
    except Exception as e:
        return jsonify({"error": "Inference calculation failed", "detail": str(e)}), 500

if __name__ == "__main__":
    print("Starting Dedicated ML Inference Service on http://localhost:8080 ...")
    app.run(host="0.0.0.0", port=8080, threaded=True)
