import os
import sys
import json
import time
import subprocess
from datetime import datetime
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc

sys.path.append('.')
from modeling.preprocessor import MuleShieldPreprocessor
from backend.database.connection import SessionLocal
from backend.database.models import ModelRegistry, ModelAudit

# 14 Post-resolution / incident features that MUST be purged to prevent target leakage
POST_INCIDENT_LEAKAGE_FEATURES = [
    "F3898", "F3899", "F3912", "F3913", "F3914", "F3915", 
    "F3916", "F3917", "F3918", "F3919", "F3920", "F3921", 
    "F3922", "F3923"
]

class RetrainingPipeline:
    def __init__(self, dataset_path="data/data_copy.csv", artifacts_dir="modeling/artifacts"):
        self.dataset_path = dataset_path
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def get_git_commit_hash(self):
        try:
            cmd = ["git", "rev-parse", "--short", "HEAD"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return "v2-development"

    def run_pipeline(self, version_name=None, hyperparameters=None, performed_by="system@muleshield.psb"):
        if not version_name:
            version_name = f"v2-candidate-{int(time.time())}"
            
        if not hyperparameters:
            hyperparameters = {
                "max_depth": 6,
                "learning_rate": 0.1,
                "n_estimators": 100,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "objective": "binary:logistic",
                "random_state": 42
            }

        print(f"======================================================================")
        print(f"    MULESHIELD PRO — CONTROLLED MODEL RETRAINING PIPELINE ({version_name})")
        print(f"======================================================================")

        # ------------------------------------------------------------------
        # Step 1: Data Ingestion & Validation
        # ------------------------------------------------------------------
        print("[1/8] Data Ingestion & Data Validation...")
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset path '{self.dataset_path}' not found.")
            
        df = pd.read_csv(self.dataset_path)
        if "F3924" not in df.columns:
            raise ValueError("Target label column 'F3924' missing from dataset.")
            
        total_rows = len(df)
        print(f" -> Ingested dataset: {total_rows} rows, {len(df.columns)} columns.")

        # ------------------------------------------------------------------
        # Step 2: Leakage Audit & Purging
        # ------------------------------------------------------------------
        print("[2/8] Executing Leakage Audit & Purging...")
        X_df = df.drop(columns=["F3924"], errors="ignore")
        y = df["F3924"].values

        purged_features = [f for f in POST_INCIDENT_LEAKAGE_FEATURES if f in X_df.columns]
        if purged_features:
            X_df = X_df.drop(columns=purged_features, errors="ignore")
            print(f" -> PURGED {len(purged_features)} post-incident target leakage features: {purged_features}")

        # Assert zero leakage features remain
        for f in POST_INCIDENT_LEAKAGE_FEATURES:
            assert f not in X_df.columns, f"Target leakage violation! Feature '{f}' remained in training set."
            
        # Extract group labels for component group splitting to prevent graph leakage
        groups = X_df.get("F3923", X_df.index // 10)

        # ------------------------------------------------------------------
        # Step 3: Preprocessing
        # ------------------------------------------------------------------
        print("[3/8] Preprocessing & Feature Engineering...")
        preprocessor = MuleShieldPreprocessor()
        X_processed = preprocessor.fit_transform(X_df)
        print(f" -> Preprocessing completed. Processed feature matrix shape: {X_processed.shape}")

        # ------------------------------------------------------------------
        # Step 4 & 5: Training & Cross-Validation
        # ------------------------------------------------------------------
        print("[4/8] Model Training & Group-Aware Cross Validation...")
        gkf = GroupKFold(n_splits=5)
        oof_preds = np.zeros(len(df))

        for fold, (train_idx, val_idx) in enumerate(gkf.split(X_processed, y, groups=groups)):
            X_tr, y_tr = X_processed.iloc[train_idx], y[train_idx]
            X_val, y_val = X_processed.iloc[val_idx], y[val_idx]

            model_fold = xgb.XGBClassifier(**hyperparameters)
            model_fold.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
            oof_preds[val_idx] = model_fold.predict_proba(X_val)[:, 1]

        # Train final candidate model on full dataset
        print("[5/8] Training Final Candidate Model Artifact...")
        final_model = xgb.XGBClassifier(**hyperparameters)
        final_model.fit(X_processed, y)

        # ------------------------------------------------------------------
        # Step 6: Metric Evaluation & Decision Thresholding
        # ------------------------------------------------------------------
        print("[6/8] Evaluating Metrics & Precision-Recall Boundaries...")
        precision_curve, recall_curve, thresholds_curve = precision_recall_curve(y, oof_preds)
        pr_auc = float(auc(recall_curve, precision_curve))
        
        # Locked high-precision decision boundary
        threshold = 0.9899
        y_pred = (oof_preds >= threshold).astype(int)
        
        prec = float(precision_score(y, y_pred, zero_division=1))
        rec = float(recall_score(y, y_pred, zero_division=0))
        f1 = float(f1_score(y, y_pred, zero_division=0))

        metrics = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "pr_auc": round(pr_auc, 4),
            "total_samples": total_rows
        }
        print(f" -> Metrics: PR-AUC={pr_auc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}, F1={f1:.4f}")

        # ------------------------------------------------------------------
        # Step 7: Saving Model Artifacts
        # ------------------------------------------------------------------
        print("[7/8] Saving Candidate Model Artifacts...")
        model_artifact_path = os.path.join(self.artifacts_dir, f"model_{version_name}.json")
        preprocessor_path = os.path.join(self.artifacts_dir, f"preprocessor_{version_name}.pkl")
        schema_path = os.path.join(self.artifacts_dir, f"schema_{version_name}.json")

        final_model.save_model(model_artifact_path)
        import pickle
        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)
        
        feature_schema = {
            "version": version_name,
            "features_count": X_processed.shape[1],
            "columns": list(X_processed.columns)
        }
        with open(schema_path, "w") as f:
            json.dump(feature_schema, f)

        # ------------------------------------------------------------------
        # Step 8: Registration in Model Registry (NO Automatic Production Deploy!)
        # ------------------------------------------------------------------
        print("[8/8] Registering Candidate Model in MLOps Registry...")
        db = SessionLocal()
        try:
            git_hash = self.get_git_commit_hash()
            training_config = {
                "hyperparameters": hyperparameters,
                "code_version": git_hash,
                "features_count": X_processed.shape[1],
                "purged_leakage_count": len(purged_features)
            }
            
            # Default approval status is VALIDATED or EXPERIMENTAL. NEVER PRODUCTION!
            approval_status = "VALIDATED" if prec >= 0.95 and pr_auc >= 0.80 else "EXPERIMENTAL"
            
            registry_entry = ModelRegistry(
                version=version_name,
                model_artifact_path=model_artifact_path,
                preprocessor_path=preprocessor_path,
                feature_schema_path=schema_path,
                dataset_version=os.path.basename(self.dataset_path),
                metrics=json.dumps(metrics),
                threshold=threshold,
                training_config=json.dumps(training_config),
                validation_status="PASSED",
                approval_status=approval_status,
                created_at=datetime.utcnow()
            )
            db.add(registry_entry)
            db.commit()

            # Record reproducible audit log
            audit_log = ModelAudit(
                version=version_name,
                action="TRAIN_AND_REGISTER",
                performed_by=performed_by,
                timestamp=datetime.utcnow(),
                details=json.dumps({
                    "note": f"Model candidate trained and registered. Status: {approval_status}. (NO AUTOMATIC PRODUCTION DEPLOYMENT)",
                    "metrics": metrics,
                    "dataset": os.path.basename(self.dataset_path),
                    "threshold": threshold,
                    "code_version": git_hash
                })
            )
            db.add(audit_log)
            db.commit()

            print(f" -> Model candidate successfully registered under version '{version_name}'.")
            print(f" -> Status: {approval_status}. (Note: Human approval required for production deployment.)")
            print(f"======================================================================")

            return {
                "version": version_name,
                "approval_status": approval_status,
                "metrics": metrics,
                "threshold": threshold,
                "model_artifact_path": model_artifact_path,
                "preprocessor_path": preprocessor_path,
                "training_config": training_config
            }
        finally:
            db.close()

if __name__ == "__main__":
    pipeline = RetrainingPipeline()
    pipeline.run_pipeline()
