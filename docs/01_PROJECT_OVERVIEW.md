# 🛡️ 01 — PROJECT OVERVIEW
**MuleShield PRO — Explainable and Leakage-Controlled AI Prototype for Suspicious Mule Account Detection**

---

## 1. What is MuleShield PRO?

**MuleShield PRO** is an explainable, leakage-controlled AI/ML prototype built for Public Sector Banks (PSBs). It analyzes bank account transaction metrics, cross-channel payment flows, and regulatory alerts to detect **money mule accounts** and suspicious fund-layering syndicates before fraudulent proceeds can be withdrawn or laundered.

---

## 2. What is a Money Mule Account?

A **money mule account** is a bank account used by cyber-criminals to receive and transfer illegally obtained funds (e.g. proceeds from phishing, UPI scams, investment fraud, or ransomware). Mule accounts act as intermediary "layering" nodes between victims and criminal masterminds.

### Why do banks struggle to detect them?
1. **Low-Volume Inflows / Rapid Outflows:** Funds arrive via fast digital channels (UPI, IMPS) and are immediately split or drained via ATM cash withdrawals or crypto exchanges within minutes.
2. **Normal Customer Profiles:** Many mule accounts belong to real individuals (students, low-income earners, or compromised retail accounts) who rent their credentials for small commissions, making traditional static rule engines ineffective.
3. **High False Positive Rates:** Traditional threshold alerts generate thousands of false alerts daily, overwhelming compliance teams and locking legitimate customer funds unnecessarily.

---

## 3. What Does MuleShield PRO Do?

MuleShield PRO replaces rigid static rules with a zero-leakage, highly calibrated **XGBoost Machine Learning Classifier** combined with **TreeSHAP Explainable AI**, real-time **Flask REST APIs**, and an analyst-facing **Tailwind CSS Dashboard**.

```
┌─────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│  Bank Accounts  │ ───► │ MuleShield Preprocessor │ ───► │ XGBoost Risk Engine     │ ───► │ Analyst Dashboard      │
│ (Transaction &  │      │ (Winsorize, Impute,     │      │ (Predicts Probability   │      │ (Risk Tiering, SHAP,   │
│  Alert Feeds)   │      │  Domain Ratios)         │      │  0.0000 to 1.0000)      │      │  CBS Freeze, STR Draft)│
└─────────────────┘      └─────────────────────────┘      └─────────────────────────┘      └────────────────────────┘
```

---

## 4. System Capabilities & Implementation Status

### **IMPLEMENTED (100% Fully Functional):**
* **Zero-Leakage ML Model:** XGBoost classifier trained on 6,820 sanitized features, achieving **`0.8807 ± 0.0403` PR-AUC** under strict 5-fold Group-Aware Cross-Validation (`0.8833 ± 0.0365` Hyperparameter Search Champion, $100\%$ Precision @ threshold `0.9899`).
* **Explainable AI (TreeSHAP):** Translates raw feature attributions into clear banking domain concepts (*Cash-to-UPI Velocity Ratio*, *Outflow-Inflow Balance Anomaly*).
* **Flask REST API Engine:** Real-time endpoint inference listening on `http://localhost:8000`.
* **Suspicious Transaction Report (STR) Generator:** Compiles FIU-IND compliant report drafts for flagged accounts.

### **SIMULATED (UI Prototype Demonstrations):**
* **Mule Network Ring Topology:** Interactive 2D Vis.js graph demonstrating multi-hop fund-layering networks using sample UI data.
* **CBS Debit Freeze Trigger:** Provides operational receipt confirmation (`CBS-FRZ-2026-9003-8492`) for human-in-the-loop account freezing.
* **Regulatory Watchlists:** In-memory lookups against I4C, CERT-In, and RBI caution feeds.

### **NOT IMPLEMENTED (Future Cloud Scope):**
* Live Core Banking System (Finacle/BaNCS) integration, direct FIU portal transmission, or live production cloud infrastructure.

---

## 5. Input-to-Output Flow Summary

1. **Input:** Raw account transaction metrics, alert counts, and demographic features.
2. **Processing:** Preprocessed via `MuleShieldPreprocessor` (handles missing values, quantile clipping, and feature ratios).
3. **Prediction:** Evaluated by XGBoost model against calibrated threshold (`0.9899`).
4. **Investigation:** Displayed on Analyst Dashboard with SHAP behavioral drivers and regulatory watchlist cross-referencing.
5. **Action:** Analyst confirms CBS Debit Freeze and exports FIU-IND STR report.
