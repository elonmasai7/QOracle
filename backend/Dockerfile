FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY sample_data /app/sample_data
COPY alembic.ini /app/alembic.ini
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["sh", "/app/backend/start.sh"]
