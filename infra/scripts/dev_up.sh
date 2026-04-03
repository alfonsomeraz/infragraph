#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

# Copy env if missing
[ -f .env ] || cp .env.example .env

docker compose up -d postgres
echo "Waiting for Postgres..."
until docker compose exec postgres pg_isready -U infragraph > /dev/null 2>&1; do
  sleep 1
done

echo "Running migrations..."
cd backend && .venv/bin/alembic upgrade head
echo "Ready — run 'make dev' or 'uvicorn app.main:app --reload'"
