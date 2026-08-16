# 📈 12 — MODEL EVALUATION & METRIC BENCHMARKS

---

## 1. Verified Model Performance Metrics

All cross-validation evaluation metrics reported in MuleShield PRO are derived from 5-Fold Group-Aware Cross-Validation on sanitized, leakage-free feature matrices:

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                     5-FOLD GROUP-AWARE CROSS-VALIDATION BENCHMARKS                        │
├───────────────────────────────────────────────┬───────────────────────────────────────────┤
│ Metric                                        │ Verified CV Value (Mean ± Std)            │
├───────────────────────────────────────────────┼───────────────────────────────────────────┤
│ PR-AUC (Precision-Recall Area Under Curve)    │ 0.8807 ± 0.0403                           │
│ Champion Config PR-AUC                        │ 0.8833 ± 0.0365                           │
│ Precision (Validation Folds)                  │ 1.0000 (100.0% Precision on validation)   │
│ Recall (Validation Folds)                     │ 0.6164 (61.64% Fraud Recall)              │
│ F1-Score (Validation Folds)                   │ 0.7586                                     │
│ Calibrated Decision Threshold                 │ 0.9899                                     │
└───────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

## 2. 3-Model Baseline Comparison Table

To confirm XGBoost as the champion architecture, Logistic Regression and Random Forest were evaluated across identical 5-Fold Group-Aware CV splits:

| Model Architecture | PR-AUC (Mean ± Std) | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost Classifier (CHAMPION)** | **`0.8807 ± 0.0403`** | **`1.0000`** | **`0.6164`** | **`0.7586`** | **SELECTED CHAMPION** |
| **Random Forest Classifier** | `0.7845 ± 0.1001` | `0.9770` | `0.4033` | `0.5539` | Rejected (Lower Recall) |
| **Logistic Regression** | `0.6652 ± 0.1035` | `0.7058` | `0.6037` | `0.6447` | Rejected (Lower Precision) |

### Key Observations:
1. **XGBoost Outperforms Random Forest:** Beats Random Forest by **+9.62% in PR-AUC** and **+21.31% in Recall**, proving gradient boosting's superiority in identifying subtle fraud signals.
2. **XGBoost Outperforms Logistic Regression:** Outperforms Logistic Regression by **+21.55% in PR-AUC** and **+29.42% in Precision**, confirming that non-linear decision trees capture multi-feature transaction interactions that linear models miss.

---

## 3. In-Sample Full-Dataset Confusion Matrix at Threshold 0.9899

> [!NOTE]
> **IN-SAMPLE FULL-DATASET EVALUATION — NOT A GENERALIZATION METRIC:**  
> The confusion matrix below reflects full dataset inference evaluation ($9,082$ accounts) using the trained XGBoost binary at threshold `0.9899`. Out-of-fold generalization performance is represented by the 5-fold cross-validation metrics above ($0.8807 \pm 0.0403$ PR-AUC).

```
                       PREDICTED CLASS
                  Non-Mule (0)      Mule (1)
ACTUAL   Non-Mule (0)   9,000            1      (99.989% Specificity)
CLASS    Mule (1)         26            55      (67.901% Sensitivity)
```

* **True Positives (TP):** 55 mule accounts correctly identified and flagged.
* **True Negatives (TN):** 9,000 legitimate accounts correctly cleared.
* **False Positives (FP):** 1 legitimate account flagged (minimal false freeze rate).
* **False Negatives (FN):** 26 subtle mule accounts missed (addressed via secondary watchlist matching).

---

## 4. Performance Disclaimer

* **Cross-Validation Metrics:** Primary metrics reported above (`0.8807 ± 0.0403` PR-AUC) represent out-of-fold generalization performance across internal 5-fold splits.
* **Hidden Validation Disclaimer:** Performance on the organizer's private hidden validation dataset is **UNKNOWN** until official hackathon evaluation.
