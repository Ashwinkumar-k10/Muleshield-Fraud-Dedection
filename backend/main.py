from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import sys
import os
import io
import json
import numpy as np

sys.path.append('.')
from backend.db import db
from backend.risk_engine import risk_engine
from backend.report_generator import generate_pdf_report

app = Flask(__name__)
CORS(app)

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

@app.route("/api/cases/<int:account_id>/status", methods=["POST"])
def update_case_status(account_id: int):
    data = request.json or {}
    new_status = data.get("status")
    analyst = data.get("analyst", "Analyst-10")
    if not new_status:
        return jsonify({"error": "Missing status parameter"}), 400
    
    updated_case = db.update_case_status(account_id, new_status, analyst)
    if not updated_case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(updated_case)

@app.route("/api/cases/<int:account_id>/notes", methods=["POST"])
def add_case_note(account_id: int):
    data = request.json or {}
    note_text = data.get("note")
    analyst = data.get("analyst", "Analyst-10")
    if not note_text:
        return jsonify({"error": "Missing note parameter"}), 400
    
    updated_case = db.add_case_note(account_id, note_text, analyst)
    if not updated_case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(updated_case)

@app.route("/api/cases/<int:account_id>/str-draft", methods=["POST"])
def create_str_draft(account_id: int):
    result = db.generate_str_report(account_id)
    if not result:
        return jsonify({"error": "Account case not found for STR generation"}), 404
    return jsonify(result)

@app.route("/api/cases/<int:account_id>/cbs-freeze", methods=["POST"])
def cbs_freeze(account_id: int):
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    data = request.json or {}
    analyst = data.get("analyst", "Analyst-10")
    ref_no = f"CBS-FRZ-2026-{account_id}-{np.random.randint(1000, 9999)}"
    
    # Update status to ESCALATED
    db.update_case_status(account_id, "ESCALATED", analyst)
    db.add_case_note(account_id, f"CBS Emergency Debit Freeze Confirmed. Reference: {ref_no}.", "System")
    db.log_audit_event("CBS Debit Freeze Simulation", account_id, f"FREEZE LOCKED ({ref_no})", analyst)
    
    # Reload case with updated entries
    updated_case = db.get_case(account_id)
    return jsonify({"success": True, "ref_no": ref_no, "case": updated_case})

@app.route("/api/cases/<int:account_id>/download-json", methods=["GET"])
def download_json(account_id: int):
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    db.log_audit_event("Download JSON Data", account_id, "SUCCESS")
    return send_file(
        io.BytesIO(json.dumps(case, indent=2).encode('utf-8')),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"MuleShield_Case_{account_id}.json"
    )

@app.route("/api/cases/<int:account_id>/download-pdf", methods=["GET"])
def download_pdf(account_id: int):
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    pdf_bytes = generate_pdf_report(case)
    db.log_audit_event("Download PDF Report", account_id, "SUCCESS")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"MuleShield_Report_{account_id}.pdf"
    )

@app.route("/api/sample-mule-payload", methods=["GET"])
def get_sample_mule_payload():
    return jsonify(db.get_sample_mule_payload())

@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    return jsonify({"audit_logs": db.audit_logs})

@app.route("/api/predict", methods=["POST"])
def predict_raw_account():
    import pandas as pd
    data = request.json or {}
    raw_df = pd.DataFrame([data.get("account_features", {})])
    result = risk_engine.predict_raw_row(raw_df)
    db.log_audit_event("Account Evaluation Ingestion", "N/A", f"RISK: {result['risk_score']:.4f} ({result['tier']})")
    return jsonify(result)

@app.route("/api/model/metadata", methods=["GET"])
def get_model_metadata():
    return jsonify({
        "model_name": "XGBoost Classifier",
        "model_version": "v1.0.0-PRO",
        "threshold": 0.9899,
        "pr_auc": 0.8807,
        "pr_auc_std": 0.0403,
        "precision": 1.0000,
        "recall": 0.6164,
        "f1": 0.7586,
        "stress_pr_auc": 0.8383,
        "evaluation_method": "Stratified 5-Fold Group-Aware Cross-Validation",
        "total_evaluated": 9082,
        "similarity_clusters": 6118,
        "near_duplicate_profiles": 3112,
        "purged_features_count": 14
    })

if __name__ == "__main__":
    print("Starting MuleShield Backend API on http://localhost:8000 ...")
    app.run(host="0.0.0.0", port=8000, debug=False)
