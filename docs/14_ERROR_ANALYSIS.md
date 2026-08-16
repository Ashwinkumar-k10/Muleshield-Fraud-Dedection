# 🔍 14 — ERROR ANALYSIS & MISCLASSIFICATION DIAGNOSTICS

---

## 1. Error Analysis Overview

Error analysis examines the specific conditions under which the XGBoost model produces False Positives (legitimate accounts flagged as mules) and False Negatives (mule accounts missed by the classifier).

```
                       PREDICTED CLASS
                  Non-Mule (0)      Mule (1)
ACTUAL   Non-Mule (0)   9,000            1      (False Positive Rate = 0.011%)
CLASS    Mule (1)         26            55      (False Negative Rate = 32.099%)
```

---

## 2. False Positive (FP) Analysis

* **Occurrences:** 1 account in full dataset evaluation at threshold `0.9899`.
* **Root Cause:** The account belonged to a small retail merchant experiencing sudden high-volume UPI inflows during a festive promotional campaign. The rapid influx of digital transfers mimicked mule layering behavior.
* **Banking Impact:** Minimizing False Positives is critical for Public Sector Banks. Unnecessary account freezes generate customer friction, regulatory complaints, and operational overhead.
* **Mitigation in MuleShield PRO:** Calibrating decision threshold to `0.9899` ensures near-zero false freezes (`99.989% Specificity`).

---

## 3. False Negative (FN) Analysis

* **Occurrences:** 26 accounts in full dataset evaluation.
* **Root Cause:** Missed mule accounts were primarily **dormant low-activity accounts** that received single, small-value transfers just below transaction volume deviation thresholds. Because these accounts exhibited minimal transaction history prior to the alert, numerical deviation ratios remained low.
* **Banking Impact:** Missed mule accounts allow fraudulent proceeds to circulate through the banking system.
* **Mitigation in MuleShield PRO:** MuleShield PRO addresses False Negatives through a **multi-layered defense strategy**:
  1. **Regulatory Intelligence Watchlist Integration (Tab 4):** Accounts missed by transaction ML models are cross-referenced against external I4C cyber-fraud tickets and RBI caution lists.
  2. **Multi-Tier Risk Queue:** Accounts scoring between `0.6000` and `0.7999` are routed to the `High Risk` queue for manual human inspection rather than being outright cleared.
