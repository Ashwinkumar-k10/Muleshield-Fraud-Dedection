# 📚 MuleShield PRO — Master Technical Documentation Package
**PSB CyberShield Hackathon — Final Technical Documentation**

Welcome to the official master documentation hub for **MuleShield PRO**. This documentation package covers the complete project lifecycle from raw dataset ingestion, leakage sanitization, and 5-fold group cross-validation to backend REST API endpoints, TreeSHAP explainability, and single-page dashboard UI integration.

---

## 📑 Master Navigation Index

### 📌 Section I: Project Overview & Scope
* [01 — Project Overview](01_PROJECT_OVERVIEW.md) — Beginner-friendly explanation of MuleShield PRO, mule accounts, and core system capabilities.
* [02 — Problem Statement](02_PROBLEM_STATEMENT.md) — Alignment with the official PSB CyberShield problem statement and scope distinctions.

---

### 📊 Section II: Dataset Analysis & Preprocessing
* [03 — Dataset Description](03_DATASET_DESCRIPTION.md) — Overview of `data_copy.csv` (9,082 rows x 3,924 columns), target class distribution, and taxonomy.
* [04 — Dataset Audit](04_DATASET_AUDIT.md) — Quality metrics, duplicate clustering analysis, and outlier winsorization bounds.
* [05 — Data Preprocessing](05_DATA_PREPROCESSING.md) — Detailed transformation pipeline (`MuleShieldPreprocessor`) and training/inference consistency.
* [06 — Data Leakage Audit](06_DATA_LEAKAGE_AUDIT.md) — Forensic audit of purged post-incident resolution flags (`F3912`, `F3914`, etc.) and date proxies.
* [07 — Feature Engineering](07_FEATURE_ENGINEERING.md) — Inventory of derived banking domain ratios (`BANK_FE_CASH_TO_UPI_RATIO`, etc.).
* [08 — Class Imbalance Strategy](08_CLASS_IMBALANCE.md) — Benchmark comparison of SMOTE, ADASYN, and `scale_pos_weight` across 5-Fold Group CV.

---

### 🤖 Section III: Model Development, Optimization & Validation
* [09 — Model Development](09_MODEL_DEVELOPMENT.md) — XGBoost algorithm selection rationale, beginner-friendly explanation, and production parameters.
* [10 — Model Optimization](10_MODEL_OPTIMIZATION.md) — Hyperparameter grid search logs, tree depth regularization, and L1/L2 penalties.
* [11 — Validation Strategy](11_VALIDATION_STRATEGY.md) — 5-Fold Stratified Group K-Fold Cross-Validation framework using 6,118 group clusters.
* [12 — Model Evaluation](12_MODEL_EVALUATION.md) — Verified CV metrics (`0.8807 ± 0.0403` PR-AUC), 3-model baseline comparison, and confusion matrix.
* [13 — Generalization & Hidden Validation](13_GENERALIZATION_AND_HIDDEN_VALIDATION.md) — Generalization risk matrix for organizer's unseen test set.
* [14 — Error Analysis](14_ERROR_ANALYSIS.md) — Misclassification diagnostics for False Positives and False Negatives.
* [15 — Explainable AI (SHAP)](15_EXPLAINABLE_AI_SHAP.md) — TreeSHAP integration and dynamic feature mapping using `Description.xlsx`.

---

### 🌐 Section IV: Full-Stack Architecture & Application Features
* [16 — System Architecture](16_SYSTEM_ARCHITECTURE.md) — High-level system architecture diagram and component responsibility matrix.
* [17 — Backend REST API](17_BACKEND_API.md) — Complete specification of Flask REST endpoints (`/api/cases`, `/api/predict`, etc.).
* [18 — Frontend Dashboard](18_FRONTEND_DASHBOARD.md) — Tab-by-tab breakdown of the single-page Tailwind CSS analyst dashboard.
* [19 — Mule Network Visualization](19_MULE_NETWORK_VISUALIZATION.md) — Documentation of the Vis.js interactive Mule Ring topology graph (Simulated Demo).
* [20 — CBS Freeze Demo](20_CBS_FREEZE_DEMO.md) — Documentation of the mock Core Banking System debit freeze action button (Simulated Demo).
* [21 — STR Generation](21_STR_GENERATION.md) — Automated Suspicious Transaction Report draft generator for FIU-IND compliance.
* [22 — Regulatory Intelligence](22_REGULATORY_INTELLIGENCE.md) — Cross-referencing accounts against I4C, CERT-In, and RBI caution lists.

---

### 🛠️ Section V: Tech Stack, Deployment & Verification
* [23 — Complete Tech Stack](23_TECH_STACK.md) — Technology table detailing all libraries, frameworks, and CDNs used.
* [24 — Artifacts & File Structure](24_ARTIFACTS_AND_FILE_STRUCTURE.md) — Inventory of repository directories and serialized model binaries.
* [25 — Deployment Guide](25_DEPLOYMENT.md) — Instructions for running the web application and standalone deployment pack offline.
* [26 — Reproducibility Guide](26_REPRODUCIBILITY.md) — Fixed random seeds and step-by-step reproduction instructions.
* [27 — Security & Compliance](27_SECURITY_AND_COMPLIANCE.md) — Banking auditability, PMLA Section 12 compliance, and security controls.
* [28 — Competition Readiness](28_COMPETITION_READINESS.md) — Hackathon verification checklist.
* [29 — Limitations & Future Roadmap](29_LIMITATIONS_AND_FUTURE_WORK.md) — Current prototype disclaimers and future production roadmap.
* [30 — End-to-End Project Flow](30_END_TO_END_PROJECT_FLOW.md) — Step-by-step 24-step walkthrough from data ingestion to final action.
* [Pre-Submission Integrity Audit](PRE_SUBMISSION_INTEGRITY_AUDIT.md) — Complete audit verification matrix and consistency log.
