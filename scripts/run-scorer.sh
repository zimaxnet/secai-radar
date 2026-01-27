#!/bin/bash
# Run Scorer worker (T-073). Reads evidence_items/evidence_claims, writes score_snapshots and latest_scores.
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

# Install scoring package first (required dependency)
echo "Installing scoring package..."
cd packages/scoring
"$VENV/bin/pip" install -q -e . || {
  echo "Failed to install scoring package"
  exit 1
}
cd "$OLDPWD"

# Install scorer worker
echo "Installing scorer worker..."
cd apps/workers/scorer
"$VENV/bin/pip" install -q -e . || {
  echo "Failed to install scorer worker"
  exit 1
}
cd "$OLDPWD"

# Run scorer
"$VENV/bin/python" apps/workers/scorer/src/scorer.py
