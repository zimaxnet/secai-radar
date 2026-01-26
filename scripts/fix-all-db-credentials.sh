#!/bin/bash
# Fix DB credentials for BOTH ctxEco and secai-radar (shared server: ctxeco-db).
# Run after a password reset. Updates Key Vault only; restarts Zep so it refetches from KV.
#
# Credentials may only be stored in: .env (local), GitHub secrets, Key Vault (KV).
# This script updates KV. For secai-radar public-api, update GitHub DATABASE_URL from KV and redeploy.
#
# Usage:
#   POSTGRES_PASSWORD='your-new-password' ./scripts/fix-all-db-credentials.sh
#   ./scripts/fix-all-db-credentials.sh
#
# Requires: az login, access to ctxecokv + secai-radar-kv, permission to update ctxeco-zep (ctxeco-rg).
set -e

CTXECO_KV="${CTXECO_KV:-ctxecokv}"
CTXECO_RG="${CTXECO_RG:-ctxeco-rg}"
SECAI_KV="${SECAI_KV:-secai-radar-kv}"
SECAI_RG="${SECAI_RG:-secai-radar-rg}"
ZEP_APP="${ZEP_APP:-ctxeco-zep}"
PUBLIC_API_APP="${PUBLIC_API_APP:-secai-radar-public-api}"
PG_USER="${PG_USER:-ctxecoadmin}"
PG_HOST="${PG_HOST:-ctxeco-db.postgres.database.azure.com}"
PG_DB_CTXECO="${PG_DB_CTXECO:-ctxEco}"

# URL-encode password for use in connection URIs (special chars like @, #, & break otherwise)
urlencode_password() {
  python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=''))"
}

echo "=== Fix all DB credentials (ctxEco + secai-radar) ==="
echo "Server: $PG_HOST  User: $PG_USER"
echo ""

if [ -n "${POSTGRES_PASSWORD:-}" ]; then
  PG_PASS="$POSTGRES_PASSWORD"
else
  read -s -p "Enter PostgreSQL password for $PG_USER (hidden): " PG_PASS
  echo ""
  if [ -z "$PG_PASS" ]; then
    echo "No password provided. Set POSTGRES_PASSWORD or enter at prompt."
    exit 1
  fi
fi

PG_PASS_ENC=$(printf '%s' "$PG_PASS" | urlencode_password)
echo "Updating Key Vaults and apps..."
echo ""

# 1) ctxecokv – used by Zep, ctxEco backend/worker/temporal
echo "1. ctxecokv ($CTXECO_KV)..."
az keyvault secret set --vault-name "$CTXECO_KV" --name postgres-password --value "$PG_PASS" --output none
az keyvault secret set --vault-name "$CTXECO_KV" --name zep-postgres-dsn --value "postgresql://${PG_USER}:${PG_PASS_ENC}@${PG_HOST}:5432/zep?sslmode=require" --output none
az keyvault secret set --vault-name "$CTXECO_KV" --name postgres-connection-string --value "postgresql://${PG_USER}:${PG_PASS_ENC}@${PG_HOST}:5432/${PG_DB_CTXECO}?sslmode=require" --output none
echo "   postgres-password, zep-postgres-dsn, postgres-connection-string OK"

# 2) secai-radar-kv – used by secai public-api (and as source for GitHub DATABASE_URL)
echo "2. secai-radar-kv ($SECAI_KV)..."
SECAI_URL="postgresql://${PG_USER}:${PG_PASS_ENC}@${PG_HOST}:5432/secairadar?sslmode=require"
az keyvault secret set --vault-name "$SECAI_KV" --name database-url --value "$SECAI_URL" --output none
echo "   database-url OK"

# 3) Zep – force new revision so it refetches zep-postgres-dsn from Key Vault
echo "3. Zep (new revision + scale 0→1)..."
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --revision-suffix "creds-$(date +%s)" --output none
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --min-replicas 0 --max-replicas 2 --output none
az containerapp update -g "$CTXECO_RG" -n "$ZEP_APP" --min-replicas 1 --max-replicas 2 --output none
echo "   Zep restarted"

# 4) secai-radar public-api gets DATABASE_URL from GitHub secret at deploy (credentials only in .env, gh secrets, KV)
echo "4. secai-radar public-api uses GitHub secret DATABASE_URL at deploy."
echo "   Update it from KV, then re-run Deploy to Staging:"
echo "   gh secret set DATABASE_URL --body \"\$(az keyvault secret show --vault-name $SECAI_KV --name database-url --query value -o tsv)\""

echo ""
echo "=== Done ==="
echo ""
echo "Credentials are stored only in: .env (local), GitHub secrets, Key Vault."
echo "Update GitHub DATABASE_URL from KV (required for public-api to use new creds on next deploy):"
echo "  gh secret set DATABASE_URL --body \"\$(az keyvault secret show --vault-name $SECAI_KV --name database-url --query value -o tsv)\""
echo ""
echo "Verify:"
echo "  Zep:        az containerapp logs show -g $CTXECO_RG -n $ZEP_APP --tail 30"
echo "  public-api: curl -s https://\$(az containerapp show -n $PUBLIC_API_APP -g $SECAI_RG --query 'properties.configuration.ingress.fqdn' -o tsv)/api/v1/public/health"
echo ""
