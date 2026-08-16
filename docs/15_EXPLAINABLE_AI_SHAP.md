# 💡 15 — EXPLAINABLE AI & SHAP INTEGRATION

---

## 1. Why Explainability is Mandatory in Banking

Black-box machine learning models cannot be deployed in regulated banking environments without explainability.
* **RBI Audit Requirements:** Regulators require banks to justify why an account was frozen or flagged for suspicious activity.
* **Analyst Actionability:** Compliance officers need clear, domain-specific reasons to draft Suspicious Transaction Reports (STRs).

MuleShield PRO implements **TreeSHAP (SHapley Additive exPlanations)** to calculate exact feature attributions for every classification decision.

---

## 2. Feature Description Mapping (`Description.xlsx`)

In raw model outputs, features are represented as anonymized IDs (`F994`, `F3598`, `F1319`). MuleShield PRO dynamically translates these raw IDs into human-readable banking descriptions using the official dictionary:

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                          SHAP FEATURE DESCRIPTION MAPPING MATRIX                          │
├───────────────┬──────────────────────────────────────────┬────────────────────────────────┤
│ Raw Feature ID│ Business Variable Name (`Description.xlsx`)│ Plain-Language Analyst Label   │
├───────────────┼──────────────────────────────────────────┼────────────────────────────────┤
│ F994          │ MAX_UPI_XFER_TXNS_L7D                    │ Max UPI Transaction Velocity   │
│ F3598         │ DA_CI_NON_CASH_CHQ_TXN_14D_OC            │ Transaction Deviation Anomaly  │
│ F1813         │ NON_CASH_CHQ_AMT_L31D                    │ Non-Cash Total Amount Turnover │
│ F1319         │ MM_UPI_TXNS_CR_L7D                       │ Outflow / Inflow Balance Spread│
│ BANK_FE_CASH  │ BANK_FE_CASH_TO_UPI_RATIO                │ Cash-to-UPI Debit/Inflow Ratio │
│ F3592         │ DA_NON_CASH_CHQ_TXN_14D_OC               │ Micro-Cap Account Anomaly      │
│ F3805         │ TOT_TXNAMT_L14D                          │ Total 14D Transaction Volume   │
│ F2122         │ AVG_CASH_TXNS_L31D                       │ Average Cash Withdrawal Count  │
└───────────────┴──────────────────────────────────────────┴────────────────────────────────┘
```

---

## 3. How SHAP Explanations Function in the UI

When a compliance officer inspects an account card on the Analyst Dashboard (Tab 1), the system displays the top SHAP behavioral drivers derived from sanitized, post-preprocessing features:

```
ACCOUNT INSPECTOR PANEL (#9003 - CRITICAL MULE)
─────────────────────────────────────────────────────────────────────────────
Risk Score: 0.9998 (CRITICAL)
Top SHAP Anomaly Drivers:
  1. Max UPI Transaction Velocity (F994 - Last 7D High-Volume Inflow)
  2. Customer-Induced Transaction Deviation (F3598 - 14D Velocity Anomaly)
  3. Outflow / Inflow Balance Ratio (F1319 - UPI Credit Spread Deviation)
─────────────────────────────────────────────────────────────────────────────
```

This transparent breakdown allows analysts to understand *why* an account was flagged in under 5 seconds.
