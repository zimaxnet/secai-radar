#!/bin/bash
# Create secairadar_app user on ctxeco-db. Uses apps/public-api venv.
# Requires ADMIN_DATABASE_URL or DATABASE_URL (ctxecoadmin). Optional: SECAIRADAR_APP_PASSWORD.

set -e
cd "$(dirname "$0")/.."
API_DIR="apps/public-api"
VENV="${API_DIR}/.venv"

if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -r "$API_DIR/requirements.txt" -q
fi

"$VENV/bin/python" scripts/create-secairadar-db-user.py
