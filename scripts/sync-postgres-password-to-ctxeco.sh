#!/bin/bash
# Copy Postgres admin password from secai Key Vault to ctxeco Key Vault and update zep-postgres-dsn.
# Run after the server password is reset and stored in the source vault.
#
# Usage:
#   SOURCE_VAULT=secai-radar-kv SOURCE_SECRET=postgres-password ./scripts/sync-postgres-password-to-ctxeco.sh
#   # Or if the password is in database-url (we parse it from the connection string):
#   SOURCE_VAULT=secai-radar-kv SOURCE_SECRET=database-url ./scripts/sync-postgres-password-to-ctxeco.sh
#
# Requires: az login, read access to SOURCE_VAULT, and set/list/set on ctxecokv.

set -e

SOURCE_VAULT="${SOURCE_VAULT:-secai-radar-kv}"
SOURCE_SECRET="${SOURCE_SECRET:-postgres-password}"
CTXECO_KV="${CTXECO_KV:-ctxecokv}"
CTXECO_RG="${CTXECO_RG:-ctxeco-rg}"
ZEP_APP="${ZEP_APP:-ctxeco-zep}"
PG_USER="${PG_USER:-ctxecoadmin}"
PG_HOST="${PG_HOST:-ctxeco-db.postgres.database.azure.com}"

echo "Sync Postgres password: $SOURCE_VAULT ($SOURCE_SECRET) -> $CTXECO_KV"
echo ""

VAL=$(az keyvault secret show --vault-name "$SOURCE_VAULT" --name "$SOURCE_SECRET" --query value -o tsv 2>/dev/null) || {
  echo "Cannot read secret $SOURCE_SECRET from $SOURCE_VAULT. Ensure it exists and you have read access."
  exit 1
}

if [ "$SOURCE_SECRET" = "database-url" ]; then
  # Parse password from postgresql://user:password@host/...
  if [[ "$VAL" =~ postgresql://[^:]+:([^@]+)@ ]]; then
    PG_PASS="${BASH_REMATCH[1]}"
  else
    echo "Could not parse password from database-url."
    exit 1
  fi
else
  PG_PASS="$VAL"
fi

echo "Updating $CTXECO_KV postgres-password and zep-postgres-dsn..."
az keyvault secret set --vault-name "$CTXECO_KV" --name postgres-password --value "$PG_PASS" --output none
DSN="postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:5432/zep?sslmode=require"
az keyvault secret set --vault-name "$CTXECO_KV" --name zep-postgres-dsn --value "$DSN" --output none
echo "Restarting Zep so it picks up the new DSN..."
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --min-replicas 0 --max-replicas 2 --output none
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --min-replicas 1 --max-replicas 2 --output none
echo "Done. ctxecokv postgres-password and zep-postgres-dsn updated; Zep restarted."