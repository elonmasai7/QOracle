import os
from pathlib import Path


os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/quantumrisk-test.db")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

test_db_path = Path("/tmp/quantumrisk-test.db")
if test_db_path.exists():
    test_db_path.unlink()
