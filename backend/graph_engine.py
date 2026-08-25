import collections
import time
from datetime import datetime

class MuleGraph:
    def __init__(self, transactions):
        self.adj = collections.defaultdict(list)
        self.rev_adj = collections.defaultdict(list)
        self.nodes = set()
        self.edges = []
        
        for tx in transactions:
            src = tx.source_account_id
            dst = tx.destination_account_id
            self.nodes.add(src)
            self.nodes.add(dst)
            self.edges.append({
                "id": tx.id,
                "source": src,
                "destination": dst,
                "amount": tx.amount,
                "type": tx.transaction_type,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            self.adj[src].append((dst, tx.amount, tx.timestamp))
            self.rev_adj[dst].append((src, tx.amount, tx.timestamp))

    def compute_metrics(self, account_id):
        # 1. Degree, Fan-in, Fan-out
        fan_out = len(self.adj.get(account_id, []))
        fan_in = len(self.rev_adj.get(account_id, []))
        degree = fan_out + fan_in
        
        # 2. Transaction Velocity & Volume
        all_txs = [e for e in self.edges if e["source"] == account_id or e["destination"] == account_id]
        total_volume = sum(e["amount"] for e in all_txs)
        velocity = len(all_txs)
        
        # 3. Centrality (Degree Centrality)
        total_nodes = len(self.nodes)
        centrality = degree / (total_nodes - 1) if total_nodes > 1 else 0.0
        
        # 4. Cycle Detection
        cycles = self.detect_cycles(account_id)
        
        # 5. Multi-hop Paths (depth=3)
        paths = self.find_multihop_paths(account_id, depth=3)
        
        # 6. Cluster Nodes (connected component)
        cluster = self.get_cluster(account_id)
        
        # 7. Suspicious Signals ( money mule risk indicators )
        signals = []
        if fan_in >= 4:
            signals.append("High Fan-In (Potential Aggregation Hub)")
        if fan_out >= 4:
            signals.append("High Fan-Out (Potential Layering Node)")
        if len(cycles) > 0:
            signals.append("Circular Flow (Cycle Detected)")
        if self.detect_rapid_movement(account_id):
            signals.append("Rapid Fund Movement (Potential Pass-Through)")
            
        return {
            "account_id": account_id,
            "degree": degree,
            "fan_in": fan_in,
            "fan_out": fan_out,
            "total_volume": total_volume,
            "velocity": velocity,
            "centrality": round(centrality, 4),
            "cycles": cycles,
            "paths": paths,
            "cluster_nodes": list(cluster),
            "signals": signals
        }

    def get_cluster(self, start_node):
        visited = {start_node}
        queue = collections.deque([start_node])
        while queue:
            node = queue.popleft()
            for neighbor, _, _ in self.adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
            for neighbor, _, _ in self.rev_adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    def detect_cycles(self, start_node, max_depth=5):
        cycles = []
        path = [start_node]
        visited = set()
        
        def dfs(node, current_depth):
            if current_depth >= max_depth:
                return
            for neighbor, _, _ in self.adj.get(node, []):
                if neighbor == start_node and len(path) > 1:
                    cycles.append(list(path) + [start_node])
                elif neighbor not in visited and neighbor not in path:
                    path.append(neighbor)
                    dfs(neighbor, current_depth + 1)
                    path.pop()
                    
        dfs(start_node, 0)
        return cycles[:3]

    def find_multihop_paths(self, start_node, depth=3):
        paths = []
        path = [start_node]
        
        def dfs(node, current_depth):
            if current_depth >= depth:
                return
            for neighbor, _, _ in self.adj.get(node, []):
                if neighbor not in path:
                    path.append(neighbor)
                    paths.append(list(path))
                    dfs(neighbor, current_depth + 1)
                    path.pop()
                    
        dfs(start_node, 0)
        return paths[:5]

    def detect_rapid_movement(self, account_id):
        inflows = sorted(self.rev_adj.get(account_id, []), key=lambda x: x[2])
        outflows = sorted(self.adj.get(account_id, []), key=lambda x: x[2])
        
        for _, in_amt, in_time in inflows:
            for _, out_amt, out_time in outflows:
                if out_time > in_time:
                    diff_seconds = (out_time - in_time).total_seconds()
                    # Outflow within 6 hours of inflow
                    if diff_seconds <= 21600:
                        return True
        return False
