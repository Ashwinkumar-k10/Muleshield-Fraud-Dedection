# 🛡️ 27 — SECURITY, AUDITABILITY & BANKING COMPLIANCE

---

## 1. Compliance Matrix (RBI & FIU-IND)

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           REGULATORY COMPLIANCE AUDIT MATRIX                              │
├───────────────────────────────┬───────────────────────────────┬───────────────────────────┤
│ Regulatory Authority          │ Compliance Requirement        │ Implemented Mechanism     │
├───────────────────────────────┼───────────────────────────────┼───────────────────────────┤
│ Reserve Bank of India (RBI)   │ Model Explainability & Audit  │ TreeSHAP feature impact   │
│ FIU-India (PMLA Sec 12)       │ STR Report Filing             │ Automated STR draft text  │
│ Public Sector Banks (PSBs)    │ Minimizing False Debit Lock   │ Calibrated threshold 0.9899│
│ Data Privacy Standards        │ Pre-Anonymized Dataset Feature │ Pre-anonymized column IDs │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────┘
```

---

## 2. PII & Data Privacy Handling

MuleShield PRO operates exclusively on pre-anonymized feature IDs supplied in the dataset (`F1`-`F3924`) and performs no customer re-identification or PII processing. In a live production environment, customer PII (such as PAN, Aadhaar, name, and address) would be tokenized prior to ingestion into the risk engine.

---

## 3. Scope Distinction: Implemented Prototype vs. Production Security Controls

| Security Dimension | Implemented Prototype | Future Production System |
| :--- | :--- | :--- |
| **Authentication** | Local HTTP development access. | OAuth2 / JWT authentication with Role-Based Access Control (RBAC). |
| **API Security** | Local CORS enabled (`Flask-CORS`). | TLS 1.3 encryption, API rate limiting, and mTLS for bank microservices. |
| **Data Privacy** | Pre-anonymized feature columns (`F1`-`F3924`). | HSM (Hardware Security Module) tokenization of customer PAN/Aadhaar. |
| **Audit Logging** | File-based STR drafts (`backend/storage/`). | Immutable append-only audit log database (PostgreSQL / HashiCorp Vault). |
