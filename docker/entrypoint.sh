#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running migrations"
poetry run alembic upgrade head

echo "Starting application"
exec "$@"
