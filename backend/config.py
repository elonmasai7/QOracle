import os
from datetime import timedelta


class Config:
    ENV = os.getenv("ENV", "dev")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-too")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://quantumrisk:quantumrisk@postgres:5432/quantumrisk",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200/hour")

    QUANTUM_MODE = os.getenv("QUANTUM_MODE", "hybrid")
    IBM_QUANTUM_CHANNEL = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum")
    IBM_QUANTUM_INSTANCE = os.getenv("IBM_QUANTUM_INSTANCE", "")
    IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN", "")

    AES_KEY = os.getenv("AES_KEY", "00000000000000000000000000000000")
    TLS_MIN_VERSION = "1.3"

    MODEL_REGISTRY_PATH = os.getenv("MODEL_REGISTRY_PATH", "/app/backend/ml/registry")
    ENABLE_SHAP = os.getenv("ENABLE_SHAP", "false").lower() == "true"
