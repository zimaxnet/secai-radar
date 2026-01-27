#!/bin/bash
# Grant the currently signed-in Azure user "Key Vault Secrets User" on a Key Vault
# so they can read secrets (e.g. database-url) via az keyvault secret show or run-migrations.sh.
#
# Usage:
#   ./scripts/grant-kv-read-access.sh
#   KEY_VAULT_NAME=secai-radar-dev-kv RESOURCE_GROUP=secai-radar-rg ./scripts/grant-kv-read-access.sh

set -e

KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
RG="${RESOURCE_GROUP:-secai-radar-rg}"
KEY_VAULT_SECRETS_USER_ID="4633458b-17de-408a-b874-0445c86b69e6"

echo "Grant Key Vault read access (Secrets User) to signed-in user"
echo "  Vault: $KV_NAME"
echo "  RG: $RG"
echo ""

if ! az account show &>/dev/null; then
  echo "Run 'az login' first."
  exit 1
fi

if ! az keyvault show --name "$KV_NAME" --resource-group "$RG" &>/dev/null; then
  echo "Key Vault '$KV_NAME' not found in '$RG'."
  exit 1
fi

USER_ID=$(az ad signed-in-user show --query id -o tsv)
KV_ID=$(az keyvault show --name "$KV_NAME" --resource-group "$RG" --query id -o tsv)

EXISTING=$(az role assignment list --scope "$KV_ID" --assignee "$USER_ID" --role "$KEY_VAULT_SECRETS_USER_ID" --query '[0].id' -o tsv 2>/dev/null || true)
if [ -n "$EXISTING" ] && [ "$EXISTING" != "" ]; then
  echo "You already have Key Vault Secrets User on $KV_NAME."
  exit 0
fi

echo "Assigning Key Vault Secrets User to current user..."
az role assignment create \
  --scope "$KV_ID" \
  --assignee "$USER_ID" \
  --role "$KEY_VAULT_SECRETS_USER_ID" \
  --output none
echo "Done. You can read secrets from $KV_NAME (e.g. run-migrations.sh will pull database-url)."
