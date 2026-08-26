# 🗺️ MuleShield PRO V2 — Product & Engineering Roadmap

This document outlines the product evolution strategy and engineering roadmap for **MuleShield PRO V2**, separating existing baseline capabilities from planned future enterprise features.

---

## 🏛️ 1. Capabilities Classification Matrix

The platform's capabilities are organized into four classifications:

| Capability / Feature | Classification | Engineering Scope / Reference |
| :--- | :--- | :--- |
| **XGBoost Inference Engine** | `IMPLEMENTED` | Loads `mule_shield_model.json` to score account risk. |
| **Target Leakage Preprocessor** | `IMPLEMENTED` | Drops 14 leaking fields via `preprocessor.pkl`. |
| **TreeSHAP Attributions** | `IMPLEMENTED` | Maps feature contribution weights to descriptors. |
| **SQL Database Foundation** | `IMPLEMENTED` | PostgreSQL support using SQLAlchemy models & repositories. |
| **PDF Document Compiler** | `IMPLEMENTED` | ReportLab PDF case report compiler. |
| **Ad-Hoc Evaluation Sandbox** | `EXPERIMENTAL` | Evaluates inputs via standard forms or JSON payloads. |
| **CBS Debit Freeze Webhook** | `SIMULATED` | Simulated core banking debit freeze with webhook returns. |
| **Regulatory Watchlists** | `SIMULATED` | Mock hits against I4C and RBI caution tables. |
| **Mule Ring Topology Graph** | `SIMULATED` | Illustrative 2D multi-hop fund routing network graph. |
| **GNN Ring Classifiers** | `PLANNED` | Graph Neural Networks to detect multi-hop groupings. |
| **Kafka Ingestion Pipeline** | `PLANNED` | High-throughput distributed ledger streaming. |
| **SSO / MFA Identity Gate** | `PLANNED` | SAML/OIDC identity management integration. |

---

## 📅 2. Implementation Phase Plan

```
  PHASE 0: BASELINE ──► PHASE 1: DATABASE ──► PHASE 2: TELEMETRY ──► PHASE 3: ADVANCED DETECT
  Establish V2 branch   SQLAlchemy Models     Celery Ingestion        GNN Graph Classifiers
  Sealing ML Assets     PostgreSQL Support    Redis Caching           Kafka Streaming
```

### **Phase 0: Baseline & Version Control (Current Phase)**
* **Objective:** Establish the `v2-development` workspace branch from the stable V1 production base.
* **Scope:** Seal all verified machine learning weights (`mule_shield_model.json`), preprocessing pipelines (`preprocessor.pkl`), and calibration thresholds (`0.9899`).

### **Phase 1: Database Foundation & Service Decoupling (Current Phase)**
* **Objective:** Replace temporary in-memory database mocks with a structured relational database layer.
* **Scope:** Implement SQLAlchemy models for `users`, `roles`, `accounts`, `cases`, `risk_predictions`, `shap_explanations`, `investigation_events`, and `audit_logs`. Build the repository query layers.

### **Phase 2: High-Performance Ingestion & Streaming (Planned)**
* **Objective:** Transition ad-hoc API scoring into a decoupled event processing pipeline.
* **Scope:** Introduce **Celery** task queues and **Redis** cache clusters to compute TreeSHAP explanations asynchronously without blocking web requests.

### **Phase 3: Graph Intelligence & Enterprise Security (Planned)**
* **Objective:** Automate network detection and secure banking access control.
* **Scope:** Replace illustrative ring maps with active GNN model inferences, and integrate Okta/Keycloak OAuth2 single sign-on gates.
