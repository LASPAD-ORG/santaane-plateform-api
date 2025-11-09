#!/bin/bash
set -e

echo "🚀 Starting Santaane API..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
max_retries=30
counter=0

# Check PostgreSQL directly (not through PGBouncer)
echo "Checking connection to db:5432..."

until pg_isready -h db -p 5432 -U "$POSTGRES_USER" 2>/dev/null || [ $counter -eq $max_retries ]; do
  counter=$((counter+1))
  echo "PostgreSQL is unavailable - attempt $counter/$max_retries"
  sleep 2
done

if [ $counter -eq $max_retries ]; then
  echo "❌ Failed to connect to PostgreSQL after $max_retries attempts"
  exit 1
fi

echo "✅ PostgreSQL is ready!"

# Wait a bit more for PGBouncer to be ready
echo "⏳ Waiting for PGBouncer to be ready..."
sleep 3
echo "✅ PGBouncer should be ready!"

# Run Alembic migrations
echo "📦 Running database migrations..."
poetry run alembic upgrade head

if [ $? -eq 0 ]; then
  echo "✅ Migrations completed successfully!"
else
  echo "❌ Migration failed!"
  exit 1
fi

# Start the application
echo "🎯 Starting FastAPI application..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
