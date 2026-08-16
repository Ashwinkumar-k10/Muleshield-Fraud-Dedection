# 🔌 17 — BACKEND REST API DOCUMENTATION

---

## 1. REST API Overview

The backend server is built using **Python Flask** ([backend/main.py](file:///a:/Projects/PSB/backend/main.py)) and listens on port `8000`. All API responses use standard `application/json` formatting.

---

## 2. API Endpoint Specification

### 1. `GET /api/cases`
* **Purpose:** Fetches the operational case queue and overall dataset summary statistics.
* **HTTP Method:** `GET`
* **Query Parameters:** Optional `tier` filter (`Critical`, `High`, `Medium`, `Low`).
* **Response Body Example:**
  ```json
  {
    "summary": {
      "total_evaluated": 9082,
      "critical_alerts": 87,
      "high_risk": 19,
      "cleared_accounts": 8934
    },
    "total": 382,
    "cases": [
      {
        "account_id": "9003",
        "risk_score": 0.9998,
        "tier": "Critical",
        "primary_flag": "HIGH_VALUE_UPI_DB_TXNS",
        "flag_count": 4
      }
    ]
  }
  ```

---

### 2. `GET /api/cases/<account_id>`
* **Purpose:** Retrieves detailed profile metrics, SHAP drivers, and regulatory watchlist status for a specific account.
* **HTTP Method:** `GET`
* **Response Body Example:**
  ```json
  {
    "account_id": "9003",
    "risk_score": 0.9998,
    "tier": "Critical",
    "top_shap_drivers": ["F994", "F3598", "F1319"],
    "regulatory_flags": {
      "i4c_db": "FLAGGED",
      "cert_in_botnet": "CLEAR",
      "rbi_caution_list": "FLAGGED"
    }
  }
  ```

---

### 3. `POST /api/predict`
* **Purpose:** Evaluates raw JSON account features in real time against `preprocessor.pkl` and `mule_shield_model.json`.
* **HTTP Method:** `POST`
* **Request Body Example:** `{"F1": 12.0, "F2": 0.5, "F994": 15.0, ...}`
* **Response Body Example:**
  ```json
  {
    "risk_score": 0.9791,
    "tier": "Critical",
    "mule_detected": true,
    "exceeds_threshold": true,
    "calibrated_threshold": 0.9899,
    "shap_drivers": [...]
  }
  ```

---

### 4. `POST /api/cases/<account_id>/str-draft`
* **Purpose:** Generates a legal-grade Suspicious Transaction Report (STR) draft for FIU-IND compliance filing.
* **HTTP Method:** `POST`
* **Response Body Example:**
  ```json
  {
    "account_id": "9003",
    "str_draft": "SUSPICIOUS TRANSACTION REPORT (STR) DRAFT - FIU-IND COMPLIANCE\nAccount Index: #9003\nRisk Score: 0.9998...",
    "status": "Generated"
  }
  ```

---

### 5. `GET /api/sample-mule-payload`
* **Purpose:** Provides a pre-populated raw JSON mule payload for testing in the Live Sandbox tab.
* **HTTP Method:** `GET`
* **Response Body Example:** `{"F1": 15.0, "F2": 3.2, "F994": 15.0, ...}`
