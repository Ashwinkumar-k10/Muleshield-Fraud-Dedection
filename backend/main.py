from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import sys
import os
import io
import json
import time
import functools
import base64
import hmac
import hashlib
from datetime import datetime
import numpy as np

sys.path.append('.')
from backend.db import db
from backend.risk_engine import risk_engine
from backend.report_generator import generate_pdf_report

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Environment-backed secret key
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "muleshield-secure-secret-2026-xyz").encode()

# JWT Token Helpers
def create_token(email, role):
    # Expire in 2 hours (7200 seconds)
    exp = int(time.time()) + 7200
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"email": email, "role": role, "exp": exp}
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature = hmac.new(JWT_SECRET_KEY, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).hexdigest()
    return f"{header_b64}.{payload_b64}.{signature}"

def decode_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature = parts
        
        expected_sig = hmac.new(JWT_SECRET_KEY, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
            
        padding = "=" * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode()
        payload = json.loads(payload_json)
        
        if time.time() > payload.get("exp", 0):
            return None # Expired
            
        return payload
    except Exception:
        return None

# Middleware Decorators
def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return f(*args, **kwargs)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            db.log_audit_event("Auth Check", "N/A", "DENIED: Missing Token", "Guest")
            return jsonify({"error": "Authentication token required"}), 401
            
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if not payload:
            db.log_audit_event("Auth Check", "N/A", "DENIED: Invalid/Expired Token", "Guest")
            return jsonify({"error": "Invalid or expired session token"}), 401
            
        request.user = payload
        return f(*args, **kwargs)
    return decorated

def require_roles(*allowed_roles):
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if request.method == "OPTIONS":
                return f(*args, **kwargs)
                
            user = getattr(request, "user", None)
            if not user or user.get("role") not in allowed_roles:
                user_email = user.get("email") if user else "Guest"
                user_role = user.get("role") if user else "None"
                db.log_audit_event(
                    "Permission Check", 
                    "N/A", 
                    f"DENIED: Role {user_role} unauthorized for {request.path}", 
                    user_email
                )
                return jsonify({"error": f"Role unauthorized. Required: {allowed_roles}"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

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
            db.log_audit_event("Signup Failure", "N/A", f"FAILED: User {email} already exists", email)
            return jsonify({"error": "User with this Email/Employee ID already registered"}), 400
            
        new_user = User(email=email, password_hash=password_hash, role=role)
        db_session.add(new_user)
        db_session.commit()
        db.log_audit_event("Signup Success", "N/A", f"SUCCESS: Created user {email}", email)
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
    
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter(User.email == email, User.password_hash == password_hash).first()
        if not user:
            db.log_audit_event("Login Failure", "N/A", "FAILED: Invalid credentials", email)
            return jsonify({"error": "Invalid Email/Employee ID or password"}), 401
            
        token = create_token(user.email, user.role)
        db.log_audit_event("Login Success", "N/A", "SUCCESS", user.email)
        return jsonify({
            "message": "Authentication successful",
            "email": user.email,
            "role": user.role,
            "token": token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@app.route("/api/auth/logout", methods=["POST", "OPTIONS"])
@require_auth
def auth_logout():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
    email = request.user.get("email")
    db.log_audit_event("Logout", "N/A", "SUCCESS", email)
    return jsonify({"message": "Logged out successfully"})

@app.route("/api/cases", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def get_all_cases():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
    res = db.get_all_cases()
    return jsonify({"summary": res["summary"], "total": len(res["cases"]), "cases": res["cases"]})

@app.route("/api/cases/<int:account_id>", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def get_case_by_id(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Account case not found"}), 404
    return jsonify(case)

@app.route("/api/cases/<int:account_id>/graph", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def get_case_graph(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    from backend.database.connection import SessionLocal
    from backend.database.repositories import TransactionRepository
    from backend.graph_engine import MuleGraph
    
    db_session = SessionLocal()
    try:
        txs = TransactionRepository.get_all(db_session)
        if not txs:
            return jsonify({
                "metrics": {
                    "account_id": account_id,
                    "degree": 0, "fan_in": 0, "fan_out": 0,
                    "total_volume": 0.0, "velocity": 0, "centrality": 0.0,
                    "cycles": [], "paths": [], "cluster_nodes": [account_id], "signals": []
                },
                "nodes": [{"id": account_id, "label": f"Account #{account_id}", "color": {"background": "#3b82f6", "border": "#1d4ed8"}, "shape": "box"}],
                "edges": []
            })
            
        graph = MuleGraph(txs)
        
        if account_id not in graph.nodes:
            from backend.database.models import Account
            acc_exists = db_session.query(Account).filter(Account.account_id == account_id).first()
            if not acc_exists:
                return jsonify({"error": "Account not found"}), 404
            return jsonify({
                "metrics": {
                    "account_id": account_id,
                    "degree": 0, "fan_in": 0, "fan_out": 0,
                    "total_volume": 0.0, "velocity": 0, "centrality": 0.0,
                    "cycles": [], "paths": [], "cluster_nodes": [account_id], "signals": []
                },
                "nodes": [{"id": account_id, "label": f"Account #{account_id}", "color": {"background": "#3b82f6", "border": "#1d4ed8"}, "shape": "box"}],
                "edges": []
            })
            
        metrics = graph.compute_metrics(account_id)
        cluster_nodes = metrics["cluster_nodes"]
        nodes_to_render = set(cluster_nodes)
        
        nodes_list = []
        for nid in nodes_to_render:
            node_metrics = graph.compute_metrics(nid)
            is_active = (nid == account_id)
            has_risk = len(node_metrics["signals"]) > 0
            
            bg_color = "#3b82f6" if is_active else ("#f59e0b" if has_risk else "#94a3b8")
            border_color = "#1d4ed8" if is_active else ("#d97706" if has_risk else "#475569")
            text_color = "#ffffff"
            
            nodes_list.append({
                "id": nid,
                "label": f"Account #{nid}\n(Vol: \u20b9{node_metrics['total_volume']/1000:.1f}k)",
                "color": {"background": bg_color, "border": border_color, "highlight": {"background": "#60a5fa", "border": "#1d4ed8"}},
                "shape": "box",
                "font": {"color": text_color, "face": "JetBrains Mono", "size": 11, "bold": is_active},
                "borderWidth": 2 if is_active else 1,
                "shadow": is_active
            })
            
        edges_list = []
        for e in graph.edges:
            src = e["source"]
            dst = e["destination"]
            if src in nodes_to_render and dst in nodes_to_render:
                in_cycle = any(src in cyc and dst in cyc for cyc in metrics["cycles"])
                edge_color = "#ef4444" if in_cycle else "#64748b"
                width = 2 if in_cycle else 1
                
                edges_list.append({
                    "id": e["id"],
                    "from": src,
                    "to": dst,
                    "label": f"\u20b9{e['amount']/1000:.1f}k",
                    "arrows": "to",
                    "color": {"color": edge_color, "highlight": "#ef4444"},
                    "width": width,
                    "font": {"size": 8, "color": "#0f172a", "face": "JetBrains Mono"},
                    "title": f"Amount: \u20b9{e['amount']:,.2f}\nType: {e['type']}\nTime: {e['timestamp']}"
                })
                
        return jsonify({
            "metrics": metrics,
            "nodes": nodes_list,
            "edges": edges_list
        })
    finally:
        db_session.close()

@app.route("/api/cases/<int:account_id>/status", methods=["POST", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "INVESTIGATOR")
def update_case_status(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    data = request.json or {}
    new_status = data.get("status")
    analyst = request.user.get("email")
    if not new_status:
        return jsonify({"error": "Missing status parameter"}), 400
    
    updated_case = db.update_case_status(account_id, new_status, analyst)
    if not updated_case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(updated_case)

@app.route("/api/cases/<int:account_id>/notes", methods=["POST", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR")
def add_case_note(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    data = request.json or {}
    note_text = data.get("note")
    analyst = request.user.get("email")
    if not note_text:
        return jsonify({"error": "Missing note parameter"}), 400
    
    updated_case = db.add_case_note(account_id, note_text, analyst)
    if not updated_case:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(updated_case)

@app.route("/api/cases/<int:account_id>/str-draft", methods=["POST", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR")
def create_str_draft(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    result = db.generate_str_report(account_id)
    if not result:
        return jsonify({"error": "Account case not found for STR generation"}), 404
    return jsonify(result)

@app.route("/api/cases/<int:account_id>/cbs-freeze", methods=["POST", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "INVESTIGATOR")
def cbs_freeze(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    analyst = request.user.get("email")
    ref_no = f"CBS-FRZ-2026-{account_id}-{np.random.randint(1000, 9999)}"
    
    db.update_case_status(account_id, "ESCALATED", analyst)
    db.add_case_note(account_id, f"CBS Emergency Debit Freeze Confirmed. Reference: {ref_no}.", "System")
    db.log_audit_event("CBS Debit Freeze Simulation", account_id, f"FREEZE LOCKED ({ref_no})", analyst)
    
    updated_case = db.get_case(account_id)
    return jsonify({"success": True, "ref_no": ref_no, "case": updated_case})

@app.route("/api/cases/<int:account_id>/download-json", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def download_json(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    db.log_audit_event("Download JSON Data", account_id, "SUCCESS", request.user.get("email"))
    return send_file(
        io.BytesIO(json.dumps(case, indent=2).encode('utf-8')),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"MuleShield_Case_{account_id}.json"
    )

@app.route("/api/cases/<int:account_id>/download-pdf", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def download_pdf(account_id: int):
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    case = db.get_case(account_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    pdf_bytes = generate_pdf_report(case)
    db.log_audit_event("Download PDF Report", account_id, "SUCCESS", request.user.get("email"))
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"MuleShield_Report_{account_id}.pdf"
    )

@app.route("/api/sample-mule-payload", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def get_sample_mule_payload():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
    return jsonify(db.get_sample_mule_payload())

@app.route("/api/audit-logs", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN")
def get_audit_logs():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
    return jsonify({"audit_logs": db.audit_logs})

@app.route("/api/predict", methods=["POST", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST")
def predict_raw_account():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    import pandas as pd
    data = request.json or {}
    raw_df = pd.DataFrame([data.get("account_features", {})])
    result = risk_engine.predict_raw_row(raw_df)
    db.log_audit_event("Account Evaluation Ingestion", "N/A", f"RISK: {result['risk_score']:.4f} ({result['tier']})", request.user.get("email"))
    return jsonify(result)

@app.route("/api/model/metadata", methods=["GET", "OPTIONS"])
@require_auth
@require_roles("ADMIN", "ANALYST", "INVESTIGATOR", "VIEWER")
def get_model_metadata():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
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

# Administrative User Management Endpoint
@app.route("/api/admin/users", methods=["GET", "POST", "OPTIONS"])
@require_auth
@require_roles("ADMIN")
def admin_users():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight successful"}), 200
        
    from backend.database.connection import SessionLocal
    from backend.database.models import User
    
    db_session = SessionLocal()
    try:
        if request.method == "GET":
            users = db_session.query(User).all()
            return jsonify({"users": [{"email": u.email, "role": u.role, "created_at": u.created_at.isoformat()} for u in users]})
        
        data = request.json or {}
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "ANALYST")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
            
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        existing_user = db_session.query(User).filter(User.email == email).first()
        if existing_user:
            return jsonify({"error": "User already registered"}), 400
            
        new_user = User(email=email, password_hash=password_hash, role=role)
        db_session.add(new_user)
        db_session.commit()
        
        db.log_audit_event("Admin Action: Create User", "N/A", f"SUCCESS: Created user {email} ({role})", request.user.get("email"))
        return jsonify({"message": "User created successfully", "email": email, "role": role})
    finally:
        db_session.close()

if __name__ == "__main__":
    print("Starting MuleShield Backend API on http://localhost:8000 ...")
    app.run(host="0.0.0.0", port=8000, debug=False)
