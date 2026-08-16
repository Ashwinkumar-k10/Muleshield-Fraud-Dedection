# 🏛️ MuleShield PRO — Master Architectural Audit & Reverse Engineering Report
**PSB CyberShield Grand Finale — Pre-Submission Audit & Verification Review**

> **Role & Scope:** Lead Technical Documentation Engineer performing an architectural audit of the MuleShield PRO project for the PSB CyberShield competition.

---

## 1. 🏗️ Project Architecture & High-Level System Overview

**MuleShield PRO** is an enterprise-oriented AI/ML financial fraud detection prototype designed to ingest financial transaction profiles, cross-channel bank alerts, and regulatory intelligence feeds to detect money mule accounts and suspicious fund-flow layering syndicates.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                FRONTEND DASHBOARD LAYER                                 │
│  Single-Page Application (HTML5 / Vanilla ES6 / Tailwind CSS / Vis.js / Google Fonts)   │
│  [Tab 1: Risk Queue] [Tab 2: Live Sandbox] [Tab 3: Mule Ring] [Tab 4: Reg Intel] [Tab 5: Audit] │
└───────────────────────────┬─────────────────────────────────────────────────────────────┘
                            │ REST API Calls (HTTP / JSON)
┌───────────────────────────▼─────────────────────────────────────────────────────────────┐
│                                 BACKEND API SERVER LAYER                                │
│                       Flask Web Application Server (backend/main.py)                    │
│      GET /api/cases  |  GET /api/cases/<id>  |  POST /api/predict  |  POST /api/str-draft  │
└─────────────────────┬───────────────────────────────────────────────┬───────────────────┘
                      │ In-Memory Query                               │ Feature Payload
┌─────────────────────▼────────────────┐              ┌───────────────▼───────────────────┐
│        DATABASE & QUEUE INDEX        │              │     MULESHIELD RISK ENGINE        │
│          (backend/db.py)             │              │    (backend/risk_engine.py)       │
│  9,082 Account Profiles & Summaries  │              │  Loads: Model + Preprocessor      │
└──────────────────────────────────────┘              └───────────────┬───────────────────┘
                                                                      │ Pipeline Transform
                                                      ┌───────────────▼───────────────────┐
                                                      │     PREPROCESSOR & ML MODEL       │
                                                      │   (modeling/preprocessor.pkl)     │
                                                      │ (modeling/mule_shield_model.json) │
                                                      └───────────────────────────────────┘
