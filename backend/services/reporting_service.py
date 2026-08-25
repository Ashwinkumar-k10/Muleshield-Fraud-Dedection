import logging
import sys
import os

sys.path.append('.')
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from backend.config import Config
from backend.report_generator import generate_pdf_report

app = Flask(__name__)
CORS(app)

logger = logging.getLogger("reporting-service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logger.addHandler(handler)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "reporting", "status": "UP"}), 200


@app.route("/reports/pdf", methods=["POST", "OPTIONS"])
def generate_report():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json or {}
    case_data = data.get("case_data")

    if not case_data:
        return jsonify({"error": "Missing case_data"}), 400

    try:
        pdf_bytes = generate_pdf_report(case_data)
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        account_id = case_data.get("account_id", "unknown")
        response.headers["Content-Disposition"] = f"attachment; filename=MuleShield_Report_{account_id}.pdf"
        return response
    except Exception as e:
        logger.error(f"Report generation failed for account {case_data.get('account_id')}: {e}")
        return jsonify({
            "error": "Report generation failed",
            "detail": str(e)
        }), 500


if __name__ == "__main__":
    port = Config.REPORTING_SERVICE_PORT
    logger.info(f"Starting Reporting Service on http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, threaded=True)
