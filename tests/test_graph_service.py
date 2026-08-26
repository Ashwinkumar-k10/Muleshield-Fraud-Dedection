import unittest
import json
import sys
import os

sys.path.append('.')
from backend.services.graph_service import app as graph_app
from backend.graph_engine import MuleGraph


class MockTransaction:
    def __init__(self, id, source, dest, amount, tx_type, timestamp=None):
        from datetime import datetime
        self.id = id
        self.source_account_id = source
        self.destination_account_id = dest
        self.amount = amount
        self.transaction_type = tx_type
        self.timestamp = timestamp or datetime.utcnow()


class TestGraphService(unittest.TestCase):
    def setUp(self):
        self.client = graph_app.test_client()
        self.mock_txs = [
            MockTransaction(1, 1, 2, 100.0, "UPI"),
            MockTransaction(2, 2, 3, 100.0, "IMPS"),
            MockTransaction(3, 3, 1, 99.0, "RTGS"),
            MockTransaction(4, 4, 10, 50.0, "UPI"),
            MockTransaction(5, 5, 10, 60.0, "UPI"),
            MockTransaction(6, 10, 11, 80.0, "IMPS"),
        ]

    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["service"], "graph")
        self.assertEqual(data["status"], "UP")

    def test_metrics_computation(self):
        tx_payload = []
        for tx in self.mock_txs:
            tx_payload.append({
                "id": tx.id,
                "source_account_id": tx.source_account_id,
                "destination_account_id": tx.destination_account_id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            })
        res = self.client.post("/metrics", json={
            "account_id": 1,
            "transactions": tx_payload
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("center_metrics", data)
        self.assertIn("node_metrics", data)
        self.assertEqual(data["center_metrics"]["account_id"], 1)
        self.assertIn("node_metrics", data)

    def test_missing_payload(self):
        res = self.client.post("/metrics", json={})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_dict_transactions_accepted(self):
        tx_payload = [
            {"id": 1, "source_account_id": 1, "destination_account_id": 2, "amount": 100.0, "transaction_type": "UPI", "timestamp": "2026-01-01 00:00:00 UTC"},
            {"id": 2, "source_account_id": 2, "destination_account_id": 1, "amount": 99.0, "transaction_type": "RTGS", "timestamp": "2026-01-01 01:00:00 UTC"}
        ]
        res = self.client.post("/metrics", json={
            "account_id": 1,
            "transactions": tx_payload
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("center_metrics", data)


if __name__ == "__main__":
    unittest.main()
