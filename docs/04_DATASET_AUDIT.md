# 🔬 04 — DATASET AUDIT & QUALITY METRICS

---

## 1. Data Quality Overview

A complete statistical audit was conducted on `data_copy.csv` (9,082 account profiles by 3,924 input features).

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                              DATASET QUALITY AUDIT SUMMARY                                │
├───────────────────────────────┬───────────────────────────────────────────────────────────┤
│ Audit Metric                  │ Verified Audit Value                                      │
├───────────────────────────────┼───────────────────────────────────────────────────────────┤
│ Total Rows                    │ 9,082 accounts                                            │
│ Total Features                │ 3,924 raw input features                                  │
│ Target Column                 │ F3924 (FRAUD_TGT)                                         │
│ Positive Class (Fraud)        │ 81 accounts (0.8919%)                                     │
│ Negative Class (Non-Fraud)    │ 9,001 accounts (99.1081%)                                 │
│ Zero-Variance Columns         │ 0 columns in preprocessed matrix                          │
│ Near-Duplicate Clusters (>0.99)│ 6,118 distinct account clusters across 9,082 rows         │
│ Post-Incident Leakage Flags   │ 12 columns purged (6 base flags + 6 missingness flags)    │
│ Date Proxy Columns            │ 2 base columns purged (F2230, F3888)                      │
│ Final Sanitized Feature Count │ 6,820 aligned features                                    │
└───────────────────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 2. Missing Value Analysis

* **Numerical Features ($\le 70\%$ Missingness):** Imputed dynamically using feature medians computed from training folds. Missingness flags (`_ismissing`) appended to preserve missingness signals.
* **Sparse Numerical Features ($> 70\%$ Missingness):** Imputed with sentinel value `$-9999$`.
* **Categorical Features:** One-hot encoded via `pd.get_dummies(dummy_na=True, drop_first=True)` to convert missing categories into distinct binary indicator columns.

---

## 3. Near-Duplicate Account Clustering Audit

Pairwise cosine-similarity analysis was performed across all 9,082 rows using normalized numerical feature matrices (`l2` norm):
* **Similarity Threshold:** $> 0.99$ cosine similarity.
* **Connected Components Identified:** 6,118 distinct account clusters.
* **Duplicate Contamination Risk:** In standard K-Fold splitting, synthetic near-duplicate accounts are split across training and validation folds, causing severe metric inflation. MuleShield PRO enforces **Stratified Group K-Fold** splitting on these 6,118 group IDs to guarantee zero cross-fold duplicate contamination.

---

## 4. Outlier Handling (Winsorization Audit)

Financial transaction volumes exhibit extreme long-tailed distributions (e.g. single massive RTGS transfers). To prevent extreme outliers from distorting XGBoost histogram split bins:
* **Quantile Clipping:** 1st percentile (`0.01`) and 99th percentile (`0.99`) bounds calculated on training folds and serialized in `preprocessor.pkl`.
* **Inference Clipping:** `X_df[c].clip(lower=lower, upper=upper)` applied dynamically during evaluation.

---

## 5. Summary of Purged Features

```
Purged Leakage Feature Inventory:
───────────────────────────────────────────────────────────────────────────────────────────
1. F3898 / F3898_ismissing  : MIN_RESOLVE_DAYS (Min alert resolution days)
2. F3899 / F3899_ismissing  : MAX_RESOLVE_DAYS (Max alert resolution days)
3. F3912 / F3912_ismissing  : FRAUD_SUSPECTED (Resolution status flag — 0.9753 correlation)
4. F3913 / F3913_ismissing  : OTHER_RESOLUTION (Resolution status flag)
5. F3914 / F3914_ismissing  : FALSE_POSITIVE (Resolution status flag)
6. F3915 / F3915_ismissing  : UNATTENDED (Resolution status flag)
7. F2230                     : ALERT_DATE (Temporal date proxy)
8. F3888                     : ACCT_OPN_DATE (Account opening date proxy)
───────────────────────────────────────────────────────────────────────────────────────────
Total Feature Reduction: 3,924 raw features → 6,820 preprocessed & aligned features.
```
