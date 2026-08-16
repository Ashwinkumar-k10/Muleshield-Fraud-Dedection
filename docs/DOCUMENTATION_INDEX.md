# 🗺️ MuleShield PRO — Master Documentation Index & File Map

This document provides a complete sitemap and reference guide for all **34 Markdown documentation manuals**, **4 Technical Audit reports**, and repository guides in the **MuleShield PRO** project.

---

## 🏛️ Master Overview & Core Verification Files

| File Link | Core Purpose & Information Provided |
| :--- | :--- |
| **[`README.md`](file:///a:/Projects/PSB/README.md)** | **Master Landing Page:** System architecture overview, key features, quick-start commands, live demo links, and top-level directory structure. |
| **[`docs/31_CANONICAL_METRICS_TABLE.md`](file:///a:/Projects/PSB/docs/31_CANONICAL_METRICS_TABLE.md)** | **Single Source of Truth Metrics Table:** Defines canonical PR-AUC (`0.9180` OOF, `0.9131 ± 0.0458` 5-fold CV), 100% Precision threshold table (`0.9899`), in-sample vs out-of-fold distinctions, and 10% null cell stress test results. |
| **[`docs/32_ANTICIPATED_JUDGE_QUESTIONS.md`](file:///a:/Projects/PSB/docs/32_ANTICIPATED_JUDGE_QUESTIONS.md)** | **Judge Defensibility Q&A Guide:** 2-to-4 sentence honest answers to 6 critical judge questions (real generalization estimate, 100% precision proof, hidden validation drift, leakage prevention, simulated vs real features, XGBoost selection). |
| **[`docs/DOCUMENTATION_VERIFICATION.md`](file:///a:/Projects/PSB/docs/DOCUMENTATION_VERIFICATION.md)** | **Documentation Integrity Verification:** Audit report confirming 100% file presence, zero code modifications, metric alignment, and disclaimers on simulated features. |
| **[`docs/PRE_SUBMISSION_INTEGRITY_AUDIT.md`](file:///a:/Projects/PSB/docs/PRE_SUBMISSION_INTEGRITY_AUDIT.md)** | **Pre-Submission Audit Matrix:** 14-point checklist verifying SHAP leakage fixes, purged feature removal, STR draft verification, and score standardization. |

---

## 🔬 Machine Learning & Data Pipeline (Docs 01 – 15)

| File Link | Core Purpose & Information Provided |
| :--- | :--- |
| **[`docs/01_PROJECT_OVERVIEW.md`](file:///a:/Projects/PSB/docs/01_PROJECT_OVERVIEW.md)** | **Executive Project Summary:** High-level solution vision, key operational capabilities, target problem scope, and core banking goals. |
| **[`docs/02_PROBLEM_STATEMENT.md`](file:///a:/Projects/PSB/docs/02_PROBLEM_STATEMENT.md)** | **Problem Statement Mapping:** Maps MuleShield PRO capabilities directly to PSB CyberShield hackathon requirements and RBI guidelines. |
| **[`docs/03_DATASET_DESCRIPTION.md`](file:///a:/Projects/PSB/docs/03_DATASET_DESCRIPTION.md)** | **Data Taxonomy & Schema:** Breakdowns of all 3,924 raw column features, transaction types, customer demographics, and target column (`F3924`). |
| **[`docs/04_DATASET_AUDIT.md`](file:///a:/Projects/PSB/docs/04_DATASET_AUDIT.md)** | **Data Quality Audit:** Missing value percentages, zero-variance feature identification, extreme quantile distributions, and row counts. |
| **[`docs/05_DATA_PREPROCESSING.md`](file:///a:/Projects/PSB/docs/05_DATA_PREPROCESSING.md)** | **Preprocessing Implementation:** Details median imputation, 1st/99th percentile quantile clipping (winsorization), categorical one-hot encoding, and 6,820 feature alignment. |
| **[`docs/06_DATA_LEAKAGE_AUDIT.md`](file:///a:/Projects/PSB/docs/06_DATA_LEAKAGE_AUDIT.md)** | **Leakage Audit & Purge Log:** Details why 12 post-incident human resolution flags (`F3898`, `F3912`, `F3914`, etc.) and 2 date proxies (`F2230`, `F3888`) were purged to prevent artificial score inflation. |
| **[`docs/07_FEATURE_ENGINEERING.md`](file:///a:/Projects/PSB/docs/07_FEATURE_ENGINEERING.md)** | **Derived Banking Ratios:** Formulas and behavioral justifications for `CASH_TO_UPI_RATIO`, `UPI_TO_TOTAL_DEV_RATIO`, and `TENURE_AGE_RATIO`. |
| **[`docs/08_CLASS_IMBALANCE.md`](file:///a:/Projects/PSB/docs/08_CLASS_IMBALANCE.md)** | **Class Imbalance Handling:** Benchmark comparing SMOTE, ADASYN, Borderline-SMOTE, scale_pos_weight, and unweighted baseline across 81 positive fraud cases. |
| **[`docs/09_MODEL_DEVELOPMENT.md`](file:///a:/Projects/PSB/docs/09_MODEL_DEVELOPMENT.md)** | **XGBoost Selection & Rationale:** Beginner-friendly explanation of XGBoost boosting trees, hyperparameter parameters (`max_depth=3`, L1/L2 penalties), and model config JSON. |
| **[`docs/10_MODEL_OPTIMIZATION.md`](file:///a:/Projects/PSB/docs/10_MODEL_OPTIMIZATION.md)** | **Hyperparameter Grid Tuning:** 4 candidate grid-search configurations, tree regularization choices, and parameter selection rationale. |
| **[`docs/11_VALIDATION_STRATEGY.md`](file:///a:/Projects/PSB/docs/11_VALIDATION_STRATEGY.md)** | **Zero-Leakage Group CV Framework:** 5-Fold Stratified Group-Aware Cross-Validation across 6,118 similarity clusters to prevent near-duplicate account leakage. |
| **[`docs/12_MODEL_EVALUATION.md`](file:///a:/Projects/PSB/docs/12_MODEL_EVALUATION.md)** | **Evaluation Benchmarks & Baselines:** Head-to-head comparison table of XGBoost vs Random Forest vs Logistic Regression, plus full-dataset confusion matrix. |
| **[`docs/13_GENERALIZATION_AND_HIDDEN_VALIDATION.md`](file:///a:/Projects/PSB/docs/13_GENERALIZATION_AND_HIDDEN_VALIDATION.md)** | **Hidden Dataset Readiness:** 7-vector generalization risk matrix, fold stability analysis, and drift mitigation strategies for unseen test evaluation. |
| **[`docs/14_ERROR_ANALYSIS.md`](file:///a:/Projects/PSB/docs/14_ERROR_ANALYSIS.md)** | **Misclassification Breakdown:** Forensic analysis of false negatives (subtle low-velocity mules) and false positives (legitimate business spikes). |
| **[`docs/15_EXPLAINABLE_AI_SHAP.md`](file:///a:/Projects/PSB/docs/15_EXPLAINABLE_AI_SHAP.md)** | **TreeSHAP Explainability:** Explanation of how raw feature IDs (`F994`, `F3598`, `F1319`) are dynamically mapped to plain-language banking anomaly descriptions. |

---

## 💻 System Architecture & Backend/Frontend (Docs 16 – 22)

| File Link | Core Purpose & Information Provided |
| :--- | :--- |
| **[`docs/16_SYSTEM_ARCHITECTURE.md`](file:///a:/Projects/PSB/docs/16_SYSTEM_ARCHITECTURE.md)** | **Full System Architecture:** ASCII flow diagrams, data ingestion pipeline, Flask server layer, and frontend interaction flow. |
| **[`docs/17_BACKEND_API.md`](file:///a:/Projects/PSB/docs/17_BACKEND_API.md)** | **Flask REST API Reference:** Complete HTTP request/response payloads, endpoint specs (`/api/cases`, `/api/predict`, `/api/cases/<id>/str-draft`), and error handling behavior. |
| **[`docs/18_FRONTEND_DASHBOARD.md`](file:///a:/Projects/PSB/docs/18_FRONTEND_DASHBOARD.md)** | **Analyst Dashboard UX Guide:** Detailed walkthrough of all 5 UI tabs (Queue, Anomaly Sandbox, Mule Ring, Regulatory Intelligence, Audit Trail). |
| **[`docs/19_MULE_NETWORK_VISUALIZATION.md`](file:///a:/Projects/PSB/docs/19_MULE_NETWORK_VISUALIZATION.md)** | **Mule Ring Graph Topology:** Explains the interactive 2D Vis.js network graph rendering 8-node fund-layering syndicates and disclaimer badges. |
| **[`docs/20_CBS_FREEZE_DEMO.md`](file:///a:/Projects/PSB/docs/20_CBS_FREEZE_DEMO.md)** | **Simulated CBS Debit Freeze:** Step-by-step workflow of the mock Core Banking System debit freeze action button and confirmation receipt generator. |
| **[`docs/21_STR_GENERATION.md`](file:///a:/Projects/PSB/docs/21_STR_GENERATION.md)** | **FIU-IND STR Report Generator:** Regulatory compliance explanation of automated Suspicious Transaction Report draft formatting under PMLA Section 12. |
| **[`docs/22_REGULATORY_INTELLIGENCE.md`](file:///a:/Projects/PSB/docs/22_REGULATORY_INTELLIGENCE.md)** | **Watchlist Cross-Referencing:** Overview of simulated in-memory lookups against I4C (Cyber Crime Portal), CERT-In, and RBI Caution Lists. |

---

## 📦 Operations, Compliance & End-to-End Flow (Docs 23 – 30)

| File Link | Core Purpose & Information Provided |
| :--- | :--- |
| **[`docs/23_TECH_STACK.md`](file:///a:/Projects/PSB/docs/23_TECH_STACK.md)** | **Technology Stack Inventory:** Complete list of libraries, frameworks, Python packages, and versions used across the repository. |
| **[`docs/24_ARTIFACTS_AND_FILE_STRUCTURE.md`](file:///a:/Projects/PSB/docs/24_ARTIFACTS_AND_FILE_STRUCTURE.md)** | **Directory & Artifact Tree:** Explains the purpose of every folder (`backend/`, `data/`, `modeling/`, `deployment/`, `report/`, `scripts/`, `docs/`). |
| **[`docs/25_DEPLOYMENT.md`](file:///a:/Projects/PSB/docs/25_DEPLOYMENT.md)** | **Deployment Instructions:** Execution guides for running the live Flask web server (`python backend/main.py`) and standalone CLI package (`python deployment/run_model.py`). |
| **[`docs/26_REPRODUCIBILITY.md`](file:///a:/Projects/PSB/docs/26_REPRODUCIBILITY.md)** | **Reproducibility Guide:** Deterministic random seeds (`42`), environment setup, and instructions for re-running out-of-fold validation scripts. |
| **[`docs/27_SECURITY_AND_COMPLIANCE.md`](file:///a:/Projects/PSB/docs/27_SECURITY_AND_COMPLIANCE.md)** | **Security & Banking Audit:** PMLA Section 12 compliance, RBI AI governance guidelines, pre-anonymized dataset privacy, and zero PII processing rules. |
| **[`docs/28_COMPETITION_READINESS.md`](file:///a:/Projects/PSB/docs/28_COMPETITION_READINESS.md)** | **Competition Readiness Scorecard:** Final pre-submission checklist confirming zero leakage, group isolation, server uptime, and hackathon strengths. |
| **[`docs/29_LIMITATIONS_AND_FUTURE_WORK.md`](file:///a:/Projects/PSB/docs/29_LIMITATIONS_AND_FUTURE_WORK.md)** | **Limitations & Production Roadmap:** Transparent disclosure of prototype boundaries (simulated CBS/watchlists) and future GNN/Kafka roadmap. |
| **[`docs/30_END_TO_END_PROJECT_FLOW.md`](file:///a:/Projects/PSB/docs/30_END_TO_END_PROJECT_FLOW.md)** | **24-Step System Journey:** Complete step-by-step walkthrough covering raw data ingestion, preprocessor fitting, SMOTE oversampling, XGBoost training, OOF validation, API serving, and UI actions. |

---

## 📑 Specialized Technical Audit Reports (`report/`)

| File Link | Core Purpose & Information Provided |
| :--- | :--- |
| **[`report/final_report.md`](file:///a:/Projects/PSB/report/final_report.md)** | **Final Solution Report:** Executive solution paper detailing problem alignment, data leakage sanitization, XGBoost metrics, and operational impact. |
| **[`report/ml_audit_and_optimization_report.md`](file:///a:/Projects/PSB/report/ml_audit_and_optimization_report.md)** | **ML Audit & Tuning Report:** Forensic leak audit, SMOTE vs ADASYN imbalance comparison table, tree depth constraints, and hyperparameter selection. |
| **[`report/internal_technical_review_audit.md`](file:///a:/Projects/PSB/report/internal_technical_review_audit.md)** | **17-Stage Technical Review Audit:** Detailed evaluation across 17 MLOps, MLDD, and banking compliance stages (data leakage, fold stability, SHAP attributions, API resilience). |
| **[`report/production_readiness_architectural_audit.md`](file:///a:/Projects/PSB/report/production_readiness_architectural_audit.md)** | **Architectural Reverse Engineering Audit:** Deep-dive analysis of system data-flow, memory structures, REST contracts, and standalone deployment packaging. |
