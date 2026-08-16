# ⚖️ 08 — CLASS IMBALANCE HANDLING STRATEGY

---

## 1. Class Imbalance Overview

Financial fraud datasets suffer from extreme class imbalance because illegal mule activity accounts for less than 1% of total bank customer accounts.

```
Target Distribution (F3924):
─────────────────────────────────────────────────────────────
Class 0 (Legitimate Non-Mule):  9,001 accounts (99.1081%)
Class 1 (Mule / Fraud):            81 accounts ( 0.8919%)
─────────────────────────────────────────────────────────────
Total Evaluated:                9,082 accounts (100.0000%)
Class Imbalance Ratio:         111.12 to 1 (Extreme Imbalance)
```

### Why Accuracy is Misleading:
A naive model that predicts `Class 0` (Legitimate) for all accounts achieves **99.11% Accuracy** while catching **0% of fraud cases (0% Recall)**. Therefore, **Precision-Recall AUC (PR-AUC)** and **F1-Score** are used as the primary evaluation metrics.

---

## 2. Experimental Benchmark Results (5-Fold Group-Aware CV)

Five imbalance handling techniques were evaluated across identical **5-Fold Group-Aware Cross-Validation** splits (using 6,118 group clusters):

```
                                ┌───────────────────────────────────────────────────────────┐
                                │       CLASS IMBALANCE STRATEGY BENCHMARK RESULTS          │
                                └─────────────────────────────┬─────────────────────────────┘
                                                              │
┌──────────────────────────────────────────────┬──────────────┴───────────────┬──────────────┬──────────────┐
│ Strategy                                     │ PR-AUC (Mean ± Std)          │ F1-Score     │ Recall       │ Precision    │
├──────────────────────────────────────────────┼──────────────────────────────┼──────────────┼──────────────┤
│ SMOTE + scale_pos_weight (CHAMPION)          │ 0.8807 ± 0.0403              │ 0.7586       │ 0.6164       │ 1.0000       │
│ ADASYN + scale_pos_weight                    │ 0.8810 ± 0.0493              │ 0.7267       │ 0.5795       │ 1.0000       │
│ Pure scale_pos_weight (No Oversampling)      │ 0.8775 ± 0.0624              │ 0.5909       │ 0.4312       │ 1.0000       │
│ Borderline-SMOTE + scale_pos_weight          │ 0.8231 ± 0.0478              │ 0.7425       │ 0.6140       │ 0.9453       │
│ Unweighted Baseline (No Weighting)           │ 0.8183 ± 0.0732              │ 0.7538       │ 0.6660       │ 0.8992       │
└──────────────────────────────────────────────┴──────────────────────────────┴──────────────┴──────────────┘
```

---

## 3. Detailed Strategy Evaluation

1. **SMOTE + `scale_pos_weight` (SELECTED CHAMPION):**
   * **Result:** **`0.8807 ± 0.0403` PR-AUC**, **`1.0000` Precision**, **`0.6164` Recall**, **`0.7586` F1**.
   * **Why Chosen:** Applying SMOTE *strictly on training folds* generates synthetic positive minority samples in feature space, while `scale_pos_weight=111.12` adjusts XGBoost gradient loss weighting. This combination achieves **100% Precision** while boosting **Recall by +18.52%** compared to `scale_pos_weight` alone.
2. **ADASYN + `scale_pos_weight`:**
   * Achieved similar PR-AUC (`0.8810`) but exhibited higher fold variance ($\pm 0.0493$) and lower Recall (`0.5795`).
3. **Pure `scale_pos_weight` (No Oversampling):**
   * Achieved high Precision (`1.0000`) but suffered low Recall (`0.4312`), missing nearly 57% of positive fraud cases.
4. **Borderline-SMOTE & Unweighted Baseline:**
   * Produced lower Precision (`0.9453` and `0.8992`), introducing false positive account freezes.

---

## 4. Zero-Leakage Oversampling Rule

To prevent data leakage, SMOTE synthetic oversampling is executed **strictly inside training fold loops**:

$$\text{X\_train\_resampled}, \text{y\_train\_resampled} = \text{SMOTE}(random\_state=42).\text{fit\_resample}(\text{X\_train}, \text{y\_train})$$

Validation folds are **NEVER** oversampled; they remain 100% untouched to reflect real-world operational distributions.