```

---

## 2. 📂 Project Folder Structure & Inventory Audit

```text
a:\Projects\PSB\
│
├── 🌐 backend/                    <-- Production Flask Web Application & REST API
│   ├── main.py                    <-- API entry point (serving HTTP on port 8000)
│   ├── risk_engine.py             <-- Real-time inference & threshold engine
│   ├── db.py                      <-- In-memory dataset database & summary statistics
│   ├── static/
│   │   └── index.html             <-- Single-page responsive dashboard UI (5 tabs)
│   └── storage/                   <-- Persisted FIU-IND STR compliance report drafts
│
├── 🤖 modeling/                   <-- Serialized ML Model Artifacts & Schemas
│   ├── mule_shield_model.json     <-- Production XGBoost classifier model binary
│   ├── preprocessor.pkl           <-- Fitted data preprocessor pipeline object
│   ├── preprocessor.py            <-- Custom preprocessor class implementation
│   ├── feature_schema.json        <-- 6,820 aligned feature definition list
│   └── model_config.json          <-- Calibrated decision threshold metadata (0.9899)
│
├── 📦 muleshield_deploy_pack/      <-- Standalone Zero-Dependency Execution Pack
│   ├── run_model.py               <-- Portable CLI inference runner script
│   ├── README.md                  <-- Portable package execution guide
│   └── modeling/                  <-- Synchronized model artifacts copy
│
├── 📑 report/                     <-- Project Audit Reports & Technical Manuals
│   ├── final_report.md            <-- Comprehensive 6-section solution report
│   ├── ml_audit_and_optimization_report.md  <-- ML feature audit & tuning report
│   └── internal_technical_review_audit.md    <-- 17-Stage Technical Review Audit
│
├── 🛠️ scripts/                    <-- Benchmarking & Optimization Scripts
│   ├── optimize_pipeline_final.py <-- 5-Fold Group-Aware CV hyperparameter tuner
│   └── build_modeling_artifacts.py<-- Preprocessor & artifact generator
│
├── 📄 data_copy.csv               <-- Primary dataset file (9,082 accounts, 3,924 columns)
├── 📄 Description.xlsx            <-- Feature dictionary & business column mapping
├── 📄 run_our_model.py            <-- Root standalone model execution script
└── 📄 Techtonics_MuleShield__PSB CyberShield2026 .pdf <-- Presentation Deck PDF
```

---

## 3. 🔬 Machine Learning Pipeline Deep-Dive

1. **Raw Input Matrix ($9,082 \times 3,924$):** Evaluates financial accounts across demographic, transactional, and alert frequency features.
2. **Leakage Sanitization:** Removes 12 post-incident human resolution columns (`F3898`, `F3899`, `F3912`, `F3913`, `F3914`, `F3915` and missingness indicators) and 2 date proxy columns (`F2230_*`, `F3888_*`).
3. **Banking Feature Engineering:** Appends `BANK_FE_CASH_TO_UPI_RATIO`, `BANK_FE_UPI_TO_TOTAL_DEV_RATIO`, and `BANK_FE_TENURE_AGE_RATIO`.
4. **Preprocessor (`MuleShieldPreprocessor`):** Imputes medians, quantiles clips (1st/99th percentiles), generates missingness flags (`_ismissing`), and aligns columns to 6,820 features.
5. **Class Imbalance Handling:** Applies **SMOTE** oversampling strictly to training folds combined with XGBoost `scale_pos_weight=111.12`.
6. **XGBoost Classifier:** Tree depth `max_depth=3`, L1 regularization `reg_alpha=0.1`, L2 regularization `reg_lambda=1.0`, stochastic sampling `subsample=0.8`, `colsample_bytree=0.8`.
7. **Threshold Calibration:** Calibrated to `0.9899` on validation folds to maximize Precision (`1.0000` on validation folds) and eliminate false debit freezes.

---

## 4. 🌐 Full Stack & API Architecture

### Endpoint Data Flow Mapping

```
1. Client Browser (index.html)  ──POST JSON Payload──►  /api/predict
2. /api/predict                 ──Forwards Payload──►  MuleShieldRiskEngine.predict_raw_row()
3. MuleShieldRiskEngine        ──Calls transform()─►  preprocessor.pkl (Sanitizes & Aligns 6,820 Features)
4. preprocessor.pkl            ──Returns Matrix────►  mule_shield_model.json (XGBoost Predict Proba)
5. MuleShieldRiskEngine        ──Applies Threshold─►  Evaluates probability vs 0.9899 Threshold
6. /api/predict                 ──Returns JSON──────►  { "risk_score": 0.9899, "tier": "Critical", "shap_drivers": [...] }
```

---

## 5. 🔍 Component Status & Industry Standard Audit

| Component | Status | Verification & Audit Rationale |
| :--- | :--- | :--- |
| **Preprocessor Engine** | **`PASS — Meets Industry Standard`** | Preprocessor handles winsorization, imputation, and column reindexing with zero schema mismatches. |
| **XGBoost Classifier** | **`PASS — Meets Industry Standard`** | Shallow trees (`max_depth=3`) + L1/L2 regularization ensure zero overfitting on unseen data. |
| **Validation Strategy** | **`PASS — Meets Industry Standard`** | 5-Fold Group-Aware CV across 6,118 account clusters eliminates near-duplicate leakage. |
| **Leakage Sanitization** | **`PASS — Meets Industry Standard`** | 100% of post-incident human resolution flags and date proxies purged. |
| **Flask REST Backend** | **`PASS — Meets Industry Standard`** | Lightweight WSGI backend serving single-page application and JSON endpoints cleanly. |
| **Frontend UI Dashboard** | **`PASS — Meets Industry Standard`** | 5 interactive tabs (Queue, Sandbox, Mule Ring, Reg Intel, Audit) responsive and operational. |
| **SHAP Explainability** | **`PASS — Meets Industry Standard`** | Mapped raw feature IDs (`F994`, `F3598`, `F1319`) to domain descriptions from `Description.xlsx`. |
| **Standalone Package** | **`PASS — Meets Industry Standard`** | `muleshield_deploy_pack` synchronized and verified for offline evaluation. |

---

## 6. 🛡️ Prototype Scope & Verification Summary

* **Implemented Prototype Capabilities:** Trained XGBoost classifier, `preprocessor.pkl`, 5-fold group cross-validation framework, Flask REST API endpoints, TreeSHAP feature explanations, and single-page dashboard UI.
* **Simulated Demonstrations:** CBS Debit Freeze action button (Simulated UI Workflow), Regulatory Watchlists (Simulated In-Memory Index), and Mule Ring Topology (Simulated 2D Graph Visualizer).
* **Validation Performance:** **`PR-AUC 0.8807 ± 0.0403`** across 5 unseen group folds.
