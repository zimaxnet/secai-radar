#!/usr/bin/env bash
# Path 1 — Step 1: apply DB schema.
# Run from repo root (secai-radar). Requires Postgres and DATABASE_URL (or use default).
# Default URL: postgresql://secairadar:password@localhost:5432/secairadar
# To use Docker for a matching DB first: docker run -d --name secairadar-pg \
#   -e POSTGRES_USER=secairadar -e POSTGRES_PASSWORD=password -e POSTGRES_DB=secairadar \
#   -p 5432:5432 postgres:16-alpine

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
export DATABASE_URL="${DATABASE_URL:-postgresql://secairadar:password@localhost:5432/secairadar}"
echo "Using DATABASE_URL=${DATABASE_URL%%@*}@***"
python apps/public-api/scripts/migrate.py
echo "Step 1 done: schema applied."
