import unittest
import json
import time
import sys
import os

sys.path.append('.')
from backend.main import app
from backend.graph_engine import MuleGraph
from backend.database.models import Transaction

# Mock transaction helper class for testing without DB binding
class MockTransaction:
    def __init__(self, id, source, dest, amount, tx_type, timestamp=None):
        from datetime import datetime
        self.id = id
        self.source_account_id = source
        self.destination_account_id = dest
        self.amount = amount
        self.transaction_type = tx_type
        self.timestamp = timestamp or datetime.utcnow()

class TestTransactionGraph(unittest.TestCase):
    def setUp(self):
        # Build simple mock transactions forming a component graph
        self.mock_txs = [
            # Cycle: 1 -> 2 -> 3 -> 1
            MockTransaction(1, 1, 2, 100.0, "UPI"),
            MockTransaction(2, 2, 3, 100.0, "IMPS"),
            MockTransaction(3, 3, 1, 99.0, "RTGS"),
            
            # Fan-In & Fan-Out: 4, 5, 6 -> 10 -> 11, 12
            MockTransaction(4, 4, 10, 50.0, "UPI"),
            MockTransaction(5, 5, 10, 60.0, "UPI"),
            MockTransaction(6, 6, 10, 70.0, "UPI"),
            MockTransaction(7, 10, 11, 80.0, "IMPS"),
            MockTransaction(8, 10, 12, 90.0, "IMPS"),
            
            # Multi-Hop: 20 -> 21 -> 22 -> 23
            MockTransaction(9, 20, 21, 500.0, "RTGS"),
            MockTransaction(10, 21, 22, 490.0, "RTGS"),
            MockTransaction(11, 22, 23, 480.0, "RTGS")
        ]
        self.graph = MuleGraph(self.mock_txs)

    def test_graph_creation(self):
        # Test all nodes are added
        expected_nodes = {1, 2, 3, 4, 5, 6, 10, 11, 12, 20, 21, 22, 23}
        self.assertEqual(self.graph.nodes, expected_nodes)
        
        # Test edges count
        self.assertEqual(len(self.graph.edges), 11)

    def test_graph_updates(self):
        # Verify adding an edge updates the adjacency lists
        txs = list(self.mock_txs)
        txs.append(MockTransaction(12, 23, 24, 470.0, "RTGS"))
        updated_graph = MuleGraph(txs)
        
        self.assertIn(24, updated_graph.nodes)
        self.assertEqual(len(updated_graph.adj[23]), 1)
        self.assertEqual(updated_graph.adj[23][0][0], 24)

    def test_multi_hop_traversal(self):
        # Find paths of length up to 3 starting from 20 (expected path to 23)
        paths = self.graph.find_multihop_paths(20, depth=3)
        
        # Paths should include [20, 21], [20, 21, 22], [20, 21, 22, 23]
        self.assertTrue(any(p == [20, 21] for p in paths))
        self.assertTrue(any(p == [20, 21, 22] for p in paths))
        self.assertTrue(any(p == [20, 21, 22, 23] for p in paths))

    def test_cycle_detection(self):
        # Detect cycles starting from node 1
        cycles = self.graph.detect_cycles(1)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0], [1, 2, 3, 1])

    def test_cluster_detection(self):
        # Nodes in the connected component of node 1 should include 1, 2, 3
        cluster = self.graph.get_cluster(1)
        self.assertEqual(cluster, {1, 2, 3})
        
        # Cluster of 4 should include 4, 5, 6, 10, 11, 12
        cluster_hub = self.graph.get_cluster(4)
        self.assertEqual(cluster_hub, {4, 5, 6, 10, 11, 12})

    def test_large_graph_behavior(self):
        # Generate a large graph containing 5000 nodes and 5000 transactions
        large_txs = []
        for i in range(1, 5001):
            large_txs.append(MockTransaction(i, i, i + 1, 10.0, "UPI"))
            
        start_time = time.time()
        large_graph = MuleGraph(large_txs)
        metrics = large_graph.compute_metrics(2500)
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        print(f"Large Graph (5000 nodes) traversal and metrics computed in: {elapsed_ms:.2f}ms")
        
        # Verify it computes metrics quickly
        self.assertLess(elapsed_ms, 150.0) # Should be well under 150ms
        self.assertEqual(metrics["degree"], 2) # Node 2500 has 1 in-edge and 1 out-edge

    def test_api_graph_route(self):
        client = app.test_client()
        
        # Test unauthorized request gets 401
        res = client.get("/api/cases/9001/graph")
        self.assertEqual(res.status_code, 401)
        
        # Generate token and test authorized access
        from backend.main import create_token
        token = create_token("admin@muleshield.psb", "ADMIN")
        headers = {"Authorization": f"Bearer {token}"}
        
        res = client.get("/api/cases/9001/graph", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        data = res.get_json()
        self.assertIn("metrics", data)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

if __name__ == "__main__":
    unittest.main()
