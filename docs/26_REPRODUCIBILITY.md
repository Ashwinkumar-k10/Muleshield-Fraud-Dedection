# 🔄 26 — REPRODUCIBILITY & DETERMINISTIC PIPELINE

---

## 1. Reproducibility Guarantee

MuleShield PRO enforces deterministic execution across preprocessing, cross-validation, SMOTE oversampling, and model training.

---

## 2. Fixed Random Seeds & Configuration Parameters

| Pipeline Component | Deterministic Seed Parameter | Stored Parameter Value |
| :--- | :--- | :--- |
| **Group K-Fold CV** | `StratifiedGroupKFold(random_state=42)` | `42` |
| **SMOTE Oversampling** | `SMOTE(random_state=42)` | `42` |
| **XGBoost Model** | `XGBClassifier(random_state=42)` | `42` |
| **Decision Threshold** | Calibrated threshold value | `0.9899` |
| **Class Weighting** | Inverse positive class balance | `111.1235` |

---

## 3. How to Reproduce Cross-Validation Experiments

Run the optimization script from the workspace root:

```bash
python scripts/optimize_pipeline_final.py
```
This script will:
1. Ingest `data_copy.csv`.
2. Apply `MuleShieldPreprocessor` (purges leakage flags and adds ratio features).
3. Compute 6,118 cosine similarity group IDs.
4. Execute 5-Fold Group CV across SMOTE, ADASYN, and regularized XGBoost parameter grid.
5. Save `modeling/mule_shield_model.json`, `modeling/preprocessor.pkl`, and `modeling/model_config.json`.
