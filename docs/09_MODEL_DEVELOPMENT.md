# 🤖 09 — MODEL DEVELOPMENT & ALGORITHM SELECTION

---

## 1. Algorithm Selection Rationale (XGBoost)

**XGBoost (Extreme Gradient Boosting)** was selected as the core machine learning algorithm for MuleShield PRO.

### Why XGBoost for Banking Fraud Detection?
1. **Handles Tabular Financial Data:** Superior performance on high-dimensional, tabular transaction matrices compared to deep neural networks.
2. **Missing Value Robustness:** Automatically learns optimal split directions for missing values (`NaN`).
3. **Non-Linear Feature Interaction:** Effectively models complex interactions between transaction velocity, channel type, and deviation ratios.
4. **TreeSHAP Explainability:** Fully compatible with exact TreeSHAP calculation for regulatory auditability.
5. **Scale Position Weighting:** Supports native positive class weighting (`scale_pos_weight`) to optimize gradient updates for imbalanced data.

---

## 2. Beginner-Friendly Explanation of XGBoost

XGBoost works by combining hundreds of small, simple decision trees in a step-by-step process called **boosting**:

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│   Tree 1 (Weak)   │ ──► │  Tree 2 (Fixes    │ ──► │  Tree 3 (Fixes    │ ──► │ Combined Ensemble │ ──► Probability
│  Initial Pattern  │     │  Tree 1 Errors)   │     │  Tree 2 Errors)   │     │ (Sum of Trees)    │     Risk Score
└───────────────────┘     └───────────────────┘     └───────────────────┘     └───────────────────┘
```

1. **Tree 1** makes an initial prediction based on transaction features (e.g. *High Cash Withdrawal Velocity*).
2. **Tree 2** focuses specifically on the errors made by Tree 1 (e.g. *Accounts where UPI credit was high but tenure was long*).
3. **Tree 3** corrects remaining errors, gradually refining prediction accuracy.
4. **Ensemble Sum:** The final prediction is a weighted sum of all tree outputs converted into a probability score ($0.0000$ to $1.0000$) using the sigmoid function.

---

## 3. Production Model Configuration & Hyperparameters

The champion model parameters are stored at [modeling/model_config.json](file:///a:/Projects/PSB/modeling/model_config.json):

```json
{
  "decision_threshold": 0.9899,
  "pr_auc_mean": 0.8833,
  "pos_weight": 111.12345679012346,
  "hyperparameters": {
    "max_depth": 3,
    "min_child_weight": 3,
    "gamma": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "lr": 0.05,
    "n_est": 200
  },
  "bank_finalized_vars": 19
}
```

### Parameter Breakdown:
* **`tree_method = 'hist'`:** High-speed histogram binning for large tabular matrices.
* **`max_depth = 3`:** Restricts tree depth to 3 levels, preventing deep leaf memorization.
* **`min_child_weight = 3`:** Requires at least 3 samples per leaf node to create a split.
* **`gamma = 0.1`:** Imposes minimum loss reduction threshold for splits.
* **`subsample = 0.8`:** Stochastic row sampling (uses 80% of rows per tree).
* **`colsample_bytree = 0.8`:** Stochastic column sampling (uses 80% of features per tree).
* **`reg_alpha = 0.1` (L1) & `reg_lambda = 1.0` (L2):** Elastic net regularization to shrink feature weights.
* **`learning_rate = 0.05` & `n_estimators = 200`:** Conservative shrinkage rate across 200 boosting iterations.
