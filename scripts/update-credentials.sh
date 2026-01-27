#!/bin/bash
# Store DATABASE_URL and other credentials in Azure Key Vault and document GitHub secrets.
# PostgreSQL server: ctxeco-db (ctxeco-rg)
#   https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview

set -e

KV_NAME="${KEY_VAULT_NAME:-secai-radar-dev-kv}"
RG="${RESOURCE_GROUP:-secai-radar-rg}"
# Existing PostgreSQL (ctxeco-rg)
PG_FQDN="${PG_FQDN:-ctxeco-db.postgres.database.azure.com}"
PG_USER="${PG_USER:-ctxecoadmin}"
PG_DB="${PG_DB:-secairadar}"

echo "🔐 SecAI Radar – Update credentials (Key Vault + GitHub secrets)"
echo "================================================================="
echo "Key Vault: $KV_NAME"
echo "Resource Group: $RG"
echo "PostgreSQL: $PG_USER@$PG_FQDN / $PG_DB"
echo ""

# Ensure logged in
if ! az account show &>/dev/null; then
  echo "❌ Run 'az login' first."
  exit 1
fi

# Ensure Key Vault exists
if ! az keyvault show --name "$KV_NAME" --resource-group "$RG" &>/dev/null; then
  echo "❌ Key Vault '$KV_NAME' not found in '$RG'."
  echo "   Deploy infra first: infra/mcp-infrastructure-existing-db.bicep"
  exit 1
fi

# --- DATABASE_URL in Key Vault ---
echo "📦 DATABASE_URL → Key Vault secret 'database-url'"
if [ -n "${DATABASE_URL}" ]; then
  echo "   Using DATABASE_URL from environment."
  az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "database-url" \
    --value "$DATABASE_URL" --output none
  echo "   ✅ Stored in $KV_NAME"
else
  echo "   Enter PostgreSQL password for $PG_USER (input hidden)."
  echo "   Or set DATABASE_URL and re-run this script."
  read -s -p "   Password: " PG_PASS
  echo ""
  if [ -n "$PG_PASS" ]; then
    # URL-encode password to be safe (minimal: replace % and @)
    SAFE_PASS=$(printf '%s' "$PG_PASS" | sed 's/%/%25/g; s/@/%40/g')
    URL="postgresql://${PG_USER}:${SAFE_PASS}@${PG_FQDN}:5432/${PG_DB}"
    az keyvault secret set \
      --vault-name "$KV_NAME" \
      --name "database-url" \
      --value "$URL" --output none
    echo "   ✅ Stored in $KV_NAME"
  else
    echo "   ⚠️  Skipped (no password or DATABASE_URL)."
  fi
fi

echo ""
echo "✅ Key Vault updated."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 GitHub secrets to set (Settings → Secrets and variables → Actions):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  DATABASE_URL"
echo "    Used by: daily-pipeline.yml (workers), migrations, Container App."
echo "    Value: same connection string as in Key Vault."
echo "    Get from KV:  az keyvault secret show --vault-name $KV_NAME --name database-url --query value -o tsv"
echo ""
echo "  AZURE_STATIC_WEB_APPS_API_TOKEN"
echo "    Used by: azure-static-web-apps.yml (SWA deploy)."
echo "    From: Azure Portal → Static Web App (secai-radar) → Manage deployment token"
echo ""
echo "  VITE_API_BASE (optional)"
echo "    Used by: azure-static-web-apps.yml at build (default: https://secai-radar-api.azurewebsites.net/api)."
echo "    Set to your Public API URL when using Container App, e.g. https://<public-api-fqdn>/api"
echo ""
echo "  AZURE_CREDENTIALS (if using deploy-infrastructure / deploy-staging)"
echo "    JSON with service principal: appId, password, tenant."
echo ""
echo "Quick one-off (GH CLI, paste value when prompted):"
echo "  gh secret set DATABASE_URL"
echo "  gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN"
echo ""
echo "Using value from Key Vault for DATABASE_URL:"
echo "  gh secret set DATABASE_URL --body \"\$(az keyvault secret show --vault-name $KV_NAME --name database-url --query value -o tsv)\""
echo ""
