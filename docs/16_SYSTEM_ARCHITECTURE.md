# 🏗️ 16 — END-TO-END SYSTEM ARCHITECTURE

---

## 1. High-Level Architecture Diagram

MuleShield PRO follows a decoupled client-server architecture. The frontend single-page application interacts with a Python Flask REST API server backed by serialized ML model artifacts and an in-memory database index.

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FRONTEND PRESENTATION LAYER                               │
│     Single-Page Application (HTML5 / Vanilla ES6 / Tailwind CSS / Vis.js / Google Fonts)  │
│                                                                                           │
│   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐       │
│   │ Tab 1: Queue   │   │ Tab 2: Sandbox │   │ Tab 3: Network │   │ Tab 4: RegIntel│       │
│   └────────────────┘   └────────────────┘   └────────────────┘   └────────────────┘       │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │ REST API Calls (HTTP JSON)
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 BACKEND API APPLICATION LAYER                             │
│                       Flask Web Application Server (backend/main.py)                      │
│                                                                                           │
│   GET /api/cases        |  GET /api/cases/<id>                                            │
│   POST /api/predict     |  POST /api/cases/<id>/str-draft                                 │
└──────────────────────┬──────────────────────────────────────────────┬─────────────────────┘
                       │ Query Account Cases                          │ Inference Payload
                       ▼                                              ▼
┌──────────────────────────────────────────────┐              ┌─────────────────────────────┐
│          IN-MEMORY DATABASE INDEX            │              │   MULESHIELD RISK ENGINE    │
│              (backend/db.py)                 │              │  (backend/risk_engine.py)   │
│  9,082 Account Profiles & Summary Metrics    │              │  Loads Model & Preprocessor │
└──────────────────────────────────────────────┘              └──────────────┬──────────────┘
                                                                             │ Transform & Predict
                                                                             ▼
                                                              ┌─────────────────────────────┐
                                                              │    SERIALIZED ARTIFACTS     │
                                                              │  mule_shield_model.json     │
                                                              │  preprocessor.pkl           │
                                                              └─────────────────────────────┘
```

---

## 2. Component Responsibility Matrix

| Component | Technology | File Location | Responsibility |
| :--- | :--- | :--- | :--- |
| **HTTP Web Server** | Flask / WSGI | [backend/main.py](file:///a:/Projects/PSB/backend/main.py) | Exposes REST API endpoints and serves frontend dashboard static assets. |
| **Risk Engine** | Python / XGBoost | [backend/risk_engine.py](file:///a:/Projects/PSB/backend/risk_engine.py) | Manages model loading, preprocessor transformation, probability scoring, and SHAP calculation. |
| **In-Memory DB** | Python Dataclass | [backend/db.py](file:///a:/Projects/PSB/backend/db.py) | Indexes 9,082 account profiles and computes dataset summary counts. |
| **Dashboard UI** | HTML / JS / Tailwind | [backend/static/index.html](file:///a:/Projects/PSB/backend/static/index.html) | Single-page UI containing 5 operational tabs, network graph canvas, and CBS freeze actions. |
| **Model Artifacts** | XGBoost JSON / Pickle | [modeling/](file:///a:/Projects/PSB/modeling/) | Serialized model binary, preprocessor pipeline, feature schema, and threshold configuration. |
