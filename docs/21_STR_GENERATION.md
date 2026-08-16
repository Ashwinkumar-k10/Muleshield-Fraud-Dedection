# 📄 21 — SUSPICIOUS TRANSACTION REPORT (STR) DRAFT GENERATOR

---

## 1. Regulatory Context (FIU-IND Compliance)

Under the **Prevention of Money Laundering Act (PMLA), Section 12**, banks in India are legally mandated to furnish **Suspicious Transaction Reports (STRs)** to the **Financial Intelligence Unit - India (FIU-IND)** within 7 days of identifying suspicious activity.

MuleShield PRO automates STR report drafting by combining account metrics, risk score probability, SHAP behavioral anomaly drivers, and watchlist matches into a legal-grade report template.

---

## 2. STR Generation Workflow

```
┌─────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ Analyst Selects │ ───► │ POST /api/cases/<id>/   │ ───► │ Backend Formats Text    │ ───► │ Report Saved & Returned │
│ Account Card    │      │ str-draft               │      │ Compliance Template     │      │ backend/storage/        │
│ (e.g. #9003)    │      │                         │      │                         │      │ str_report_9003.txt     │
└─────────────────┘      └─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 3. Sample Generated STR Report Text

```text
================================================================================
          FINANCIAL INTELLIGENCE UNIT - INDIA (FIU-IND)
               SUSPICIOUS TRANSACTION REPORT (STR) DRAFT
================================================================================

1. SUBJECT DETAILS:
   - Account Index: #9003
   - Risk Assessment Score: 0.9998 (CRITICAL TIER)
   - Calibrated Decision Threshold: 0.9899

2. KEY ANOMALY & SHAP JUSTIFICATION:
   The MuleShield AI classifier flagged this account due to significant deviations in the following core behavioral drivers:
  - F994: High behavioral anomaly score (Max UPI Transaction Velocity - Last 7D)
  - F3598: High behavioral anomaly score (Customer-Induced Transaction Deviation)
  - F1319: High behavioral anomaly score (Outflow / Inflow Balance Spread Ratio)

3. REGULATORY DATABASE INTERSECTION:
   - I4C Cyber Fraud DB: FLAGGED
   - CERT-In Botnet List: CLEAR
   - RBI Caution List: FLAGGED

4. RECOMMENDED COMPLIANCE ACTION:
   Execute immediate freeze on debit transactions and transmit this STR to FIU-IND per PMLA guidelines.

==================================================
Report Generated: 2026-07-29 09:40 IST
Status: DRAFT READY FOR ANALYST SIGN-OFF
================================================================================
```

---

## 4. Scope Disclaimer

* **Implemented Feature:** Automated generation of formatted text drafts stored in `backend/storage/str_report_<id>.txt`.
* **Future Production Scope:** Direct XML formatting and automated submission over the secure FIU-IND FINnet gateway.
