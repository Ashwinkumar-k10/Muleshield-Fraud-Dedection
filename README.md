# 🛡️ MuleShield PRO — AI-Powered Mule Account & Cyber-Fraud Detection Platform
**PSB CyberShield Hackathon — Production Architecture Submission**

MuleShield PRO is an enterprise AI/ML financial fraud detection platform built for Public Sector Banks (PSBs). It ingests financial transactions, cross-channel payment flows, and regulatory alerts to detect **money mule accounts** and suspicious fund-layering syndicates before fraudulent proceeds can be withdrawn or laundered.

---

## 📐 Project Architecture & Directory Structure

```text
MuleShield-Fraud-Detection/
│
├── 🌐 frontend/                   <-- Frontend Presentation Layer
│   └── index.html                 <-- Single-Page Tailwind CSS Analyst Dashboard (5 tabs)
│
├── ⚙️ backend/                    <-- Backend Application & REST API Host
│   ├── main.py                    <-- Flask REST API server (serving port 8000)
│   ├── risk_engine.py             <-- Real-time prediction & threshold engine
│   ├── db.py                      <-- In-memory dataset database index
│   └── storage/                   <-- Persisted FIU-IND STR compliance report drafts
│
├── 🤖 modeling/                   <-- Serialized ML Model Artifacts & Schemas
│   ├── preprocessor.py            <-- Custom preprocessor class implementation
│   ├── preprocessor.pkl           <-- Fitted data preprocessor pipeline object
│   ├── mule_shield_model.json     <-- Production XGBoost classifier model binary
│   ├── feature_schema.json        <-- 6,820 aligned feature definition list
│   └── model_config.json          <-- Calibrated decision threshold metadata (0.9899)
│
├── 🛠️ scripts/                    <-- Model Optimization & Artifact Building
│   ├── optimize_pipeline_final.py <-- 5-Fold Group-Aware CV hyperparameter tuner
│   └── build_modeling_artifacts.py<-- Preprocessor & artifact generator
│
├── 📊 data/                       <-- Production Input Datasets
│   ├── data_copy.csv              <-- Primary dataset file (9,082 accounts, 3,924 columns)
│   └── Description.xlsx           <-- Feature dictionary & business column mapping
│
├── 📦 deployment/                 <-- Portable Standalone Execution Package
│   ├── run_model.py               <-- Standalone CLI inference runner script
│   ├── README.txt                 <-- Standalone package execution guide
│   └── modeling/                  <-- Synchronized model artifacts copy
│
├── 📑 report/                     <-- Project Audit Reports & Technical Manuals
│   ├── final_report.md            <-- Comprehensive solution report
│   ├── ml_audit_and_optimization_report.md  <-- ML feature audit & tuning report
│   ├── internal_technical_review_audit.md    <-- 17-Stage Technical Audit
│   └── production_readiness_architectural_audit.md <-- Reverse engineering audit
│
├── 📚 docs/                       <-- Complete Technical Documentation Package (32 files)
│   ├── README.md                  <-- Master documentation hub index
│   └── 01_PROJECT_OVERVIEW.md to PRE_SUBMISSION_INTEGRITY_AUDIT.md
│
├── 📄 run_our_model.py            <-- Root standalone CLI inference runner
├── 📄 README.md                   <-- Master repository README
└── 📄 .gitignore                  <-- Git version control configuration
```

---

## ⚡ Quick Start Guide

### 1. Start the Live Web Backend & Analyst Dashboard
```bash
python backend/main.py
```
Open your browser and navigate to **`http://localhost:8000`** to access the 5-tab Analyst Dashboard.

### 2. Run Root Command-Line Model Inference
```bash
python run_our_model.py
```

### 3. Run Portable Standalone Deployment Package
```bash
python deployment/run_model.py
```

---

## 🔬 ML Model Performance Metrics (5-Fold Group-Aware CV)

* **PR-AUC:** **`0.8807 ± 0.0403`**
* **Validation Precision:** **`1.0000` (100% Precision)**
* **Validation Recall:** **`0.6164`**
* **Calibrated Decision Threshold:** **`0.9899`**
* **Sanitized Feature Count:** **`6,820` aligned features** (Purged all 12 post-incident resolution flags & date proxies).
