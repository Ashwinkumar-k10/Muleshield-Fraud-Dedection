# 🛠️ 23 — COMPLETE TECHNOLOGY STACK

---

## 1. Technology Stack Inventory

MuleShield PRO is constructed using standard Python machine learning, web server, and data science libraries combined with modern frontend web technologies:

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                  SYSTEM TECHNOLOGY STACK                                  │
├───────────────────────────────┬───────────────────────────────┬───────────────────────────┤
│ Technology / Library          │ Version / Source              │ Exact Purpose & Usage     │
├───────────────────────────────┼───────────────────────────────┼───────────────────────────┤
│ Python                        │ 3.11                          │ Core programming runtime  │
│ XGBoost                       │ Native C++ Python Engine      │ Primary ML classifier     │
│ Scikit-Learn                  │ 1.3+                          │ CV splits & preprocessor  │
│ Imbalanced-Learn              │ 0.11+                         │ SMOTE oversampling        │
│ Pandas                        │ 2.0+                          │ Data manipulation         │
│ PyArrow                       │ High-speed engine             │ Fast CSV ingestion        │
│ NumPy                         │ 1.24+                         │ Vector math & clipping    │
│ SciPy                         │ Sparse graph                  │ Cosine group clustering   │
│ SHAP                          │ TreeSHAP                      │ Feature attribution       │
│ Flask                         │ WSGI                          │ Backend REST API host     │
│ Flask-CORS                    │ Extension                     │ Cross-origin security     │
│ Joblib                        │ 1.3+                          │ Pipeline serialization    │
│ HTML5 / JavaScript            │ Vanilla ES6                   │ Single-page UI logic      │
│ Tailwind CSS                  │ CDN                           │ Responsive UI styling     │
│ Vis.js Network                │ CDN (vis-network)             │ Interactive 2D network    │
│ FontAwesome                   │ CDN                           │ Enterprise UI icons       │
│ Google Fonts                  │ Inter & JetBrains Mono        │ Typography & data tables  │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────┘
```

---

## 2. Technology Selection Rationale

1. **XGBoost:** Selected for high-speed histogram split binning, superior tabular performance, and native TreeSHAP support.
2. **Scikit-Learn & Imbalanced-Learn:** Provided standard `StratifiedGroupKFold` splitters and `SMOTE` oversampling.
3. **Flask:** Lightweight, zero-overhead WSGI web framework ideal for embedding ML inference models.
4. **Tailwind CSS & Vis.js:** Allowed building a responsive enterprise dashboard UI with graph network rendering without heavy framework overhead (e.g. React/Angular).
