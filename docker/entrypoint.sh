#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
sleep 0.5

echo "Running migrations"
poetry run alembic upgrade head

echo "Starting application"
exec "$@"
