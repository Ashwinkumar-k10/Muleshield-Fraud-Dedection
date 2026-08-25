import unittest
import json
import sys

sys.path.append('.')
from backend.main import app
from backend.database.connection import SessionLocal
from backend.database.models import ModelRegistry, ModelAudit, Base
from backend.main import create_token

class TestMLOpsRegistry(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        
        # Build authentication tokens
        self.admin_token = create_token("admin@muleshield.psb", "ADMIN")
        self.analyst_token = create_token("analyst@muleshield.psb", "ANALYST")
        
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.analyst_headers = {"Authorization": f"Bearer {self.analyst_token}"}
        
        # Register a temporary candidate model for tests
        db = SessionLocal()
        try:
            # Clean up old registrations if present
            db.query(ModelAudit).delete()
            db.query(ModelRegistry).delete()
            
            # Re-seed stable V1 BASELINE
            v1 = ModelRegistry(
                version="V1 BASELINE",
                model_artifact_path="modeling/mule_shield_model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"precision": 1.0, "recall": 0.6164, "f1": 0.7586, "pr_auc": 0.8807}),
                threshold=0.9899,
                training_config=json.dumps({"params": "v1"}),
                validation_status="PASSED",
                approval_status="PRODUCTION"
            )
            db.add(v1)
            db.commit()
        finally:
            db.close()

    def test_get_registry_list(self):
        res = self.client.get("/api/model-registry", headers=self.analyst_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("models", data)
        self.assertTrue(len(data["models"]) >= 1)
        self.assertEqual(data["models"][0]["version"], "V1 BASELINE")

    def test_register_candidate_model(self):
        payload = {
            "version": "v2.0.0-GraphSAGE",
            "model_artifact_path": "modeling/gnn_experiment.py",
            "preprocessor_path": "modeling/preprocessor.pkl",
            "feature_schema_path": "modeling/feature_schema.json",
            "dataset_version": "data_copy.csv",
            "metrics": {"precision": 1.0, "recall": 0.0857, "f1": 0.1579, "pr_auc": 0.4836},
            "threshold": 0.9899,
            "training_config": {"epochs": 100, "lr": 0.01},
            "validation_status": "PASSED",
            "approval_status": "EXPERIMENTAL"
        }
        res = self.client.post("/api/model-registry", json=payload, headers=self.analyst_headers)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn("successfully registered", data["message"])

    def test_promotion_policy_blocks_direct_production_deploy(self):
        # Register a new experimental candidate model
        db = SessionLocal()
        try:
            cand = ModelRegistry(
                version="v2-experimental",
                model_artifact_path="modeling/model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"pr_auc": 0.5}),
                threshold=0.9899,
                training_config=json.dumps({}),
                validation_status="VALIDATED",
                approval_status="EXPERIMENTAL"
            )
            db.add(cand)
            db.commit()
        finally:
            db.close()
            
        # Attempting to promote v2-experimental directly to PRODUCTION must fail!
        res = self.client.post("/api/model-registry/v2-experimental/approve", json={"status": "PRODUCTION"}, headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("Only APPROVED models can be deployed to PRODUCTION", data["error"])

    def test_promotion_lifecycle_success(self):
        # Register a validated model candidate
        db = SessionLocal()
        try:
            cand = ModelRegistry(
                version="v2-validated",
                model_artifact_path="modeling/model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"pr_auc": 0.95}),
                threshold=0.9899,
                training_config=json.dumps({}),
                validation_status="VALIDATED",
                approval_status="VALIDATED"
            )
            db.add(cand)
            db.commit()
        finally:
            db.close()
            
        # 1. Promote to APPROVED
        res1 = self.client.post("/api/model-registry/v2-validated/approve", json={"status": "APPROVED"}, headers=self.admin_headers)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.get_json()["new_status"], "APPROVED")
        
        # 2. Promote from APPROVED to PRODUCTION
        res2 = self.client.post("/api/model-registry/v2-validated/approve", json={"status": "PRODUCTION"}, headers=self.admin_headers)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.get_json()["new_status"], "PRODUCTION")

    def test_model_comparison(self):
        # Register a candidate
        db = SessionLocal()
        try:
            cand = ModelRegistry(
                version="v2-compare",
                model_artifact_path="modeling/model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"pr_auc": 0.85, "precision": 1.0}),
                threshold=0.9899,
                training_config=json.dumps({}),
                validation_status="VALIDATED",
                approval_status="APPROVED"
            )
            db.add(cand)
            db.commit()
        finally:
            db.close()
            
        res = self.client.get("/api/model-registry/compare?candidate=v2-compare", headers=self.analyst_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("production", data)
        self.assertIn("candidate", data)
        self.assertEqual(data["production"]["version"], "V1 BASELINE")
        self.assertEqual(data["candidate"]["version"], "v2-compare")

    def test_audit_logging(self):
        # Trigger an action
        db = SessionLocal()
        try:
            cand = ModelRegistry(
                version="v2-audit",
                model_artifact_path="modeling/model.json",
                preprocessor_path="modeling/preprocessor.pkl",
                feature_schema_path="modeling/feature_schema.json",
                dataset_version="data_copy.csv",
                metrics=json.dumps({"pr_auc": 0.99}),
                threshold=0.9899,
                training_config=json.dumps({}),
                validation_status="VALIDATED",
                approval_status="VALIDATED"
            )
            db.add(cand)
            db.commit()
        finally:
            db.close()
            
        self.client.post("/api/model-registry/v2-audit/approve", json={"status": "APPROVED"}, headers=self.admin_headers)
        
        # Verify audit is logged
        res = self.client.get("/api/model-registry/audits", headers=self.analyst_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(len(data["audits"]) >= 1)
        self.assertEqual(data["audits"][0]["version"], "v2-audit")
        self.assertEqual(data["audits"][0]["action"], "TRANSITION_TO_APPROVED")

if __name__ == "__main__":
    unittest.main()
