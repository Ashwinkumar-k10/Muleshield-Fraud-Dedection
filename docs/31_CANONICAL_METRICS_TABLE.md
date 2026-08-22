# 📊 31 — CANONICAL METRICS TABLE (SINGLE SOURCE OF TRUTH)

---

## 1. Primary System Benchmark Matrix

The following canonical table defines the single source of truth for all quantitative performance metrics across the **MuleShield PRO** repository:

| Metric Name | Value | Validation / Evaluation Methodology | Primary Purpose & Usage Context |
| :--- | :--- | :--- | :--- |
| **Final Serialized / Verified Model PR-AUC** | **`0.8807 ± 0.0403`** | 5-Fold Stratified Group-Aware CV (leakage-free holdout evaluation) | **Primary verified 5-fold cross-validation performance of the final serialized model.** |
| **Hyperparameter-Search Champion PR-AUC** | **`0.8833 ± 0.0365`** | Grid-search optimization experiment (`modeling/model_config.json`) | **Optimization champion score recorded during grid-search tuning.** |
| **Precision @ Threshold 0.9899** | **`1.0000` (100.0%)** | 5-Fold Group-Aware CV on validation folds | **Zero false positive debit freezes on unseen validation accounts (0 False Positives).** |
| **Recall @ Threshold 0.9899** | **`0.6164` (61.64%)** | 5-Fold Group-Aware CV on validation folds | **Fraud recall catching 61.64% of positive mule accounts automatically.** |
| **F1-Score @ Threshold 0.9899** | **`0.7586`** | 5-Fold Group-Aware CV on validation folds | **Harmonic mean of precision and recall at production decision boundary.** |
| **Calibrated Decision Threshold** | **`0.9899`** | Precision-Recall curve threshold tuning on validation folds | **Selected production decision boundary enforcing 100% Precision.** |
| **In-Sample Full-Dataset Specificity** | **`0.99989` (99.989%)** | Full dataset inference evaluation ($9,082$ rows at threshold `0.9899`) | **In-sample full dataset operational check (9,000 TN, 1 FP). NOT a generalization metric.** |
| **In-Sample Full-Dataset Sensitivity** | **`0.67901` (67.901%)** | Full dataset inference evaluation ($9,082$ rows at threshold `0.9899`) | **In-sample full dataset operational check (55 TP, 26 FN). NOT a generalization metric.** |

---

## 2. Threshold & Operational Decision Rationale (Threshold 0.9899)

In Public Sector Banking operations, triggering an automated Core Banking System (CBS) debit freeze on a legitimate customer account inflicts catastrophic customer dissatisfaction, legal liability under banking Ombudsman regulations, and operational overhead. 

MuleShield PRO deliberately operates at **`threshold = 0.9899`** to enforce **`100% Precision (1.0000)`** on validation folds with **`61.64% Recall (F1 = 0.7586)`**. Unflagged accounts are routed to secondary compliance analyst review queues and regulatory watchlist cross-referencing rather than executing immediate debit locks.
