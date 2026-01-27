#!/bin/bash
# Run database migrations for secairadar.
# Requires DATABASE_URL (or database-url in Key Vault when KEY_VAULT_NAME is set).
# Creates venv and installs deps if needed.

set -e
cd "$(dirname "$0")/.."

if [ -z "${DATABASE_URL}" ]; then
  KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
  if command -v az &>/dev/null && az account show &>/dev/null 2>&1; then
    echo "DATABASE_URL not set; trying Key Vault ($KV_NAME) ..."
    DATABASE_URL=$(az keyvault secret show --vault-name "$KV_NAME" --name database-url --query value -o tsv 2>/dev/null || true)
  fi
fi

if [ -z "${DATABASE_URL}" ]; then
  echo "DATABASE_URL is not set."
  echo "Example:"
  echo "  export DATABASE_URL=\"postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar\""
  echo "Or store it in Key Vault and run with: KEY_VAULT_NAME=secai-radar-kv ./scripts/run-migrations.sh"
  echo "  (after: ./scripts/update-credentials.sh)"
  exit 1
fi

API_DIR="apps/public-api"
VENV="${API_DIR}/.venv"

if [ ! -d "$VENV" ]; then
  echo "Creating venv at $VENV ..."
  python3 -m venv "$VENV"
fi

echo "Installing dependencies ..."
"$VENV/bin/pip" install -r "$API_DIR/requirements.txt" -q

echo "Running migrations ..."
"$VENV/bin/python" "$API_DIR/scripts/migrate.py"
echo "Done."
