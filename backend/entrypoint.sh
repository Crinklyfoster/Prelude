#!/bin/sh
set -e

echo "Waiting for database..."

while ! pg_isready \
  -h postgres \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB"
do
  sleep 2
done

echo "Database ready."

echo "Running migrations..."
alembic upgrade head

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
