# 📁 24 — ARTIFACTS & FILE STRUCTURE INVENTORY

---

## 1. Project Directory Structure

```text
a:\Projects\PSB\
│
├── 🌐 backend/                    <-- Production Flask Web Application & REST API
│   ├── main.py                    <-- API entry point (serving HTTP on port 8000)
│   ├── risk_engine.py             <-- Real-time prediction & threshold engine
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
│   ├── README.txt                 <-- Portable package execution guide
│   └── modeling/                  <-- Synchronized model artifacts copy
│
├── 📑 report/                     <-- Project Audit Reports & Technical Manuals
│   ├── final_report.md            <-- Comprehensive 6-section solution report
│   ├── ml_audit_and_optimization_report.md  <-- ML feature audit & tuning report
│   ├── internal_technical_review_audit.md    <-- 17-Stage Technical Committee Audit
│   └── production_readiness_architectural_audit.md <-- Architectural audit
│
├── 🛠️ scripts/                    <-- Benchmarking & Optimization Scripts
│   ├── optimize_pipeline_final.py <-- 5-Fold Group-Aware CV hyperparameter tuner
│   └── build_modeling_artifacts.py<-- Preprocessor & artifact generator
│
├── 📚 docs/                       <-- Master Technical Documentation Package
│   ├── README.md                  <-- Master documentation hub index
│   ├── DOCUMENTATION_VERIFICATION.md <-- Verification check report
│   └── 01_PROJECT_OVERVIEW.md to 30_END_TO_END_PROJECT_FLOW.md
│
├── 📄 Description.xlsx            <-- Feature dictionary & business column mapping
├── 📄 Techtonics_MuleShield__PSB CyberShield2026 .pdf <-- Presentation Deck PDF
├── 📄 run_our_model.py            <-- Standalone root CLI model runner
└── 📄 .gitignore                  <-- Configured Git exclusion file
```

---

## 2. Key Serialized Artifact Details

1. **`modeling/mule_shield_model.json`:** Native XGBoost JSON format model file ($0.8807$ PR-AUC).
2. **`modeling/preprocessor.pkl`:** Fitted `MuleShieldPreprocessor` object handling missing values, winsorization quantiles, and feature engineering.
3. **`modeling/feature_schema.json`:** JSON array listing exact 6,820 feature names in order.
4. **`modeling/model_config.json`:** Metadata file defining `decision_threshold: 0.9899` and `pos_weight: 111.12`.
