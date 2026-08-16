# ⚙️ 05 — DATA PREPROCESSING PIPELINE

---

## 1. End-to-End Preprocessing Architecture

The preprocessing transformation pipeline is implemented in `MuleShieldPreprocessor` ([modeling/preprocessor.py](file:///a:/Projects/PSB/modeling/preprocessor.py)) and saved as a fitted binary object at [modeling/preprocessor.pkl](file:///a:/Projects/PSB/modeling/preprocessor.pkl).

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           PREPROCESSING TRANSFORM FLOW                                    │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │ Raw Input Matrix (X)
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. DATE PROXY & LEAKAGE SANITIZATION                                                       │
│    • Drops F2230 (ALERT_DATE) and F3888 (ACCT_OPN_DATE) date proxy columns.              │
│    • Drops F3898, F3899, F3912, F3913, F3914, F3915 post-incident resolution flags.        │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. DYNAMIC MISSINGNESS INDICATORS & IMPUTATION                                             │
│    • For features ≤70% missingness: appends _ismissing binary flag; imputes medians.      │
│    • For features >70% missingness: imputes sentinel -9999.                               │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. QUANTILE WINSORIZATION (OUTLIER CLIPPING)                                              │
│    • Clips extreme values to 1st (0.01) and 99th (0.99) quantiles stored during fit().   │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. CATEGORICAL ONE-HOT ENCODING                                                           │
│    • Encodes ['F3886', 'F3889', 'F3890', 'F3891', 'F3892', 'F3893'] via get_dummies().   │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. DOMAIN FEATURE RATIO ENGINEERING                                                        │
│    • Appends BANK_FE_CASH_TO_UPI_RATIO, BANK_FE_UPI_TO_TOTAL_DEV_RATIO, TENURE_AGE_RATIO.  │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. SCHEMA ALIGNMENT & REINDEXING                                                          │
│    • Reindexes against feature_schema.json (exact 6,820 feature columns alignment).       │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Training vs. Inference Consistency

To guarantee zero training-serving skew, the preprocessor executes identical logic during both model training and real-time inference:

| Processing Step | Training Execution | Inference Execution |
| :--- | :--- | :--- |
| **Quantile Bounds** | Computed from `X_train.quantile(0.01 / 0.99)` and stored in `self.percentiles_`. | Applied using stored quantiles: `X_df[c].clip(lower, upper)`. |
| **Feature Medians** | Computed from `X_train[c].median()` and stored in `self.medians_`. | Applied using stored medians: `X_df[c].fillna(self.medians_[c])`. |
| **Categorical Dummies** | Fit across categorical columns. | One-hot encoded and reindexed against stored schema `self.feature_columns_`. |
| **Column Schema** | Saved to [modeling/feature_schema.json](file:///a:/Projects/PSB/modeling/feature_schema.json). | Reindexed to exact 6,820 column order with `fill_value=0`. |

---

## 3. Artifact Dependencies

1. **`preprocessor.pkl`:** Serialized Scikit-Learn compatible transformer fitted on the training dataset.
2. **`feature_schema.json`:** JSON array containing exact order of all 6,820 input feature names.
3. **`model_config.json`:** Configuration file containing calibrated threshold (`0.9899`) and inverse class weight (`111.12`).
