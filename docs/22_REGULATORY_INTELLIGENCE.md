# 🏛️ 22 — REGULATORY INTELLIGENCE & WATCHLISTS

---

## 1. Regulatory Intelligence Overview

MuleShield PRO integrates a dedicated **Regulatory Intelligence** tab (Tab 4) on the Analyst Dashboard to demonstrate how cross-agency government cyber-fraud feeds and central bank caution lists intersect with ML transaction classification.

---

## 2. Integrated Watchlist Databases

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                       REGULATORY WATCHLIST INTEGRATION SUMMARY                            │
├───────────────────────────────┬───────────────────────────────┬───────────────────────────┤
│ Watchlist Feed                │ Simulated Integration Status  │ Current Match Metric      │
├───────────────────────────────┼───────────────────────────────┼───────────────────────────┤
│ I4C Cyber Fraud DB            │ CONNECTED (Simulated Index)   │ 87 Mule Account Matches   │
│ CERT-In Botnet Feed           │ ACTIVE (Simulated Index)      │ 0 Botnet IP Matches       │
│ RBI Caution List              │ ACTIVE (Simulated Index)      │ 87 Watchlist Hits         │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────┘
```

### Feed Details:
1. **I4C Cyber Fraud DB (Indian Cyber Crime Coordination Centre):** Cross-references national cyber-crime portal tickets against bank account numbers.
2. **CERT-In Botnet Feed (Indian Computer Emergency Response Team):** Tracks compromised IP addresses associated with malware and mobile banking trojans.
3. **RBI Caution List:** Monitors high-risk entities and director DINs flagged by the Reserve Bank of India.

---

## 3. Data Flow & Search Capabilities

* **Interactive Search Filter:** Analysts can search accounts by Account ID or match status directly in Tab 4.
* **Account Card Intersections:** Accounts flagged as `Critical` by the XGBoost ML model show matching `FLAGGED` status badges against I4C and RBI lists, providing multi-source verification.

---

## 4. Scope Disclaimer

* **Implemented Feature:** Simulated in-memory database index ([backend/db.py](file:///a:/Projects/PSB/backend/db.py)) returning watchlist statuses via `/api/cases/<id>`.
* **Future Production Scope:** Live REST/gRPC API webhooks connecting directly to national government cyber portals.
