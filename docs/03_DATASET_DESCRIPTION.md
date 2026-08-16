# 📊 03 — DATASET DESCRIPTION & SCHEMA MAP

---

## 1. Dataset Overview

* **Primary Dataset Filename:** `data_copy.csv` (Located in workspace root)
* **Dataset Size:** `111.14 MB` (Uncompressed)
* **Total Rows (Account Profiles):** `9,082` rows
* **Total Columns:** `3,925` columns (3,924 input features + 1 target column `F3924`)
* **Target Column:** `F3924` (`FRAUD_TGT`)
* **Positive Class (`F3924 = 1`):** Flagged Mule / Fraudulent Account
* **Negative Class (`F3924 = 0`):** Legitimate / Non-Mule Account

---

## 2. Class Distribution

```
Target Distribution (F3924):
─────────────────────────────────────────────────────────────
Class 0 (Legitimate Non-Mule):  9,001 accounts (99.1081%)
Class 1 (Mule / Fraud):            81 accounts ( 0.8919%)
─────────────────────────────────────────────────────────────
Total Evaluated:                9,082 accounts (100.0000%)
Class Imbalance Ratio:         111.12 to 1 (Extreme Imbalance)
```

---

## 3. What One Row Represents

Each row in `data_copy.csv` represents a **single aggregated financial account profile** evaluated as of a specific alert evaluation date. The features contain historical transaction counts, transaction volume averages, deviation metrics across time windows (7D, 14D, 31D), demographic categories, and alert frequency indicators.

---

## 4. Feature Taxonomy & Categorization (`Description.xlsx`)

The organizers released an official column dictionary (`Description.xlsx` — 3,924 rows). The feature set spans five primary operational banking domains:

```
                                  ┌───────────────────────────────────────────────────────────┐
                                  │            FEATURE TAXONOMY (3,924 RAW FEATURES)          │
                                  └─────────────────────────────┬─────────────────────────────┘
                                                                │
         ┌──────────────────────┬───────────────────────────────┼──────────────────────────────┬──────────────────────┐
         ▼                      ▼                               ▼                              ▼                      ▼
┌──────────────────┐  ┌──────────────────┐            ┌──────────────────┐           ┌──────────────────┐   ┌──────────────────┐
│ TRANSACTION      │  │ DEVIATION RATIOS │            │ DEMOGRAPHICS     │           │ ALERT FREQUENCY  │   │ POST-INCIDENT    │
│ COUNTS & AMOUNTS │  │ (D_*, DA_*, R_*) │            │ & ACCOUNT METRICS│           │ & INCIDENT SCORES│   │ RESOLUTION FLAGS │
│ (F1 - F2122)     │  │ (F2123 - F3885)  │            │ (F3886 - F3896)  │           │ (F3897 - F3923)  │   │ (F3898 - F3915)  │
└──────────────────┘  └──────────────────┘            └──────────────────┘           └──────────────────┘   └──────────────────┘
```

### Detailed Category Breakdown:

1. **Transaction Counts & Volumes (`F1` to `F2122`):**
   * Metrics across channels: Cash, Cheque, UPI, NetBanking, Electronic Transfer (IMPS/NEFT/RTGS).
   * Aggregations computed across time windows: `L7D` (Last 7 Days), `L14D` (Last 14 Days), `L31D` (Last 31 Days), `L7_14D`, `L14_31D`.
2. **Deviation & Ratio Features (`F2123` to `F3885`):**
   * Ratios of customer-induced non-cash/cheque credit vs debit transactions (`RA_CI_NON_CASH_CHQ_*`).
   * Deviations of account balance from occupation segment averages (`D_AVG_BAL_*_OCC`).
3. **Account Demographics & Profile Attributes (`F3886` to `F3896`):**
   * Categorical features: `PRODUCT_NAME` (`F3886`), `AREA_CATEGORY` (`F3890`), `CUST_OCCP` (`F3891`), `GENDER` (`F3892`), `SEGMENTATION_CLASS` (`F3893`).
   * Numerical demographics: `TENURE_AS_OF_ALERT` (`F3887`), `ACCT_OPN_DAYS` (`F3889`), `AGE_IN_YRS` (`F3894`), `MIN_INC_SCORE` (`F3895`), `MAX_INC_SCORE` (`F3896`).
4. **Alert Description Flags (`F3900` to `F3911`, `F3919` to `F3923`):**
   * Specific alert trigger flags: `HIGH_VALUE_UPI_DB_TXNS` (`F3900`), `MULTI_DBS_FROM_ACCOUNT` (`F3901`), `PWD_CHANGED_LARGE_FUND_XFERS` (`F3903`), `RCVING_FUNDS_FROM_MULITPLE_USERS` (`F3904`), `STATUS_CHANGE_AFTER_WD` (`F3906`), `TXN_AT_UNUSUAL_TIME` (`F3907`).
   * Time-of-day alert counts: `MORNING_ALERTS` (`F3920`), `AFTERNOON_ALERTS` (`F3921`), `EVENING_ALERTS` (`F3922`), `NIGHT_ALERTS` (`F3923`).
5. **Post-Incident Resolution Flags (LEAKAGE — PURGED):**
   * `MIN_RESOLVE_DAYS` (`F3898`), `MAX_RESOLVE_DAYS` (`F3899`), `FRAUD_SUSPECTED` (`F3912`), `OTHER_RESOLUTION` (`F3913`), `FALSE_POSITIVE` (`F3914`), `UNATTENDED` (`F3915`).

---

## 5. Dataset Scope & Evaluation Hierarchy

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. TRAINING DATASET (data_copy.csv — 9,082 rows)                                           │
│    • Ground truth label F3924 available during supervised training.                       │
│    • Used to fit preprocessor.pkl, SMOTE oversampling, and train XGBoost weights.         │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. INTERNAL CV VALIDATION (5-Fold Group-Aware CV)                                         │
│    • 6,118 group clusters isolated via >0.99 cosine similarity.                           │
│    • Used to tune max_depth=3, L1/L2 regularization, and decision threshold (0.9899).     │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. HIDDEN ORGANIZER VALIDATION DATASET (UNSEEN / NOT SHARED)                              │
│    • Held privately by hackathon judges for final evaluation.                             │
│    • Model receives NO target labels during inference; relies purely on generalization.     │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```
