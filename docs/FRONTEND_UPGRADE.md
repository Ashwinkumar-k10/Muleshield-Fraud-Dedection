# 🛡️ MuleShield PRO — Frontend Upgrade & Architectural Documentation

This document describes the engineering modifications, visual design system, authentication guards, and application flow implemented to transition the initial **MuleShield PRO** prototype into an enterprise-grade fraud operations workstation.

---

## 📋 1. What Existed Before
* A basic HTML layout with simple data styling.
* Local case prediction forms with manual inputs, missing validation checks, and limited error states.
* Synchronous API calls directly inside component triggers (causing potential request blocking).
* Hard-coded performance metric text blocks (e.g. baseline PR-AUC values) across various HTML views.
* A simple network topology template containing static nodes.
* A sandbox interface with basic error handling and no visual progress indicators.

---

## ⚡ 2. What Was Upgraded
1. **Interactive Demo Gate (Authentication):** Implemented a workstation login interface restricting access to the dashboard.
2. **Unified Navigation Shell:** Sidebar structure with collateral KPI cards and active tab controls.
3. **Dynamic Operations Command Center:** Added recent high-risk alert feeds, operational KPI statistics, and active status indicators.
4. **Enhanced Case Queue Workspace:** Redesigned columns containing Case IDs, Status Badges, and Assigned Analyst fields. Added search controls, status dropdown filters, and tier selectors.
5. **Detailed Inspector Workspace:** Separated details into sub-cards: attributes lists, TreeSHAP explainability drivers, regulatory intersection panels, timeline audits, and custom case notes.
6. **Robust Evaluator Interface:** Consolidated input options with progress animations and risk tier outputs.
7. **Technical Model Performance Benchmarks:** Fetches metrics dynamically from a centralized metadata API.
8. **Automated Document Compiler:** Generates printable PDF investigation summaries containing transaction registries and timeline histories.

---

## 🔄 3. Workstation Flow & Lifecycle

```
    LOGIN PAGE (Demo Authenticated Entry Gate)
        │
        ▼
    COMMAND CENTER (Executive Dashboard Feed)
        │
        ├──► CASE QUEUE (Filter by Severity & Status) ──► SELECT CASE ──► INSPECT PROFILE
        │                                                                   ├─► TreeSHAP Drivers
        │                                                                   ├─► Regulatory Intersects
        │                                                                   ├─► Timeline & Notes
        │                                                                   └─► PDF Report Download
        ▼
    EVALUATE ACCOUNT (Standard Inputs / Raw JSON Payload) ──► MODEL RUN ──► CLASSIFICATION
```

---

## 🏗️ 4. Frontend Architecture
The system uses a Single-Page Application (SPA) architecture inside [`frontend/index.html`](file:///a:/Projects/PSB/frontend/index.html):
* **Tailwind CSS Utility Engine:** Handles layouts, typography scales, spacing, and grid configurations.
* **Component-Like Workspace Panels:** Separate `<main>` containers for each workspace tag, shown/hidden dynamically via standard JS handlers.
* **Dynamic Node Canvas:** Vis.js Network rendering engine for graph networks.
* **Clean State Stores:** Dynamic memory buffers holding cases, model metrics, and active case details:
  ```javascript
  let allCases = [];
  let selectedCaseId = null;
  let activeTab = 'dashboard';
  let modelMetadata = {};
  ```

---

## 🔌 5. API Integration Details
All backend API routes are integrated into the frontend service layer:
* `GET /api/model/metadata` $\rightarrow$ Hydrates metric parameters across tabs.
* `GET /api/cases` $\rightarrow$ populates dashboard statistics and queues.
* `GET /api/cases/<id>` $\rightarrow$ Populates the inspector workspace.
* `POST /api/cases/<id>/status` $\rightarrow$ Updates case status.
* `POST /api/cases/<id>/notes` $\rightarrow$ Appends note logs.
* `POST /api/cases/<id>/cbs-freeze` $\rightarrow$ Updates status to `ESCALATED` and adds freeze entries.
* `POST /api/predict` $\rightarrow$ Processes ad-hoc inputs.
* `GET /api/audit-logs` $\rightarrow$ Returns system events.

---

## 🔐 6. Workstation Access Control (Authentication)
* **Status:** `DEMONSTRATION AUTHENTICATION GATE` (Implemented)
* **Mechanics:**
  * Checks for `muleshield_authenticated` in `sessionStorage` on page load.
  * If absent, restricts access and displays the login gate modal.
  * Permits entry using the mock login credential:
    * **Email / ID:** `analyst@muleshield.psb`
    * **Password:** `password`
  * Deletes session storage tokens upon clicking logout.

---

## 🔍 7. Triage Workspace & Case Lifecycle
Critical, High, and Medium risk alerts default to a `NEW` status and are assigned to `Unassigned` on ingestion. Analysts can manage the case lifecycle:
$$\text{NEW} \longrightarrow \text{TRIAGED} \longrightarrow \text{UNDER REVIEW} \longrightarrow \text{ESCALATED} \longrightarrow \text{CLOSED}$$

* **Analyst Notes:** Input forms allow appending custom logs to the case folder.
* **Timeline log:** Stores a chronological history of status changes, note entries, and system warnings.

---

## 📄 8. Automated Document Compiler
* **PDF Report Generator:** Compiles a formatted PDF layout using ReportLab. File naming matches:
  `MuleShield_Report_<CASE_ID>.pdf`
* **JSON File Exporter:** Downloads raw case data as `MuleShield_Case_<CASE_ID>.json`.
* **CSV Bulk Exporter:** Exports case logs as `MuleShield_Cases_<DATE>.csv`.

---

## 🏛️ 9. Performance & Audit Integrity Workspaces
* **Performance Benchmarks:** Shows group-KFold metrics dynamically loaded from the backend API.
* **Integrity Audit:** Displays checks confirming preprocessor settings, feature ordering, and model weights have been preserved.

---

## ⚖️ 10. Simulation Disclosures & Roadmaps

### **✅ Fully Implemented:**
* ML preprocessing pipeline, Winsorization, and XGBoost predictions.
* Explainable AI (SHAP attributions and interpretation mapping).
* API status metrics, audit logs, case status updates, and notes.
* Report downloads (PDF compilation, JSON exports, and CSV backups).

### **⚠️ Simulated (Demonstration Mode):**
* **Watchlist Integrations:** Watchlist matching (I4C, RBI Caution List) is simulated using mock rules for demonstration purposes.
* **Mule Ring Graph Network:** The multi-hop visualization displays an illustrative transaction flow.
* **Emergency CBS Freeze:** CBS webhook triggers return simulated transaction references.

### **🔮 Future Scalability Roadmap (Unimplemented):**
* Streaming data ingestion via Apache Kafka.
* Live enterprise SSO/MFA integrations.
* GNN models for automatic graph routing detection.

---

## 🧪 11. System Verification & Testing
* Tested authentication controls.
* Checked that CSV, JSON, and PDF download endpoints return `HTTP 200 OK`.
* Confirmed sandbox predictions process both custom inputs and JSON payloads correctly.
* Checked console logs to ensure there are no active JavaScript error flags.
