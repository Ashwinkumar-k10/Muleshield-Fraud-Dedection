import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000"

print("==========================================")
print("PART B — LIVE DEMO & BAD-INPUT REGRESSION PASS")
print("==========================================")

# 1. Test GET /api/cases
try:
    req = urllib.request.Request(f"{base_url}/api/cases")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        cases = data.get('cases', [])
        print(f"[GET /api/cases] Status {resp.status} OK — Returned {len(cases)} cases.")
        if cases:
            c = cases[0]
            print(f"  Sample Case #{c.get('account_id')}: Risk={c.get('risk_score')}, Tier={c.get('risk_tier')}")
            print(f"  SHAP Drivers: {c.get('shap_drivers')}")
except Exception as e:
    print(f"[GET /api/cases] FAILED: {e}")

# 2. Test POST /api/cases/9003/str-draft
try:
    req = urllib.request.Request(f"{base_url}/api/cases/9003/str-draft", method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"[POST /api/cases/9003/str-draft] Status {resp.status} OK — Received STR Draft ({len(data.get('str_draft', ''))} chars)")
except Exception as e:
    print(f"[POST /api/cases/9003/str-draft] FAILED: {e}")

# 3. Bad Input Test 1: Empty Payload to /api/predict
try:
    req = urllib.request.Request(
        f"{base_url}/api/predict",
        data=json.dumps({}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"[POST /api/predict Empty Payload] Status {resp.status} — Result: {data}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"[POST /api/predict Empty Payload] Handled Gracefully: Status {e.code} — {err_body[:100]}")
except Exception as e:
    print(f"[POST /api/predict Empty Payload] Unexpected Error: {e}")

# 4. Bad Input Test 2: Invalid Types / Malformed JSON to /api/predict
try:
    req = urllib.request.Request(
        f"{base_url}/api/predict",
        data=json.dumps({"F1": "invalid_text_value", "F2": None}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"[POST /api/predict Invalid Types] Status {resp.status} — Result: {data}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"[POST /api/predict Invalid Types] Handled Gracefully: Status {e.code} — {err_body[:100]}")
except Exception as e:
    print(f"[POST /api/predict Invalid Types] Unexpected Error: {e}")

# 5. Bad Input Test 3: Missing Fields Payload to /api/predict
try:
    req = urllib.request.Request(
        f"{base_url}/api/predict",
        data=json.dumps({"account_id": "9999"}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"[POST /api/predict Partial Payload] Status {resp.status} — Result: Risk={data.get('risk_score')}, Tier={data.get('risk_tier')}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"[POST /api/predict Partial Payload] Handled Gracefully: Status {e.code} — {err_body[:100]}")
except Exception as e:
    print(f"[POST /api/predict Partial Payload] Unexpected Error: {e}")
