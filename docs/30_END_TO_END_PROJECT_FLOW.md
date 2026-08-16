# 🔄 30 — END-TO-END STEP-BY-STEP PROJECT FLOW
**Beginner-Friendly Complete System Walkthrough**

---

## 1. Complete Step-by-Step Execution Journey

This document explains the entire **MuleShield PRO** system from initial raw dataset ingestion to final decision-making on the Analyst Dashboard in 24 clear steps.

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                       END-TO-END PROJECT FLOW (STEPS 1 TO 24)                             │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
 │ STAGE 1: DATA INGESTION & AUDIT (Steps 1 - 5)                                            │
 │ 1. Ingest Raw Dataset (`data_copy.csv` — 9,082 rows x 3,924 columns).                    │
 │ 2. Identify Target Variable (`F3924` — 81 Fraud vs 9,001 Non-Fraud).                      │
 │ 3. Inspect Feature Mapping (`Description.xlsx` — 3,924 column descriptions).            │
 │ 4. Perform Data Quality Audit (Missing values, zero-variance columns, quantiles).        │
 │ 5. Cluster Near-Duplicates (6,118 groups connected via >0.99 cosine similarity).        │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
 │ STAGE 2: LEAKAGE SANITIZATION & PREPROCESSING (Steps 6 - 9)                              │
 │ 6. Purge Post-Incident Flags (Dropped F3912, F3914, F3913, F3915, F3898, F3899).         │
 │ 7. Purge Date Proxies (Dropped F2230 alert date & F3888 account open date).              │
 │ 8. Engineer Banking Ratios (CASH_TO_UPI, UPI_TO_TOTAL_DEV, TENURE_AGE ratios).            │
 │ 9. Fit Preprocessor Pipeline (Impute medians, quantile clip, generate _ismissing).       │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
 │ STAGE 3: MODEL TRAINING & VALIDATION (Steps 10 - 15)                                    │
 │ 10. Execute 5-Fold Group CV (Isolate 6,118 clusters across 5 folds).                    │
 │ 11. Oversample Training Folds (Apply SMOTE strictly inside train fold loop).             │
 │ 12. Train XGBoost Classifier (tree_method='hist', max_depth=3, L1=0.1, L2=1.0).          │
 │ 13. Optimize Hyperparameters (Champion PR-AUC 0.8833 ± 0.0365).                          │
 │ 14. Calibrate Decision Threshold (Tuned to 0.9899 on validation folds).                  │
 │ 15. Serialize Model Artifacts (`mule_shield_model.json`, `preprocessor.pkl`).             │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
 │ STAGE 4: BACKEND API & FRONTEND DASHBOARD (Steps 16 - 20)                                │
 │ 16. Start Flask Web Server (`python backend/main.py` listening on port 8000).            │
 │ 17. Load MuleShieldRiskEngine (Loads model binary & preprocessor in memory).             │
 │ 18. Serve Single-Page UI (`index.html` with Tailwind CSS & Google Fonts).               │
 │ 19. Populate Case Queue (GET `/api/cases` returns 382 cases & dataset counts).           │
 │ 20. Execute Real-Time Predictions (POST `/api/predict` evaluates raw payloads).          │
 └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
 ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
 │ STAGE 5: INVESTIGATION & ACTION (Steps 21 - 24)                                          │
 │ 21. Compute SHAP Driver Explanations (TreeSHAP maps feature impact to domain labels).    │
 │ 22. Generate STR Report Draft (POST `/api/cases/<id>/str-draft` produces FIU text).      │
 │ 23. Demonstrate CBS Debit Freeze (Analyst triggers mock debit freeze confirmation).      │
 │ 24. Render Mule Ring Graph Topology (Vis.js renders synthetic 8-node fund layering).     │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Step-by-Step Breakdown

### Step 1: Problem & Dataset Ingestion
* **What Happens:** The system loads `data_copy.csv` containing 9,082 account profiles across 3,924 numerical and categorical columns.
* **Input:** `data_copy.csv`
* **Output:** In-memory Pandas DataFrame ($9,082 \times 3,925$).

### Step 2: Target Isolation & Imbalance Audit
* **What Happens:** Identifies target column `F3924`. Confirms extreme imbalance (81 Fraud vs 9,001 Non-Fraud accounts).
* **Input:** Raw DataFrame column `F3924`.
* **Output:** Target vector `y` and feature matrix `X`.

### Step 3: Feature Dictionary Mapping
* **What Happens:** Maps raw anonymized column IDs (`F1`-`F3924`) to business descriptions in `Description.xlsx`.
* **Input:** `Description.xlsx`
* **Output:** Feature dictionary mapping array.

### Step 4: Data Quality Audit
* **What Happens:** Computes missing value percentages, checks for constant zero-variance columns, and inspects quantile distributions.
* **Input:** Feature matrix `X`.
* **Output:** Data quality metrics report.

### Step 5: Duplicate Group Clustering
* **What Happens:** Computes pairwise cosine similarity matrix across normalized rows. Groups accounts exceeding $0.99$ similarity using connected components.
* **Input:** Feature matrix `X`.
* **Output:** 6,118 group cluster IDs array.

### Step 6: Post-Incident Leakage Sanitization
* **What Happens:** Purges 12 post-incident human resolution columns (`F3912`, `F3914`, `F3913`, `F3915`, `F3898`, `F3899` and missingness indicators).
* **Input:** Feature matrix `X`.
* **Output:** Sanitized matrix excluding post-incident flags.

