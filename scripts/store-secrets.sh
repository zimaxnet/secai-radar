#!/bin/bash
# Secure Secret Storage Script for SecAI Radar
# Stores secrets in Azure Key Vault via secure terminal input

set -e

KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
RG="${RESOURCE_GROUP:-secai-radar-rg}"

echo "🔐 SecAI Radar - Secure Secret Storage"
echo "======================================"
echo ""
echo "Key Vault: $KV_NAME"
echo "Resource Group: $RG"
echo ""

# Check if Key Vault exists
if ! az keyvault show --name "$KV_NAME" --resource-group "$RG" &>/dev/null; then
    echo "❌ Key Vault '$KV_NAME' not found in resource group '$RG'"
    echo ""
    echo "Create it first with:"
    echo "  az keyvault create --name $KV_NAME --resource-group $RG --location centralus"
    exit 1
fi

echo "You will be prompted to enter secrets. Your input will be hidden."
echo "Press Enter to skip any secret you don't want to store."
echo ""

# Azure OpenAI API Key
echo "📝 Azure OpenAI API Key"
read -s -p "Enter Azure OpenAI API Key (input hidden): " OPENAI_KEY
echo ""
if [ -n "$OPENAI_KEY" ]; then
    az keyvault secret set \
        --vault-name "$KV_NAME" \
        --name "azure-openai-api-key" \
        --value "$OPENAI_KEY" > /dev/null 2>&1
    echo "✅ Azure OpenAI API Key stored securely"
else
    echo "⚠️  Skipped Azure OpenAI API Key"
fi

echo ""
echo "✅ Secrets stored in Azure Key Vault: $KV_NAME"
echo ""
echo "Next steps:"
echo "1. Ensure Function App has 'Key Vault Secrets User' role"
echo "2. Set KEY_VAULT_URL in Function App settings: https://$KV_NAME.vault.azure.net/"
echo "3. Enable Managed Identity on Function App if not already enabled"

