---
layout: default
title: Key Vault Setup
---

# Azure Key Vault Setup

## Overview

SecAI Radar uses Azure Key Vault to securely store and manage secrets, keys, and certificates. This provides centralized secret management with proper access controls and auditing.

## Key Vault Configuration

### 1. Create Key Vault

```bash
# Set variables
KV_NAME=secai-radar-kv-$(openssl rand -hex 4)
RG=secai-radar-rg
LOC=centralus

# Create Key Vault
az keyvault create \
  --name "$KV_NAME" \
  --resource-group "$RG" \
  --location "$LOC" \
  --sku standard \
  --enable-rbac-authorization true
```

### 2. Grant Access to Function App

The Function App needs access to read secrets from Key Vault:

```bash
# Get Function App identity (if using Managed Identity)
FUNCTION_APP_NAME=secai-radar-api
PRINCIPAL_ID=$(az functionapp identity show \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --query principalId -o tsv)

# Grant Key Vault Secrets User role
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee "$PRINCIPAL_ID" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/$KV_NAME"
```

### 3. Store Secrets in Key Vault

#### Store Azure OpenAI API Key

Use the secure input script:

```bash
KEY_VAULT_NAME=secai-radar-kv ./scripts/store-secrets.sh
```

Or set directly:

```bash
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "azure-openai-api-key" \
  --value "$(read -s -p 'Enter Azure OpenAI API Key: ' key && echo $key)"
```

### 4. Configure Function App

Add Key Vault URL to Function App settings:

```bash
az functionapp config appsettings set \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --settings "KEY_VAULT_URL=https://$KV_NAME.vault.azure.net/"
```

### 5. Enable Managed Identity (if not already enabled)

```bash
az functionapp identity assign \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG"
```

## Secrets Stored in Key Vault

### Required Secrets

- `azure-openai-api-key` - Azure OpenAI API key for AI features

### Optional Secrets (Future)

- `azure-storage-connection-string` - Storage account connection string
- `azure-tables-connection-string` - Table storage connection string
- `azure-blobs-connection-string` - Blob storage connection string
- `github-token` - GitHub personal access token
- `slack-webhook-url` - Slack webhook URL for notifications

## Access Patterns

### In Code (Python)

```python
from shared.key_vault import get_secret_from_key_vault_or_env

# Get secret from Key Vault or environment variable (fallback)
api_key = get_secret_from_key_vault_or_env(
    secret_name="azure-openai-api-key",
    env_var_name="AZURE_OPENAI_API_KEY"
)
```

### Direct Key Vault Access

```python
from shared.key_vault import get_key_vault

kv = get_key_vault()
if kv:
    secret = kv.get_secret("azure-openai-api-key")
```

## Security Best Practices

1. **Never commit secrets**: All secrets go in Key Vault
2. **Use Managed Identity**: Function App authenticates automatically
3. **Least Privilege**: Only grant necessary permissions
4. **Audit Access**: Monitor Key Vault access logs
5. **Rotate Secrets**: Regularly rotate API keys and secrets
6. **Separate Environments**: Use different Key Vaults for dev/staging/prod

## Troubleshooting

### "Unable to authenticate to Key Vault"
- Check Managed Identity is enabled on Function App
- Verify role assignment (Key Vault Secrets User)
- Check Key Vault URL is correct

### "Secret not found"
- Verify secret name matches exactly
- Check secret exists in Key Vault
- Verify access permissions

### Local Development
- Use Azure CLI authentication: `az login`
- Or set environment variables for local testing
- Key Vault will be used automatically in Azure

## Related Documentation

- [Tool Research and Mapping](/wiki/Tool-Research-and-Mapping)
- [AI Integration](/wiki/AI-Integration)
