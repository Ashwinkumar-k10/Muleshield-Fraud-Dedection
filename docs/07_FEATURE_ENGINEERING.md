# ⚙️ 07 — FEATURE ENGINEERING PIPELINE

---

## 1. Domain Feature Engineering Overview

Feature engineering in MuleShield PRO derives banking domain ratios directly from raw transaction columns identified in `Description.xlsx`. No external or unavailable data is invented.

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                      ENGINEERED BANKING DOMAIN RATIO FEATURES                             │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐
│ BANK_FE_CASH_TO_UPI_RATIO   │  │ BANK_FE_UPI_TO_TOTAL_DEV    │  │ BANK_FE_TENURE_AGE_RATIO    │
│ F2122 / (F670.abs() + 1.0)  │  │ F2582 / (F2737.abs() + 1.0) │  │ F3887 / (F3894.abs() + 1.0) │
└─────────────────────────────┘  └─────────────────────────────┘  └─────────────────────────────┘
```

---

## 2. Inventory of Engineered Features

### 1. `BANK_FE_CASH_TO_UPI_RATIO`
* **Source Columns:** `F2122` (`AVG_CASH_TXNS_L31D` — Average Cash Transaction Count) and `F670` (`MIN_UPI_XFER_TXNS_L7D` — Min UPI Total Txns).
* **Formula:** $\text{BANK\_FE\_CASH\_TO\_UPI\_RATIO} = \frac{\text{F2122}}{|\text{F670}| + 1.0}$
* **Banking Domain Meaning:** Measures the ratio of cash debit withdrawals relative to digital UPI inflows.
* **Why Useful for Mule Detection:** Mule accounts frequently receive large digital UPI inflows which are rapidly drained via cash ATM withdrawals to break the digital audit trail.

---

### 2. `BANK_FE_UPI_TO_TOTAL_DEV_RATIO`
* **Source Columns:** `F2582` (`DA_UPI_TXN_CR_L7_14D` — Deviation of averages of UPI Total Amount) and `F2737` (`DA_NON_CASH_CHQ_AMT_L7_31D` — Deviation of Non-Cash Non-Cheque Amount).
* **Formula:** $\text{BANK\_FE\_UPI\_TO\_TOTAL\_DEV\_RATIO} = \frac{\text{F2582}}{|\text{F2737}| + 1.0}$
* **Banking Domain Meaning:** Evaluates UPI credit volume deviation relative to overall account deviation.
* **Why Useful for Mule Detection:** Sudden velocity spikes specifically in digital UPI credits (compared to normal account history) are strong indicators of scam fund-layering.

---

### 3. `BANK_FE_TENURE_AGE_RATIO`
* **Source Columns:** `F3887` (`TENURE_AS_OF_ALERT` — Customer tenure with bank) and `F3894` (`AGE_IN_YRS` — Customer age as of alert date).
* **Formula:** $\text{BANK\_FE\_TENURE\_AGE\_RATIO} = \frac{\text{F3887}}{|\text{F3894}| + 1.0}$
* **Banking Domain Meaning:** Computes customer bank account tenure relative to customer age.
* **Why Useful for Mule Detection:** Highlights newly opened accounts held by young individuals, a demographic frequently targeted by fraud syndicates for mule recruitment.

---

## 3. Implementation in Code

The feature engineering transformations are implemented directly in `MuleShieldPreprocessor.transform()` ([modeling/preprocessor.py](file:///a:/Projects/PSB/modeling/preprocessor.py)):

```python
# Domain Feature Engineering
if 'F2122' in X_df.columns and 'F670' in X_df.columns:
    X_df['BANK_FE_CASH_TO_UPI_RATIO'] = X_df['F2122'] / (X_df['F670'].abs() + 1.0)
if 'F2582' in X_df.columns and 'F2737' in X_df.columns:
    X_df['BANK_FE_UPI_TO_TOTAL_DEV_RATIO'] = X_df['F2582'] / (X_df['F2737'].abs() + 1.0)
if 'F3887' in X_df.columns and 'F3894' in X_df.columns:
    X_df['BANK_FE_TENURE_AGE_RATIO'] = X_df['F3887'] / (X_df['F3894'].abs() + 1.0)
```
