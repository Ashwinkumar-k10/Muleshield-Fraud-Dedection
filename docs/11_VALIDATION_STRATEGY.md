# 🔬 11 — VALIDATION STRATEGY & ZERO-LEAKAGE FRAMEWORK
**PASS — Meets Industry Standard**

---

## 1. Why Standard Random Splitting Fails

In financial transaction datasets, near-duplicate account profiles exist due to duplicate alerts, recurring transfer structures, or near-identical customer attributes.

If standard **Random K-Fold Cross-Validation** or **Train-Test Splitting** is applied:
1. Near-duplicate account profiles end up split across both training and validation folds.
2. The model "memorizes" the training duplicate and scores high on the validation duplicate.
3. Cross-validation metrics appear deceptively high ($>99\%$ Precision/Recall), but performance collapses when deployed on an unseen hidden dataset.

---

## 2. 5-Fold Stratified Group K-Fold Cross-Validation

MuleShield PRO implements a rigorous **5-Fold Stratified Group K-Fold Cross-Validation** framework:

```
                                  ┌───────────────────────────────────────────────────────────┐
                                  │           PAIRWISE COSINE SIMILARITY CLUSTERING           │
                                  │      Computes similarity matrix on normalized features     │
                                  └─────────────────────────────┬─────────────────────────────┘
                                                                │ >0.99 Threshold
                                                                ▼
                                  ┌───────────────────────────────────────────────────────────┐
                                  │            6,118 CONNECTED COMPONENT GROUPS               │
                                  │        Groups near-duplicate account profiles together    │
                                  └─────────────────────────────┬─────────────────────────────┘
                                                                │ Enforce Group Isolation
                                                                ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           5-FOLD STRATIFIED GROUP CROSS-VALIDATION                        │
├───────────────┬───────────────────────────────┬───────────────────────────────┬───────────┤
│ Fold          │ Training Set                  │ Validation Set                │ Group ID  │
├───────────────┼───────────────────────────────┼───────────────────────────────┼───────────┤
│ Fold 1        │ Folds 2, 3, 4, 5 (80% Groups) │ Fold 1 (20% Unseen Groups)    │ Isolated  │
│ Fold 2        │ Folds 1, 3, 4, 5 (80% Groups) │ Fold 2 (20% Unseen Groups)    │ Isolated  │
│ Fold 3        │ Folds 1, 2, 4, 5 (80% Groups) │ Fold 3 (20% Unseen Groups)    │ Isolated  │
│ Fold 4        │ Folds 1, 2, 3, 5 (80% Groups) │ Fold 4 (20% Unseen Groups)    │ Isolated  │
│ Fold 5        │ Folds 1, 2, 3, 4 (80% Groups) │ Fold 5 (20% Unseen Groups)    │ Isolated  │
└───────────────┴───────────────────────────────┴───────────────────────────────┴───────────┘
```

---

## 3. Zero-Leakage Pipeline Rules

1. **Group Isolation:** Near-duplicate accounts belonging to the same cluster group ID are placed *exclusively* in either the training fold or the validation fold—never both.
2. **Train-Fold Preprocessing:** Quantile winsorization bounds (1st/99th percentiles) and median imputation values are calculated strictly on training folds.
3. **Train-Fold Resampling:** SMOTE minority oversampling is applied strictly to training folds. Validation folds remain 100% untouched.
4. **Train-Fold Threshold Calibration:** Precision-Recall curve threshold tuning is computed strictly inside training fold iterations.

---

## 4. Internal Validation vs. Hidden Organizer Validation

| Validation Tier | Dataset | Group Isolation | Purpose | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Internal CV** | `data_copy.csv` (9,082 rows) | Enforced (6,118 groups) | Hyperparameter tuning & threshold selection. | **`0.8807 ± 0.0403` PR-AUC** |
| **Organizer Hidden Set** | Private / Un-shared Dataset | Private | Final hackathon evaluation & ranking. | **UNKNOWN (Hidden Evaluation)** |
