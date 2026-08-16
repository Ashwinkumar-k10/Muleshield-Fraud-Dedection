# 📊 31 — CANONICAL METRICS TABLE (SINGLE SOURCE OF TRUTH)

---

## 1. Primary System Benchmark Matrix

The following canonical table defines the single source of truth for all quantitative performance metrics across the **MuleShield PRO** repository:

| Metric Name | Value | Validation / Evaluation Methodology | Primary Purpose & Usage Context |
| :--- | :--- | :--- | :--- |
| **Out-Of-Fold (OOF) PR-AUC** | **`0.9180`** | 5-Fold Stratified Group-Aware CV (no repeats, single OOF pass over 9,082 rows) | **Primary baseline out-of-fold generalization performance across unseen accounts.** |
| **5-Fold Group CV PR-AUC (Mean ± Std)** | **`0.9131 ± 0.0458`** | Out-of-fold metrics across 5 isolated similarity group folds (6,118 clusters) | **Fold stability indicator showing robust generalization across group splits.** |
| **OOF Precision @ Threshold 0.9899** | **`1.0000` (100.0%)** | Single OOF prediction pass on 9,082 unseen holdout rows | **Zero false positive debit freezes on unseen validation accounts (0 False Positives).** |
| **OOF Recall @ Threshold 0.9899** | **`0.5926` (59.26%)** | Single OOF prediction pass on 9,082 unseen holdout rows | **Fraud recall catching 48 out of 81 positive mule accounts automatically.** |
| **OOF F1-Score @ Threshold 0.9899** | **`0.7442`** | Single OOF prediction pass on 9,082 unseen holdout rows | **Harmonic mean of precision and recall at production decision boundary.** |
| **Hyperparameter-Search Champion PR-AUC** | **`0.8833 ± 0.0365`** | Grid-search optimization experiment (`modeling/model_config.json`) | **Historical hyperparameter selection benchmark recorded during grid-search tuning.** |
| **Historical CV Benchmark PR-AUC** | **`0.8807 ± 0.0403`** | Early 5-fold group CV trial with SMOTE + scale_pos_weight | **Documented baseline score reported in legacy review documentation.** |
| **In-Sample Full-Dataset Specificity** | **`0.99989` (99.989%)** | Full dataset inference evaluation ($9,082$ rows at threshold `0.9899`) | **In-sample full dataset operational check (9,000 TN, 1 FP). NOT a generalization metric.** |
| **In-Sample Full-Dataset Sensitivity** | **`0.67901` (67.901%)** | Full dataset inference evaluation ($9,082$ rows at threshold `0.9899`) | **In-sample full dataset operational check (55 TP, 26 FN). NOT a generalization metric.** |
| **10% Null Cell Stress Test PR-AUC** | **`0.8383`** | Random nulling of 10% populated cells across 6,820 feature space | **ROBUSTNESS TEST — NOT hidden validation (demonstrates -7.97% graceful degradation).** |

---

## 2. OOF Threshold Analysis Matrix

Evaluated directly on the single 9,082-row Out-Of-Fold probability vector:

| Decision Threshold | Precision | Recall | F1-Score | FP Count | FN Count | True Positives (TP) | True Negatives (TN) | Operating Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0.5000` | `0.6789` | `0.9136` | `0.7789` | 35 | 7 | 74 | 8966 | High recall; high false freeze rate (35 legitimate accounts locked). |
| `0.7000` | `0.8293` | `0.8395` | `0.8344` | 14 | 13 | 68 | 8987 | Balanced exploratory threshold. |
| `0.9000` | `0.9275` | `0.7901` | `0.8533` | 5 | 17 | 64 | 8996 | High precision; 5 false freezes. |
| `0.9500` | `0.9846` | `0.7901` | `0.8767` | 1 | 17 | 64 | 9000 | Peak F1-Score operating point; 1 false freeze. |
| `0.9700` | `1.0000` | `0.7531` | `0.8592` | 0 | 20 | 61 | 9001 | Zero false positive boundary. |
| `0.9800` | `1.0000` | `0.6667` | `0.8000` | 0 | 27 | 54 | 9001 | Conservative freeze boundary. |
| `0.9850` | `1.0000` | `0.6420` | `0.7820` | 0 | 29 | 52 | 9001 | Ultra-conservative freeze boundary. |
| **`0.9899`** | **`1.0000`** | **`0.5926`** | **`0.7442`** | **0** | **33** | **48** | **9001** | **SELECTED PRODUCTION BOUNDARY — Zero False Debit Freezes.** |
| `0.9900` | `1.0000` | `0.5926` | `0.7442` | 0 | 33 | 48 | 9001 | Near-identical operating point. |
| `0.9950` | `1.0000` | `0.5679` | `0.7244` | 0 | 35 | 46 | 9001 | Restrictive boundary; lower fraud recall. |

---

## 3. Banking Rationale for Operating Point (0.9899)

In Public Sector Banking operations, triggering an automated Core Banking System (CBS) debit freeze on a legitimate customer account inflicts catastrophic customer dissatisfaction, legal liability under banking Ombudsman regulations, and operational overhead. 

MuleShield PRO deliberately operates at **`threshold = 0.9899`** to enforce **`100% Precision (0 False Positives)`** on out-of-fold validation accounts. The remaining 33 false negatives are not ignored; they are routed to secondary compliance analyst review queues and regulatory watchlist cross-referencing rather than executing immediate debit locks.
