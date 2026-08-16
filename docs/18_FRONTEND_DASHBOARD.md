# 🖥️ 18 — FRONTEND ANALYST DASHBOARD

---

## 1. Dashboard Overview

The MuleShield PRO frontend is built as a responsive single-page web application ([backend/static/index.html](file:///a:/Projects/PSB/backend/static/index.html)) styled with Tailwind CSS, Google Inter/JetBrains typography, and Vis.js Network canvas visualization.

---

## 2. Detailed Tab-by-Tab Breakdown

### 1. Tab 1: Risk Case Queue & Account Inspector
* **Purpose:** Main investigation dashboard for bank fraud analysts.
* **Left Panel:** Risk case queue listing flagged accounts sorted by risk score. Multi-tier filter buttons (`ALL`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) allow instant sub-queue filtering.
* **Right Panel (Inspector):** Displays selected account risk score (`0.9999`), SHAP behavioral anomaly drivers with plain-language domain descriptions, and watchlist status badges.
* **Interactive Actions:**
  * **Confirm CBS Debit Freeze Button:** Triggers simulated Core Banking System debit lock.
  * **Generate STR Draft Button:** Creates FIU-IND legal report draft.

---

### 2. Tab 2: Live Account Anomaly Sandbox
* **Purpose:** Real-time testing sandbox for evaluating un-indexed account profiles or incoming transaction JSON API payloads.
* **Controls:** **Load Sample Mule Payload** button populates raw feature parameters into the JSON code editor.
* **Execution:** **Execute Real-Time Classification** dispatches payload to `POST /api/predict`.
* **Output Card:** Renders dynamic probability score (e.g. `0.9791`), classification tier (`CRITICAL MULE DETECTED`), and threshold comparison.

---

### 3. Tab 3: Mule Network Ring Topology *(Simulated Visual Demo)*
* **Purpose:** Visualizes multi-hop fund-layering networks to demonstrate graph syndicate detection concepts.
* **Prominent Banner:** Clearly labeled `<span class="badge">Illustrative Example — Simulated Data</span>`.
* **Interactive Canvas:** Vis.js 2D physics graph showing 8-node fund flow (`Victim #1001` $\rightarrow$ `Feeder #9001` $\rightarrow$ `Mules #9003/#9004/#9006` $\rightarrow$ `Aggregator #9099` $\rightarrow$ `ATM Cash-Out / Crypto`).

---

### 4. Tab 4: Regulatory Intelligence & Watchlists
* **Purpose:** Manages national regulatory watchlist feeds and cross-references them against bank accounts.
* **Status Badges:** Displays connection status for **I4C Cyber Fraud DB** (87 Mule Matches), **CERT-In Botnet List**, and **RBI Caution List**.
* **Interactive Search:** Client-side search bar filtering regulatory tickets by account ID or match status.

---

### 5. Tab 5: Model Calibration & Performance Audit
* **Purpose:** Transparency panel providing complete audit logs of model validation benchmarks.
* **Benchmark Table:** Displays 5-Fold Group-Aware CV metrics across XGBoost (`0.8807` PR-AUC), Random Forest (`0.7845`), and Logistic Regression (`0.6652`).
* **Decision Threshold Slider:** Interactive slider demonstrating model sensitivity from `0.50` to `0.999` (default calibrated at `0.9899`).
