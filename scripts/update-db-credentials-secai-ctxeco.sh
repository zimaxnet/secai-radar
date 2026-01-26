#!/bin/bash
# Update Postgres credentials in both ctxEco and secai-radar Key Vaults (shared server: ctxeco-db).
# Use after a password reset or to sync a single password into both vaults.
#
# For a single run that also updates the RUNNING secai public-api and gives verification steps,
# use: ./scripts/fix-all-db-credentials.sh  (see workspace root DB-CREDENTIALS-FIX.md)
#
# Usage:
#   POSTGRES_PASSWORD='newpassword' ./scripts/update-db-credentials-secai-ctxeco.sh
#   ./scripts/update-db-credentials-secai-ctxeco.sh
#   ./scripts/update-db-credentials-secai-ctxeco.sh --from-vault ctxecokv
#
# Requires: az login, set permission on both ctxecokv and secai-radar-kv.

set -e

urlencode_password() { python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=''))"; }

CTXECO_KV="${CTXECO_KV:-ctxecokv}"
CTXECO_RG="${CTXECO_RG:-ctxeco-rg}"
SECAI_KV="${SECAI_KV:-secai-radar-kv}"
ZEP_APP="${ZEP_APP:-ctxeco-zep}"
PG_USER="${PG_USER:-ctxecoadmin}"
PG_HOST="${PG_HOST:-ctxeco-db.postgres.database.azure.com}"
PG_DB_CTXECO="${PG_DB_CTXECO:-ctxEco}"

FROM_VAULT=""
if [ "${1:-}" = "--from-vault" ] && [ -n "${2:-}" ]; then
  FROM_VAULT="$2"
fi

if [ -n "$FROM_VAULT" ]; then
  echo "Reading postgres password from $FROM_VAULT (postgres-password)..."
  PG_PASS=$(az keyvault secret show --vault-name "$FROM_VAULT" --name postgres-password --query value -o tsv 2>/dev/null) || {
  echo "Could not read postgres-password from $FROM_VAULT."
  exit 1
}
elif [ -n "${POSTGRES_PASSWORD:-}" ]; then
  PG_PASS="$POSTGRES_PASSWORD"
else
  echo "Enter PostgreSQL admin password for $PG_USER (input hidden). Or set POSTGRES_PASSWORD and re-run."
  read -s -p "Password: " PG_PASS
  echo ""
  if [ -z "$PG_PASS" ]; then
    echo "No password provided."
    exit 1
  fi
fi

PG_PASS_ENC=$(printf '%s' "$PG_PASS" | urlencode_password)

echo "Updating ctxEco Key Vault ($CTXECO_KV)..."
az keyvault secret set --vault-name "$CTXECO_KV" --name postgres-password --value "$PG_PASS" --output none
ZEP_DSN="postgresql://${PG_USER}:${PG_PASS_ENC}@${PG_HOST}:5432/zep?sslmode=require"
POSTGRES_CS="postgresql://${PG_USER}:${PG_PASS_ENC}@${PG_HOST}:5432/${PG_DB_CTXECO}?sslmode=require"
az keyvault secret set --vault-name "$CTXECO_KV" --name zep-postgres-dsn --value "$ZEP_DSN" --output none
az keyvault secret set --vault-name "$CTXECO_KV" --name postgres-connection-string --value "$POSTGRES_CS" --output none
echo "  postgres-password, zep-postgres-dsn, postgres-connection-string updated."

echo "Updating secai-radar Key Vault ($SECAI_KV)..."
SECAI_DATABASE_URL="postgresql://${PG_USER}:${PG_PASS_ENC}@${PG_HOST}:5432/secairadar?sslmode=require"
az keyvault secret set --vault-name "$SECAI_KV" --name database-url --value "$SECAI_DATABASE_URL" --output none
echo "  database-url updated (ctxecoadmin / secairadar DB)."

echo "Restarting Zep so it picks up the new DSN (force new revision to refetch Key Vault)..."
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --revision-suffix "dsn-$(date +%s)" --output none
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --min-replicas 0 --max-replicas 2 --output none
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --min-replicas 1 --max-replicas 2 --output none
echo ""

echo "Done. Both vaults updated; Zep restarted."
echo "  ctxecokv: postgres-password, zep-postgres-dsn, postgres-connection-string"
echo "  $SECAI_KV: database-url (secairadar DB, ctxecoadmin)"
echo ""
echo "Update GitHub DATABASE_URL for secai-radar deploy (run from secai-radar repo):"
echo "  gh secret set DATABASE_URL --body \"\$(az keyvault secret show --vault-name $SECAI_KV --name database-url --query value -o tsv)\""