#!/bin/bash
set -e

echo "🚀 Starting Santaane API (PROD)"

# 1️⃣ Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# 2️⃣ Run migrations ONLY if explicitly enabled
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "📦 Running database migrations..."
  alembic upgrade head
  echo "✅ Migrations done"
fi

# 3️⃣ Start FastAPI
echo "🎯 Starting FastAPI application"
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 
