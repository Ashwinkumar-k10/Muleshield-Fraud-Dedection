# MuleShield PRO — Enterprise AI/ML Mule Account & Fraud Layering Detection Platform
**PSB CyberShield Grand Finale 2026 Submission**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![XGBoost Champion](https://img.shields.io/badge/Model-XGBoost%20Classifier-emerald.svg)](modeling/mule_shield_model.json)
[![Validation Precision](https://img.shields.io/badge/Validation%20Precision-100%25-brightgreen.svg)](docs/12_MODEL_EVALUATION.md)
[![PR-AUC CV](https://img.shields.io/badge/PR--AUC-0.8807%20%C2%B1%200.0403-gold.svg)](docs/11_VALIDATION_STRATEGY.md)
[![Kubernetes Ready](https://img.shields.io/badge/K8s-Deployment--Ready-blue.svg)](docs/V2_KUBERNETES.md)
[![Security Hardened](https://img.shields.io/badge/Security-Hardened--scrypt-orange.svg)](docs/V2_SECURITY.md)

> **Executive Summary:** MuleShield PRO is an explainable AI-powered financial risk engine engineered specifically for Public Sector Banks (PSBs) to detect mule accounts, halt fraudulent fund-layering syndicates, and automate FIU-IND regulatory reporting in real time. Built upon an uncompromised, zero-leakage XGBoost classifier ($0.8807 \pm 0.0403$ PR-AUC across 5-Fold Group CV), MuleShield PRO delivers **100% Precision on validation folds** to eliminate false debit locks on legitimate banking customers while achieving rapid operational response.

---

## 🗺️ V2 Microservices & Deployment Architecture

MuleShield PRO has transitioned from a single monolithic local server to a fully decoupled microservices architecture prepared for Kubernetes scaling.

```
                                 MULESHIELD PRO V2 ARCHITECTURE
                                 
      [ Next.js Frontend ] ◄────────────────────────────────────────┐
      │  (Port 3000)       │                                        │
      └─────────┬──────────┘                                        │
                │                                                   │
                ▼                                                   ▼
     ┌──────────────────────┐   Role-Based Authorization   ┌────────────────┐
     │  API Gateway (Flask) │ ───────────────────────────► │  Auth Service  │
     │  (Port 8000)         │   (Analyst/Investigator/etc)│  (JWT + scrypt)│
     └────┬────┬────┬───────┘                              └────────────────┘
          │    │    │
          │    │    └─────────────────────────┐
          ▼    ▼                              ▼
     ┌──────────────┐ ┌────────────────┐ ┌───────────────────┐
     │ ML Inference │ │ Graph Database │ │ Reporting Service │
     │ Service (Pod)│ │ Service (Pod)  │ │ Service (Pod)     │
     │ (Port 8080)  │ │ (Port 8081)    │ │ (Port 8082)      │
     └────┬─────────┘ └───────┬────────┘ └────────┬──────────┘
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │  XGBoost  │       │ MuleGraph │       │ ReportLab │
    │ Classifier│       │ (Topology)│       │ PDF Engine│
    └───────────┘       └───────────┘       └───────────┘
```

---

## Quick Links & Navigation Index

| Resource Section | Direct Link | Key Technical Highlights |
| :--- | :--- | :--- |
| **V2 Release Index** | [`docs/V2_RELEASE.md`](docs/V2_RELEASE.md) | Release status categorizations (Implemented, Experimental, Simulated, Future). |
| **V2 System Validation** | [`docs/V2_SYSTEM_VALIDATION.md`](docs/V2_SYSTEM_VALIDATION.md) | Comprehensive integration check verification metrics. |
| **V2 Kubernetes Manifests** | [`docs/V2_KUBERNETES.md`](docs/V2_KUBERNETES.md) | Cluster setup, service specifications, ConfigMaps, HPAs, and rollbacks. |
| **V2 Security Controls** | [`docs/V2_SECURITY.md`](docs/V2_SECURITY.md) | Details rate-limiting, CORS setup, scrypt password hashing, and exception masking. |
| **Master Documentation Package** | [`docs/README.md`](docs/README.md) | 32 comprehensive architectural manuals & guides. |
| **Final Technical Report** | [`report/final_report.md`](report/final_report.md) | 6-section solution paper & forensic leak audit. |

---

## 🔒 Security Hardening (V2 Updates)
To meet enterprise public sector banking requirements, the platform has been hardened against common security vulnerabilities:
1. **Cryptographically Secure Passwords:** Upgraded plain SHA-256 storage to Werkzeug's `scrypt`/`pbkdf2` dynamic salting hashes (`generate_password_hash` / `check_password_hash`).
2. **Access Security (RBAC):** Prevents Privilege Escalation by restricting public signup `/api/auth/signup` to non-privileged roles (`ANALYST` or `VIEWER`). Administrative roles must be added via `/api/admin/users` by an authorized admin.
3. **Auth Rate Limiting:** Implemented an in-memory client IP rate limiter (10 requests per minute) on sensitive auth endpoints to block automated brute-force attacks.
4. **CORS Origin Control:** Replaced wildcard `*` CORS settings across all gateways and services with strict environment-variable whitelist restrictions.
5. **No Exception Disclosures:** Raw database exception stack traces are suppressed in production mode HTTP 500 responses and replaced with generic, secure notifications.

---

## Quick Start & Execution Guide

### 1. Launch with Docker Compose
To spin up the entire microservices stack (API Gateway, ML Inference, Graph Engine, Reporting, Frontend, Postgres, and Kafka stub):
```bash
docker-compose up --build
```
* Access the main API gateway at `http://localhost:8000`.
* Access the Next.js Frontend at `http://localhost:3000`.

### 2. Deploy to Kubernetes
Configure your target cluster credentials and apply the combined manifest file:
```bash
kubectl apply -f k8s/all.yaml
```
Verify pod readiness:
```bash
kubectl get pods -n muleshield-pro-v2
```

---

## Repository Structure Overview

```text
MuleShield-Fraud-Detection/
│
├── frontend/                      <-- Next.js Frontend Application
│   ├── app/                       <-- Dashboard tabs and layout
│   └── components/                <-- UI Nav, Float Copilot, and Vis.js Graph
│
├── backend/                       <-- Flask REST API Gateway & Microservices
│   ├── main.py                    <-- API Gateway host (port 8000)
│   ├── inference_service.py       <-- Decoupled ML Inference (port 8080)
│   ├── db.py                      <-- Case and Audit Log controller
│   ├── config.py                  <-- App configurations & security parameters
│   └── services/                  
│       ├── graph_service.py       <-- Graph Topology Microservice (port 8081)
│       └── reporting_service.py   <-- PDF report generation microservice (port 8082)
│
├── k8s/                           <-- Kubernetes Deployment Manifests
│   └── all.yaml                   <-- Unified namespace, config, deployments, and services
│
├── modeling/                      <-- Machine Learning Core
│   ├── preprocessor.py            <-- Preprocessor class implementation
│   ├── mule_shield_model.json     <-- Production XGBoost model
│   └── retrain_pipeline.py        <-- Controlled model retraining & MLOps MLDD pipeline
│
├── tests/                         <-- 49 Pass/Fail Verification Tests
│   ├── test_rbac.py               <-- Authentication, RBAC, and rate limit checks
│   ├── test_drift.py              <-- Feature & score drift calculations
│   └── test_mlops.py              <-- Model MLOps status promotion restrictions
│
├── CHANGELOG.md                   <-- Release history log
└── LICENSE                        <-- MIT License
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
