#!/bin/bash
# Cleanup duplicate MCP servers based on content similarity
# Marks duplicates as 'Deprecated' status, keeping the best one

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
PYTHON="${VENV}/bin/python"

if [ ! -d "$VENV" ]; then
  echo "Virtual environment not found at $VENV"
  exit 1
fi

SCRIPT="${PWD}/apps/public-api/scripts/cleanup_duplicates.py"

if [ ! -f "$SCRIPT" ]; then
  echo "Cleanup script not found at $SCRIPT"
  exit 1
fi

echo "==> Running duplicate cleanup script"
"$PYTHON" "$SCRIPT"

echo "==> Duplicate cleanup complete"
