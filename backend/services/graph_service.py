import logging
import sys
import os
from datetime import datetime

sys.path.append('.')
from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.config import Config
from backend.graph_engine import MuleGraph

app = Flask(__name__)
CORS(app)

logger = logging.getLogger("graph-service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.addHandler(handler)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "graph", "status": "UP"}), 200


@app.route("/metrics", methods=["POST", "OPTIONS"])
def compute_metrics():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json or {}
    account_id = data.get("account_id")
    transactions = data.get("transactions", [])

    if account_id is None or not transactions:
        return jsonify({"error": "Missing account_id or transactions"}), 400

    try:
        graph = MuleGraph(transactions)
        center_metrics = graph.compute_metrics(account_id)
        cluster_nodes = center_metrics.get("cluster_nodes", [account_id])
        node_metrics = {nid: graph.compute_metrics(nid) for nid in cluster_nodes}
        return jsonify({
            "center_metrics": center_metrics,
            "node_metrics": node_metrics
        }), 200
    except Exception as e:
        logger.error(f"Graph computation failed for account {account_id}: {e}")
        return jsonify({
            "error": "Graph computation failed",
            "detail": str(e)
        }), 500


if __name__ == "__main__":
    port = Config.GRAPH_SERVICE_PORT
    logger.info(f"Starting Graph Service on http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, threaded=True)