### Step 7: Date Proxy Removal
* **What Happens:** Removes temporal date proxy columns `F2230` (`ALERT_DATE`) and `F3888` (`ACCT_OPN_DATE`).
* **Input:** Feature matrix `X`.
* **Output:** Matrix free from temporal calendar proxies.

### Step 8: Domain Feature Engineering
* **What Happens:** Appends `BANK_FE_CASH_TO_UPI_RATIO`, `BANK_FE_UPI_TO_TOTAL_DEV_RATIO`, and `BANK_FE_TENURE_AGE_RATIO`.
* **Input:** Feature matrix `X`.
* **Output:** Feature matrix with appended ratio features.

### Step 9: Preprocessor Pipeline Fitting
* **What Happens:** `MuleShieldPreprocessor` fits median imputations, quantile clipping bounds (1st/99th percentiles), and one-hot encodings.
* **Input:** Feature matrix `X`.
* **Output:** Fitted `preprocessor.pkl` and 6,820 aligned feature schema.

### Step 10: 5-Fold Group-Aware Cross-Validation Setup
* **What Happens:** Sets up 5-Fold Stratified Group K-Fold cross-validation using the 6,118 group cluster IDs.
* **Input:** Feature matrix `X`, target `y`, `groups`.
* **Output:** 5 isolated train/validation fold splits.

### Step 11: SMOTE Resampling on Training Folds
* **What Happens:** Applies SMOTE minority oversampling *strictly inside training fold loops*.
* **Input:** Training fold `X_train`, `y_train`.
* **Output:** Balanced training fold `X_train_res`, `y_train_res`.

### Step 12: XGBoost Classifier Training
* **What Happens:** Trains XGBoost classifier (`tree_method='hist'`, `max_depth=3`, `scale_pos_weight=111.12`, L1=`0.1`, L2=`1.0`).
* **Input:** Balanced training fold matrices.
* **Output:** Fitted XGBoost tree ensemble.

### Step 13: Hyperparameter Optimization Search
* **What Happens:** Evaluates parameter configurations across folds, selecting Config #1 (`PR-AUC 0.8833 ± 0.0365`).
* **Input:** Cross-validation predictions.
* **Output:** Selected champion hyperparameter dictionary.

### Step 14: Decision Threshold Calibration
* **What Happens:** Computes Precision-Recall curve on validation folds, calibrating optimal decision threshold to `0.9899`.
* **Input:** Validation probability outputs.
* **Output:** Calibrated decision threshold (`0.9899`).

### Step 15: Model Artifact Serialization
* **What Happens:** Saves fitted model binary to `mule_shield_model.json`, preprocessor to `preprocessor.pkl`, and config to `model_config.json`.
* **Input:** Fitted champion model and preprocessor.
* **Output:** Serialized files in `modeling/` and `muleshield_deploy_pack/modeling/`.

### Step 16: Flask Web Backend Startup
* **What Happens:** `python backend/main.py` starts the WSGI web server on `http://localhost:8000`.
* **Input:** `backend/main.py`
* **Output:** HTTP server listening on port 8000.

### Step 17: MuleShield Risk Engine Loading
* **What Happens:** `MuleShieldRiskEngine` initializes, loading `mule_shield_model.json` and `preprocessor.pkl` into memory.
* **Input:** `modeling/` files.
* **Output:** In-memory risk engine ready for inference.

### Step 18: Dashboard Single-Page UI Serving
* **What Happens:** Flask serves `backend/static/index.html` at route `/`.
* **Input:** HTTP GET request to `/`.
* **Output:** Single-page application rendered in browser.

### Step 19: Case Queue In-Memory Index Query
* **What Happens:** Dashboard fetches `GET /api/cases`. Backend queries `backend/db.py` and returns indexed account cards and summary counts.
* **Input:** HTTP GET request to `/api/cases`.
* **Output:** JSON list of 382 cases and dataset counts (`9,082` evaluated).

### Step 20: Real-Time Anomaly Sandbox Inference
* **What Happens:** User clicks "Execute Real-Time Classification" in Tab 2. Dispatches payload to `POST /api/predict`.
* **Input:** JSON payload `{"F1": 15.0, ...}`.
* **Output:** JSON response `{"risk_score": 0.9791, "tier": "Critical", ...}`.

### Step 21: SHAP Driver Calculation & Display
* **What Happens:** Risk Engine computes TreeSHAP values for positive predictions and maps raw feature IDs to plain-language labels.
* **Input:** Evaluated account feature vector.
* **Output:** Top 3 SHAP anomaly drivers displayed on UI Inspector panel.

### Step 22: STR Compliance Report Draft Generation
* **What Happens:** Analyst clicks "Generate STR Draft" in Tab 1. Backend formats FIU-IND report template and saves text file to `backend/storage/str_report_<id>.txt`.
* **Input:** Account ID.
* **Output:** Formatted STR draft text returned to UI and saved to disk.

### Step 23: Simulated CBS Debit Freeze Demonstration
* **What Happens:** Analyst clicks "Confirm CBS Debit Freeze" on a Critical account card. UI renders simulated freeze confirmation receipt (`CBS-FRZ-2026-9003-8492`).
* **Input:** User click event.
* **Output:** Instant UI confirmation receipt card.

### Step 24: Mule Ring Network Graph Visualization
* **What Happens:** User selects Tab 3. Vis.js physics canvas renders interactive 8-node fund-layering graph with simulated disclaimer badge.
* **Input:** User tab selection.
* **Output:** Interactive 2D graph network rendering.
