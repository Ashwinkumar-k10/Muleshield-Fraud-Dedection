import unittest
import json
import os
import sys

sys.path.append('.')
from modeling.retrain_pipeline import RetrainingPipeline, POST_INCIDENT_LEAKAGE_FEATURES
from backend.main import app, create_token
from backend.database.connection import SessionLocal
from backend.database.models import ModelRegistry, ModelAudit

class TestControlledRetrainingPipeline(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.pipeline = RetrainingPipeline()
        
        self.admin_token = create_token("admin@muleshield.psb", "ADMIN")
        self.analyst_token = create_token("analyst@muleshield.psb", "ANALYST")
        
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.analyst_headers = {"Authorization": f"Bearer {self.analyst_token}"}

    def test_pipeline_execution_and_no_automatic_deploy(self):
        # 1. Run controlled retraining pipeline
        version_name = f"v2-pipeline-test-{os.urandom(2).hex()}"
        res = self.pipeline.run_pipeline(
            version_name=version_name,
            hyperparameters={"max_depth": 3, "n_estimators": 5, "random_state": 42},
            performed_by="analyst@muleshield.psb"
        )
        
        self.assertEqual(res["version"], version_name)
        self.assertIn("metrics", res)
        self.assertIn("pr_auc", res["metrics"])
        
        # REQUIREMENT: No automatic production deployment! Must be VALIDATED or EXPERIMENTAL!
        self.assertIn(res["approval_status"], ["VALIDATED", "EXPERIMENTAL"])
        self.assertNotEqual(res["approval_status"], "PRODUCTION")

        # Verify entry in database
        db = SessionLocal()
        try:
            entry = db.query(ModelRegistry).filter(ModelRegistry.version == version_name).first()
            self.assertIsNotNone(entry)
            self.assertNotEqual(entry.approval_status, "PRODUCTION")
            
            # Verify audit trail recorded
            audit = db.query(ModelAudit).filter(ModelAudit.version == version_name).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.action, "TRAIN_AND_REGISTER")
        finally:
            db.close()

    def test_rollback_capability_endpoint(self):
        target_v = f"v2-target-{os.urandom(2).hex()}"
        faulty_v = f"v2-faulty-{os.urandom(2).hex()}"
        
        db = SessionLocal()
        try:
            # Create a mock production version and a mock rollback target version
            v_old = ModelRegistry(
                version=target_v,
                model_artifact_path="modeling/model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"pr_auc": 0.88}),
                threshold=0.9899,
                training_config=json.dumps({}),
                validation_status="VALIDATED",
                approval_status="APPROVED"
            )
            v_curr = ModelRegistry(
                version=faulty_v,
                model_artifact_path="modeling/model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"pr_auc": 0.70}),
                threshold=0.9899,
                training_config=json.dumps({}),
                validation_status="PASSED",
                approval_status="PRODUCTION"
            )
            db.add(v_old)
            db.add(v_curr)
            db.commit()
        finally:
            db.close()

        # Trigger rollback via API
        res = self.client.post("/api/model-registry/rollback", json={
            "target_version": target_v
        }, headers=self.admin_headers)
        
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["active_production"], target_v)
        self.assertEqual(data["rolled_back_from"], faulty_v)

        # Verify DB states after rollback
        db = SessionLocal()
        try:
            target_entry = db.query(ModelRegistry).filter(ModelRegistry.version == target_v).first()
            old_prod_entry = db.query(ModelRegistry).filter(ModelRegistry.version == faulty_v).first()
            
            self.assertEqual(target_entry.approval_status, "PRODUCTION")
            self.assertEqual(old_prod_entry.approval_status, "APPROVED")
            
            # Verify Rollback audit log
            audit = db.query(ModelAudit).filter(ModelAudit.action == "ROLLBACK").order_by(ModelAudit.timestamp.desc()).first()
            self.assertIsNotNone(audit)
            self.assertEqual(audit.version, target_v)
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
