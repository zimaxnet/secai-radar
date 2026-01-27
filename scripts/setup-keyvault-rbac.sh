#!/bin/bash
# Create a user-assigned managed identity and grant it Key Vault Secrets Officer
# on the given Key Vault. Use RBAC (enable if not already).
#
# Usage:
#   ./scripts/setup-keyvault-rbac.sh
#   KEY_VAULT_NAME=my-kv RESOURCE_GROUP=my-rg ./scripts/setup-keyvault-rbac.sh

set -e

KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
RG="${RESOURCE_GROUP:-secai-radar-rg}"
# Identity name: no hyphens for ARM (e.g. secairadarkvidentity)
IDENTITY_NAME="${KV_IDENTITY_NAME:-$(echo "$KV_NAME" | sed 's/-//g')identity}"

KEY_VAULT_SECRETS_OFFICER_ID="b86a8fe4-44ce-4948-aee5-eccb2c155cd7"

echo "Key Vault RBAC (managed identity)"
echo "  Vault: $KV_NAME"
echo "  Resource group: $RG"
echo "  Managed identity: $IDENTITY_NAME"
echo ""

if ! az account show &>/dev/null; then
  echo "Run 'az login' first."
  exit 1
fi

if ! az keyvault show --name "$KV_NAME" --resource-group "$RG" &>/dev/null; then
  echo "Key Vault '$KV_NAME' not found in '$RG'."
  exit 1
fi

# Enable RBAC on the vault if still using access policies
RBAC=$(az keyvault show --name "$KV_NAME" --resource-group "$RG" --query "properties.enableRbacAuthorization" -o tsv 2>/dev/null || true)
if [ "$RBAC" != "true" ]; then
  echo "Enabling RBAC on Key Vault..."
  az keyvault update --name "$KV_NAME" --resource-group "$RG" --enable-rbac-authorization true
  echo "  Done."
else
  echo "RBAC already enabled on Key Vault."
fi

# Create user-assigned managed identity if it doesn't exist
if ! az identity show --name "$IDENTITY_NAME" --resource-group "$RG" &>/dev/null; then
  echo "Creating managed identity '$IDENTITY_NAME'..."
  az identity create --name "$IDENTITY_NAME" --resource-group "$RG" --output none
  echo "  Done."
else
  echo "Managed identity '$IDENTITY_NAME' already exists."
fi

PRINCIPAL_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RG" --query principalId -o tsv)
KV_ID=$(az keyvault show --name "$KV_NAME" --resource-group "$RG" --query id -o tsv)

# Role assignment (idempotent: list first to avoid duplicate-create errors)
ASSIGNMENT_ID=$(az role assignment list \
  --scope "$KV_ID" \
  --assignee "$PRINCIPAL_ID" \
  --role "$KEY_VAULT_SECRETS_OFFICER_ID" \
  --query '[0].id' -o tsv 2>/dev/null || true)

if [ -z "$ASSIGNMENT_ID" ] || [ "$ASSIGNMENT_ID" = "" ]; then
  echo "Assigning 'Key Vault Secrets Officer' to managed identity..."
  az role assignment create \
    --scope "$KV_ID" \
    --assignee "$PRINCIPAL_ID" \
    --role "$KEY_VAULT_SECRETS_OFFICER_ID" \
    --output none
  echo "  Done."
else
  echo "Role assignment already present."
fi

CLIENT_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RG" --query clientId -o tsv)
echo ""
echo "Summary:"
echo "  Key Vault: $KV_NAME (RBAC enabled)"
echo "  Managed identity: $IDENTITY_NAME"
echo "  Principal ID: $PRINCIPAL_ID"
echo "  Client ID: $CLIENT_ID"
echo "  Role: Key Vault Secrets Officer"
echo ""
echo "Use this identity for Container Apps, automation, or Azure services that need to read/write secrets in $KV_NAME."
