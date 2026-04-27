#!/bin/sh
set -e

alembic upgrade head
exec gunicorn --bind 0.0.0.0:8000 --workers 4 backend.app:app
