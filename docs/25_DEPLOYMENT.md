# 🚀 25 — LOCAL & PRODUCTION DEPLOYMENT GUIDE

---

## 1. Local Prototype Deployment

### Prerequisites:
* Python 3.11+
* Installed packages: `pandas`, `numpy`, `xgboost`, `scikit-learn`, `imbalanced-learn`, `shap`, `flask`, `flask_cors`, `joblib`, `pyarrow`, `openpyxl`

### Step 1: Clone Repository
```bash
git clone https://github.com/Ashwinkumar-k10/Muleshield-Fraud-Dedection.git
cd Muleshield-Fraud-Dedection
```

### Step 2: Start Backend Server
```bash
python backend/main.py
```
* The server initializes the `MuleShieldRiskEngine`, loads `preprocessor.pkl` and `mule_shield_model.json`, and starts listening on `http://localhost:8000`.

### Step 3: Access Dashboard
Open your web browser and navigate to:
```
http://localhost:8000
```

---

## 2. Standalone Deployment Package Execution

To run offline inference without starting the web server, use the self-contained package ([muleshield_deploy_pack/](file:///a:/Projects/PSB/muleshield_deploy_pack/)):

```bash
python muleshield_deploy_pack/run_model.py
```
* Loads `muleshield_deploy_pack/sample_data.csv`, executes transformation via `preprocessor.pkl`, evaluates against `mule_shield_model.json`, and outputs risk probabilities and classifications directly to the terminal.
