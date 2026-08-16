from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

sys.path.append('.')
from backend.db import db
from backend.risk_engine import risk_engine

app = Flask(__name__)
CORS(app)

from flask import send_from_directory

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.route("/", methods=["GET"])
def read_root():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/cases", methods=["GET"])
def get_all_cases():
    res = db.get_all_cases()
    return jsonify({"summary": res["summary"], "total": len(res["cases"]), "cases": res["cases"]})

@app.route("/api/cases/<int:account_id>", methods=["GET"])
def get_case_by_id(account_id: int):
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Account case not found"}), 404
    return jsonify(case)

@app.route("/api/cases/<int:account_id>/str-draft", methods=["POST"])
def create_str_draft(account_id: int):
    result = db.generate_str_report(account_id)
    if not result:
        return jsonify({"error": "Account case not found for STR generation"}), 404
    return jsonify(result)

@app.route("/api/sample-mule-payload", methods=["GET"])
def get_sample_mule_payload():
    return jsonify(db.get_sample_mule_payload())

@app.route("/api/predict", methods=["POST"])
def predict_raw_account():
    import pandas as pd
    data = request.json or {}
    raw_df = pd.DataFrame([data.get("account_features", {})])
    result = risk_engine.predict_raw_row(raw_df)
    return jsonify(result)

if __name__ == "__main__":
    print("Starting MuleShield Backend API on http://localhost:8000 ...")
    app.run(host="0.0.0.0", port=8000, debug=False)
