import os


class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///muleshield_local.db")

    ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://localhost:8080")
    GRAPH_SERVICE_URL = os.environ.get("GRAPH_SERVICE_URL")
    REPORTING_SERVICE_URL = os.environ.get("REPORTING_SERVICE_URL")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "muleshield-secure-secret-2026-xyz").encode()

    GATEWAY_PORT = int(os.environ.get("PORT", 8000))
    ML_SERVICE_PORT = int(os.environ.get("ML_SERVICE_PORT", 8080))
    GRAPH_SERVICE_PORT = int(os.environ.get("GRAPH_SERVICE_PORT", 8081))
    REPORTING_SERVICE_PORT = int(os.environ.get("REPORTING_SERVICE_PORT", 8082))

    SERVICE_TIMEOUT = int(os.environ.get("SERVICE_TIMEOUT", 5))

    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
