FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY worker /app/worker
COPY sample_data /app/sample_data
COPY alembic.ini /app/alembic.ini
ENV PYTHONPATH=/app
CMD ["celery", "-A", "backend.tasks.celery", "worker", "--loglevel=INFO", "--concurrency=4"]
