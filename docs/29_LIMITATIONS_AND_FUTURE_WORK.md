# ⚠️ 29 — LIMITATIONS & FUTURE ROADMAP

---

## 1. Prototype Limitations

1. **Unseen Validation Uncertainty:** While internal 5-fold group cross-validation yields **`0.8807 ± 0.0403` PR-AUC**, performance on the organizer's private, hidden validation dataset remains unknown until evaluation.
2. **Tabular Dataset Structure:** The provided dataset (`data_copy.csv`) lacks explicit sender-receiver counterparty transaction linkage columns, necessitating the use of simulated data for the Mule Ring network visualization tab.
3. **Mock Operational Actions:** The **Confirm CBS Debit Freeze** button and regulatory intelligence feeds function as simulated in-memory UI demonstrations.

---

## 2. Production Enhancement Roadmap

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                              FUTURE PRODUCTION ROADMAP                                    │
└─────────────────────────────┬─────────────────────────────┬───────────────────────────────┘
                              │                             │
                              ▼                             ▼
               ┌─────────────────────────────┐┌─────────────────────────────┐
               │    REAL-TIME STREAMING      ││     GRAPH NEURAL NETWORK    │
               │ Apache Kafka ingestion of   ││ GNN (Heterogeneous Graph)   │
               │ ISO 20022 payment streams.  ││ for link prediction.        │
               └─────────────────────────────┘└─────────────────────────────┘
                              │                             │
                              ▼                             ▼
               ┌─────────────────────────────┐┌─────────────────────────────┐
               │  LIVE CORE BANKING APIS     ││   I4C REGULATORY WEBHOOKS   │
               │ Direct Finacle / BaNCS REST ││ Live bidirectional sync     │
               │ webhook debit freeze.       ││ with National Cyber Portal. │
               └─────────────────────────────┘└─────────────────────────────┘
```
