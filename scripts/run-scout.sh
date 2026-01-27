#!/bin/bash
# Run Scout worker (T-070 discovery ingest). Uses same DB as run-migrations/seed.
set -e
cd "$(dirname "$0")/.."

if [ -z "${DATABASE_URL}" ]; then
  KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
  if command -v az &>/dev/null && az account show &>/dev/null 2>&1; then
    DATABASE_URL=$(az keyvault secret show --vault-name "$KV_NAME" --name database-url --query value -o tsv 2>/dev/null || true)
  fi
fi

if [ -z "${DATABASE_URL}" ]; then
  echo "DATABASE_URL is not set. Set it or use Azure CLI + Key Vault (secai-radar-kv / database-url)."
  exit 1
fi

export DATABASE_URL
VENV="${PWD}/apps/public-api/.venv"
if [ ! -d "$VENV" ]; then
  echo "Run ./scripts/run-migrations.sh first to create the venv."
  exit 1
fi

"$VENV/bin/pip" install -q requests 2>/dev/null || true
"$VENV/bin/python" apps/workers/scout/src/scout.py
