# MuleShield PRO V2.0.0 — Release Guide & Feature Categorization

This document provides a final release guide classifying all system capabilities of the **MuleShield PRO v2.0.0** platform.

---

## 🏛️ V1 BASELINE

These core ML capabilities constitute the initial fraud-detection engine baseline:
* **Baseline Classifier Model:** Champion XGBoost Classifier (`max_depth=3`, L1/L2 regularized) yielding `0.8807 ± 0.0403` PR-AUC on 5-Fold Group CV.
* **Leakage Sanitizer Filter:** Complete removal of 14 target-leakage features from training data (demographics proxy timestamps and post-incident resolution flags).
* **Calibrated Decision Boundary:** Constant threshold locked at `0.9899` to ensure **100% Precision on validation folds** (zero false locks).
* **Fitted Data Preprocessor:** Serialized `preprocessor.pkl` transformer performing winsorization clipping (1st/99th percentile) and median imputation.

---

## 🚀 V2 IMPLEMENTED

These components are fully built, integrated, tested, and operational in code:
* **API Gateway Service:** REST API routed on port `8000` handling user registration, login, dashboard queries, and routing downstream requests.
* **ML Inference Microservice:** Decoupled Flask inference app served on port `8080` processing features and returning predictions along with dynamic TreeSHAP explainability attributions.
* **Graph Computation Microservice:** Decoupled network topology service served on port `8081` returning connected components, centrality weights, fan-in/fan-out metrics, and cyclic loops.
* **Reporting Microservice:** Decoupled PDF engine served on port `8082` executing ReportLab layout assemblies to build suspicious activity report downloads.
* **JWT-Based RBAC Permissions:** Decorator checks restricting access levels based on user roles (`ADMIN`, `ANALYST`, `INVESTIGATOR`, `VIEWER`).
* **Authentication Rate Limiting:** 10 requests per minute limit per client IP address applied to `/api/auth/login` and `/api/auth/signup`.
* **CORS Origin Whitelists:** Enforces configurable domain whitelists for cross-origin security, defaulting to localhost origins in development.
* **Exception Call Masking:** Suppresses internal traceback stack logs in production mode HTTP 500 error responses.
* **MLOps Model Registry:** Database registry allowing model registration, metrics logs, deployment comparison, and automated fallback rollbacks.
* **Microservice Container Orchestration:** Docker-Compose stack configs and Kubernetes YAML manifests (`k8s/all.yaml`) mapping name-spaces, HPA scaling, limits, and probes.

---

## 🔬 V2 EXPERIMENTAL

These features exist as experimental code, evaluation pipelines, or metrics-monitoring routines and are not wired to block active production requests:
* **Graph Neural Network (GNN) Cosine Split Pipeline:** message-passing node classification experiments implemented inside [`modeling/gnn_experiment.py`](file:///a:/Projects/PSB/modeling/gnn_experiment.py).
* **Population Stability Index (PSI) Drift Engine:** Statistical score evaluation comparing production telemetry distributions against reference baselines.
* **Kolmogorov-Smirnov (K-S) Drift Engine:** Feature-level p-value checks ($p < 0.05$) to monitor data distribution shifts.

---

## 🎭 V2 SIMULATED

These features provide realistic user experience mockups for analyst workflows but have **no** external production integrations:
* **CBS Emergency Debit Freeze:** Mock action button returning custom transaction IDs and simulation confirmations with zero live core banking connections.
* **Regulatory Intelligence Lookups:** Sandbox cross-referencing lookups againstRBI Caution list, I4C portal, and CERT-In records using static database matches.
* **FIU-IND STR Report Drafts:** Suspicious activity reports output in raw text summaries compliant with India's PMLA requirements.

---

## 🔮 V3 / FUTURE ROADMAP

These architecture components are planned as future improvements:
* **Apache Kafka Streaming Bus:** Full pipeline event streaming integration to capture real-time banking ledger feeds (Kubernetes manifests contain stubs).
* **Live Core Banking (CBS) Connectors:** True REST/gRPC database integrations with commercial public sector banking hosts.
* **GNN Production Integration:** Deploying a live GNN model in parallel to standard XGBoost to evaluate graph attributes on active accounts.
