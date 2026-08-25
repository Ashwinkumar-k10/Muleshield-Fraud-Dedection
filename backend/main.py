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

@app.route("/api/auth/signup", methods=["POST", "OPTIONS"])
def auth_signup():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "ANALYST")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    from backend.database.connection import SessionLocal
    from backend.database.models import User
    
    db_session = SessionLocal()
    try:
        existing_user = db_session.query(User).filter(User.email == email).first()
        if existing_user:
            return jsonify({"error": "User with this Email/Employee ID already registered"}), 400
            
        new_user = User(email=email, password_hash=password_hash, role=role)
        db_session.add(new_user)
        db_session.commit()
        return jsonify({"message": "User registered successfully", "email": email, "role": role})
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def auth_login():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    from backend.database.connection import SessionLocal
    from backend.database.models import User
    from datetime import datetime
    
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter(User.email == email, User.password_hash == password_hash).first()
        if not user:
            return jsonify({"error": "Invalid Email/Employee ID or password"}), 401
            
        return jsonify({
            "message": "Authentication successful",
            "email": user.email,
            "role": user.role,
            "token": f"MS-SESSION-{user.id}-{int(datetime.utcnow().timestamp())}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

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

@app.route("/api/cases/<int:account_id>/status", methods=["POST", "OPTIONS"])
def update_case_status(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    data = request.json or {}
    new_status = data.get("status")
    analyst = data.get("analyst", "Analyst-10")
    if not new_status:
        return jsonify({"error": "Missing status parameter"}), 400
    
    updated_case = db.update_case_status(account_id, new_status, analyst)
    if not updated_case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(updated_case)

@app.route("/api/cases/<int:account_id>/notes", methods=["POST", "OPTIONS"])
def add_case_note(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    data = request.json or {}
    note_text = data.get("note")
    analyst = data.get("analyst", "Analyst-10")
    if not note_text:
        return jsonify({"error": "Missing note parameter"}), 400
    
    updated_case = db.add_case_note(account_id, note_text, analyst)
    if not updated_case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(updated_case)

@app.route("/api/cases/<int:account_id>/str-draft", methods=["POST", "OPTIONS"])
def create_str_draft(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    result = db.generate_str_report(account_id)
    if not result:
        return jsonify({"error": "Account case not found for STR generation"}), 404
    return jsonify(result)

@app.route("/api/cases/<int:account_id>/cbs-freeze", methods=["POST", "OPTIONS"])
def cbs_freeze(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
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

@app.route("/api/predict", methods=["POST", "OPTIONS"])
def predict_raw_account():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
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
