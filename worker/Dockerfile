FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY worker /app/worker
COPY sample_data /app/sample_data
ENV PYTHONPATH=/app
CMD ["celery", "-A", "backend.tasks.celery", "worker", "--loglevel=INFO", "--concurrency=4"]
