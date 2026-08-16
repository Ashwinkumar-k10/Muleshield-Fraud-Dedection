import sys
import os
import json

sys.path.append('.')
from backend.main import app

client = app.test_client()

def test_backend():
    print("--- VERIFYING BACKEND API ENDPOINTS ---")
    
    # 1. Root
    res = client.get("/")
    assert res.status_code == 200
    print("[OK] GET / -> Status 200")
    
    # 2. Get Cases
    res = client.get("/api/cases")
    assert res.status_code == 200
    data = res.get_json()
    assert "cases" in data
    assert len(data["cases"]) > 0
    print(f"[OK] GET /api/cases -> Returned {len(data['cases'])} cases")
    
    # 3. Get Case 9003
    res = client.get("/api/cases/9003")
    assert res.status_code == 200
    case9003 = res.get_json()
    assert case9003["account_id"] == 9003
    assert case9003["tier"] == "Critical"
    print(f"[OK] GET /api/cases/9003 -> Score: {case9003['risk_score']}, Tier: {case9003['tier']}")
    
    # 4. Generate STR Draft
    res = client.post("/api/cases/9003/str-draft")
    assert res.status_code == 200
    str_data = res.get_json()
    assert "str_draft" in str_data
    assert "SUSPICIOUS TRANSACTION REPORT" in str_data["str_draft"]
    print("[OK] POST /api/cases/9003/str-draft -> Generated STR draft successfully")
    
    print("\nALL BACKEND VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_backend()
