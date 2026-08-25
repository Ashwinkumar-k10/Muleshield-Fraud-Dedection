import unittest
import numpy as np
import pandas as pd
import json
import sys

sys.path.append('.')
from backend.drift_engine import MuleShieldDriftMonitor
from backend.main import app
from backend.main import create_token

class TestModelDriftMonitoring(unittest.TestCase):
    def setUp(self):
        self.monitor = MuleShieldDriftMonitor()
        self.core_features = self.monitor.core_features
        self.client = app.test_client()
        self.analyst_token = create_token("analyst@muleshield.psb", "ANALYST")
        self.analyst_headers = {"Authorization": f"Bearer {self.analyst_token}"}

    def test_psi_calculation(self):
        # 1. No shift test
        expected = np.random.normal(0, 1, 1000)
        actual = np.random.normal(0, 1, 1000)
        psi_healthy = self.monitor.calculate_psi(expected, actual)
        self.assertTrue(psi_healthy < 0.1, f"PSI should be healthy (<0.1) but got {psi_healthy}")
        
        # 2. Significant shift test
        actual_shifted = np.random.normal(1.5, 1, 1000)
        psi_critical = self.monitor.calculate_psi(expected, actual_shifted)
        self.assertTrue(psi_critical >= 0.25, f"PSI should be critical (>=0.25) but got {psi_critical}")

    def test_healthy_scenario(self):
        # Sample healthy features directly from reference features
        current_features = self.monitor.reference_features.sample(n=500, replace=True, random_state=42)
        np.random.seed(42)
        current_probs = np.random.choice(self.monitor.reference_probs, size=500, replace=True)
        
        results = self.monitor.monitor_drift(current_features, current_probs)
        self.assertEqual(results["status"], "HEALTHY")
        self.assertIn("No action required", results["recommendation"])

    def test_warning_scenario(self):
        # Shift a single feature distribution moderately by flipping 200 values
        current_features = self.monitor.reference_features.sample(n=500, replace=True, random_state=42).copy()
        vals = current_features["F994"].values.copy()
        vals[:200] = 1 - vals[:200]
        current_features["F994"] = vals
        np.random.seed(42)
        current_probs = np.random.choice(self.monitor.reference_probs, size=500, replace=True)
        
        results = self.monitor.monitor_drift(current_features, current_probs)
        self.assertEqual(results["status"], "WARNING")
        self.assertTrue(results["feature_drift"]["F994"]["drift_detected"])

    def test_critical_scenario_multiple_features(self):
        # Shift three features significantly to trigger critical feature drift
        current_features = self.monitor.reference_features.sample(n=500, replace=True, random_state=42).copy()
        current_features["F994"] = current_features["F994"] + 1.5
        current_features["F3598"] = current_features["F3598"] + 1.5
        current_features["F1319"] = current_features["F1319"] + 1.5
        np.random.seed(42)
        current_probs = np.random.choice(self.monitor.reference_probs, size=500, replace=True)
        
        results = self.monitor.monitor_drift(current_features, current_probs)
        self.assertEqual(results["status"], "CRITICAL")
        self.assertIn("Multiple core features show distribution shifts", results["recommendation"])

    def test_critical_scenario_prediction_drift(self):
        # Shift probabilities to high risk (skewed to high risk)
        current_features = self.monitor.reference_features.sample(n=500, replace=True, random_state=42)
        current_probs = np.random.beta(5, 2, size=500)
        
        results = self.monitor.monitor_drift(current_features, current_probs)
        self.assertEqual(results["status"], "CRITICAL")
        self.assertTrue(results["prediction_drift"]["psi"] >= 0.25)
        self.assertIn("Major shift in prediction scores", results["recommendation"])

    def test_drift_api_endpoint(self):
        # Assert API works and returns the structured dictionary
        res = self.client.get("/api/model/drift", headers=self.analyst_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)
        self.assertIn("feature_drift", data)
        self.assertIn("prediction_drift", data)
        self.assertIn("performance", data)
        self.assertIn("model_version", data)

if __name__ == "__main__":
    unittest.main()
