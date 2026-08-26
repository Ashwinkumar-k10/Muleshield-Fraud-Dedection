# 🏛️ MuleShield PRO V2 — System & Database Architecture

This document describes the design patterns, database schemas, and compatibility mappings implemented for **MuleShield PRO V2** to support persistent data structures.

---

## 🏗️ 1. Layered Architecture

MuleShield PRO V2 decouples REST endpoints from database transactions using a clean layered architecture:

```
  REST API (backend/main.py)
       │
       ▼
  SERVICE LAYER (backend/db.py - MuleDatabase Facade)
       │
       ▼
  REPOSITORY LAYER (backend/database/repositories.py)
       │
       ▼
  OR-MAPPING LAYER (SQLAlchemy Session Manager)
       │
       ▼
  DATABASE STORAGE (PostgreSQL / local SQLite fallback)
```

### **1.1 Layer Responsibilities**
* **REST API:** Handles HTTP routing, input validation, and JSON serialization.
* **Service Facade:** Provides backward-compatible interfaces for the API, seeds database tables on startup, and coordinates actions across multiple repositories.
* **Repository Layer:** Abstract classes containing parameterized database operations (queries, updates, appends).
* **Database Engine:** Connection manager loading environment variables from `.env` and managing database connection pools.

---

## 🗄️ 2. Relational Database Schema

The database schema is defined in [`backend/database/models.py`](file:///a:/Projects/PSB/backend/database/models.py). The entity relationship structure is detailed below:

```
   ┌───────────────┐          ┌───────────────┐          ┌─────────────────┐
   │    accounts   │ ◄─────── │     cases     │ ◄─────── │  invest_events  │
   │  (raw attrs)  │          │ (risk, status)│          │ (timeline log)  │
   └──────┬────────┘          └───────────────┘          └─────────────────┘
          │
          ├──────────────────►┌─────────────────┐
          │                   │ risk_predictions│
          │                   └─────────────────┘
          │
          └──────────────────►┌─────────────────┐
                              │shap_explanations│
                              └─────────────────┘
```

### **2.1 Tables & Schema Specifications**

#### **`accounts`**
* Stores raw account behavioral features before preprocessing.
* **Columns:**
  * `account_id` (Integer, Primary Key)
  * `attributes` (JSON, Stores feature key-value pairs)
  * `created_at` (DateTime)

#### **`cases`**
* Manages alert lifecycle states and analyst triage details.
* **Columns:**
  * `id` (Integer, Primary Key)
  * `account_id` (Integer, Foreign Key to `accounts.account_id`, Unique)
  * `risk_score` (Float)
  * `tier` (String)
  * `status` (String: `NEW`, `TRIAGED`, `UNDER REVIEW`, `ESCALATED`, `CLEARED`, `CLOSED`)
  * `assigned_analyst` (String)
  * `created_at` (DateTime)
  * `action` (String)
  * `notes` (JSON, List of note dicts)

#### **`risk_predictions`**
* Records ML prediction history logs.
* **Columns:**
  * `id` (Integer, Primary Key)
  * `account_id` (Integer, Foreign Key to `accounts.account_id`)
  * `risk_score` (Float)
  * `tier` (String)
  * `action` (String)
  * `exceeds_threshold` (Boolean)
  * `created_at` (DateTime)

#### **`shap_explanations`**
* Caches TreeSHAP attribution lists.
* **Columns:**
  * `id` (Integer, Primary Key)
  * `account_id` (Integer, Foreign Key to `accounts.account_id`)
  * `features` (JSON, Array of top anomaly feature keys)
  * `created_at` (DateTime)

#### **`investigation_events`**
* Chronological timeline log for each case.
* **Columns:**
  * `id` (Integer, Primary Key)
  * `account_id` (Integer, Foreign Key to `accounts.account_id`)
  * `timestamp` (DateTime)
  * `event` (String: e.g., Case Ingestion, Note Added, Status Updated)
  * `detail` (Text)

#### **`audit_logs`**
* System operations log.
* **Columns:**
  * `id` (Integer, Primary Key)
  * `timestamp` (DateTime)
  * `actor` (String: analyst identifier)
  * `action` (String: action performed)
  * `case_id` (String)
  * `status` (String: success/error status)

---

## 🔌 3. Database Seeding & Compatibility Mappings

### **3.1 Seeding Process**
When the server starts:
1. `MuleDatabase` instantiates.
2. Runs `init_db()`, which registers the SQLAlchemy models and creates the tables if they do not exist.
3. Checks if the `cases` table is empty.
4. If empty, the system reads `data/data_copy.csv`, processes the rows through the preprocessing pipeline, generates XGBoost risk scores, and writes the initial case records, predictions, SHAP explanations, and timeline events to the database.

### **3.2 Dual-Engine Fallback Strategy**
To maintain stability during development, the connection manager supports a database fallback strategy:
* Reads `DATABASE_URL` from the `.env` file.
* If a PostgreSQL connection string (e.g., `postgresql://...`) is provided, it connects to the PostgreSQL database.
* If the environment variable is missing, it falls back to a local SQLite database (`sqlite:///muleshield_local.db`), allowing the system to run locally without a running PostgreSQL instance.
