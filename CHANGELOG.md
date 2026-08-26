# Changelog

All notable changes to the **MuleShield PRO** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-08-26

### Added
- **Microservices Migration (Phase 13):**
  - Switched monolith into 4 decoupled, independent services: API Gateway (`main.py`), ML Inference Service (`inference_service.py`), Graph Service (`services/graph_service.py`), and Reporting Service (`services/reporting_service.py`).
  - Added multi-container `docker-compose.yml` for unified microservice startup.
  - Added Kubernetes deployment manifests (`k8s/all.yaml`) featuring resource limits, readiness/liveness health probes, ConfigMaps, Secret variables, and Horizontal Pod Autoscalers (HPA).
- **Security Hardening (Phase 14):**
  - Added secure password hashing (`werkzeug.security`) replacing plain SHA-256 with strong, salted `scrypt` hashing.
  - Added role restrictions on the public signup endpoint (`/api/auth/signup`) to prevent unauthorized users from registering as `ADMIN` or `INVESTIGATOR`.
  - Added in-memory API Rate Limiting (10 requests/minute per client IP) on sensitive authentication endpoints.
  - Added dynamic CORS origin checks restricting access in production using environment variables.
  - Added exception handling to mask raw traceback exception strings from database/API failures in production mode HTTP 500 responses.
  - Added security warning triggers on startup if a default/fallback secret JWT key is loaded in a production environment.
- **System Validation Suite (Phase 15):**
  - Added new integration unit tests in `tests/test_rbac.py` validating rate limiting, signup role checks, and JWT validations.
  - Formulated a comprehensive sitemap and feature classification report (`docs/V2_SYSTEM_VALIDATION.md`).

---

## [1.0.0] - 2026-08-23

### Added
- **Core ML Engine:**
  - Standard XGBoost classifier champion model trained on 9,082 rows.
  - Custom data preprocessor transformer (`preprocessor.py`).
  - 14-column target leakage purge filter (removing human-remediating flags like `F3898`, `F3914`, etc.).
  - 5-Fold Stratified Connected-Component Group Cross-Validation framework to handle similarity clustering leakage.
- **Analyst Interface:**
  - Single-page dashboard featuring 5 responsive views (Cases queue, Anomaly Sandbox, Mule Ring Vis.js topology, Regulatory watchlist alerts, and Operations Audit Trail).
  - Mock CBS debit freeze button.
  - FIU-IND compliance STR text report draft generator.
- **Comprehensive Documentation:**
  - 32 core manuals and 4 technical reports auditing model training, generalize metrics, and codebases.
