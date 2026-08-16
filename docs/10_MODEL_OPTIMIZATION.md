# 🎛️ 10 — MODEL OPTIMIZATION & EXPERIMENTAL LOGS

---

## 1. Optimization Methodology

Model optimization in MuleShield PRO prioritized **generalization on unseen data** rather than optimistic training set fitting.

```
                                  ┌───────────────────────────────────────────────────────────┐
                                  │            OPTIMIZATION & HYPERPARAMETER SEARCH           │
                                  └─────────────────────────────┬─────────────────────────────┘
                                                                │
         ┌──────────────────────┬───────────────────────────────┼──────────────────────────────┬──────────────────────┐
         ▼                      ▼                               ▼                              ▼                      ▼
┌──────────────────┐  ┌──────────────────┐            ┌──────────────────┐           ┌──────────────────┐   ┌──────────────────┐
│ BASELINE AUDIT   │  │ PURGE LEAKAGE    │            │ CLASS IMBALANCE  │           │ REGULARIZATION   │   │ THRESHOLD        │
│ Identify Post-   │  │ Drop F3912,      │            │ Benchmark SMOTE, │           │ Tune max_depth=3,│   │ CALIBRATION      │
│ Incident Flags   │  │ Date Proxies     │            │ ADASYN, PosWeight│           │ L1/L2 Penalties  │   │ Tune to 0.9899   │
└──────────────────┘  └──────────────────┘            └──────────────────┘           └──────────────────┘   └──────────────────┘
```

---

## 2. Experimental Hyperparameter Configurations & Results

Four hyperparameter grid configurations were evaluated across 5-Fold Group-Aware Cross-Validation ([scripts/optimize_pipeline_final.py](file:///a:/Projects/PSB/scripts/optimize_pipeline_final.py)):

| Config ID | `max_depth` | `min_child` | `gamma` | `subsample` | `colsample` | L1 (`alpha`) | L2 (`lambda`) | Learning Rate | PR-AUC (Mean ± Std) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Config #1** | **`3`** | **`3`** | **`0.1`** | **`0.8`** | **`0.8`** | **`0.1`** | **`1.0`** | **`0.05`** | **`0.8833 ± 0.0365`** | **CHAMPION (Selected)** |
| Config #2 | `4` | `5` | `0.2` | `0.7` | `0.7` | `0.5` | `2.0` | `0.03` | `0.8474 ± 0.0408` | Rejected (Lower PR-AUC) |
| Config #3 | `3` | `5` | `0.5` | `0.8` | `0.7` | `1.0` | `3.0` | `0.03` | `0.8732 ± 0.0353` | Rejected (Over-regularized) |
| Config #4 | `2` | `3` | `0.0` | `0.8` | `0.8` | `0.0` | `1.0` | `0.05` | `0.8403 ± 0.0434` | Rejected (Underfitted) |

> [!NOTE]
> **Hyperparameter Search Champion vs. Final Serialized Model Metric:**  
> Config #1 represents the **Hyperparameter Search Champion** experiment result obtained during grid-search tuning (`0.8833 ± 0.0365` PR-AUC). The **Final Serialized / Verified Model** achieves **`0.8807 ± 0.0403` PR-AUC** under full out-of-fold 5-fold group cross-validation benchmarking across the sanitized dataset.

---

## 3. Analysis of Optimization Choices

1. **Tree Depth Constraints (`max_depth = 3`):**
   * Constraining tree depth to 3 levels prevents the model from splitting on rare noise patterns in the training data, ensuring robust feature attribution on unseen test sets.
2. **Elastic Net Regularization (`reg_alpha = 0.1`, `reg_lambda = 1.0`):**
   * L1 regularization zeroes out noisy feature weights across the 6,820 feature space, while L2 regularization prevents extreme probability score spikes.
3. **Stochastic Sampling (`subsample = 0.8`, `colsample_bytree = 0.8`):**
   * Subsampling 80% of rows and features per tree forces the ensemble to build diverse decision trees rather than over-relying on a small subset of dominant features.

---

## 4. Final Saved Model Artifacts

* **Native Model Binary:** [modeling/mule_shield_model.json](file:///a:/Projects/PSB/modeling/mule_shield_model.json)
* **Preprocessed Pipeline:** [modeling/preprocessor.pkl](file:///a:/Projects/PSB/modeling/preprocessor.pkl)
* **Feature Schema:** [modeling/feature_schema.json](file:///a:/Projects/PSB/modeling/feature_schema.json)
* **Config File:** [modeling/model_config.json](file:///a:/Projects/PSB/modeling/model_config.json)
