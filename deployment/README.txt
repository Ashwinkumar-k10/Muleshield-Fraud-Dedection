MuleShield PRO — Standalone Deployment Package
====================================================

This package provides a zero-dependency offline inference package for MuleShield PRO.

Directory Structure:
--------------------
deployment/
├── run_model.py                # Portable CLI inference script
├── README.txt                  # Deployment package instructions
├── sample_data.csv             # Offline sample account data
└── modeling/
    ├── mule_shield_model.json  # Champion XGBoost binary model
    ├── preprocessor.pkl        # Serialized preprocessor transformer
    ├── feature_schema.json     # 6,820 aligned feature schema
    └── model_config.json       # Decision threshold metadata (0.9899)

How to Run Standalone Inference:
--------------------------------
Run the following command from the project root or deployment folder:

    python deployment/run_model.py

Requirements:
-------------
- Python 3.8+
- pandas, numpy, xgboost, scikit-learn, joblib, pyarrow
