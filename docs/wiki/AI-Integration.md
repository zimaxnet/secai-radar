---
layout: default
title: Ai Integration
---

# AI Integration

## Overview

SecAI Radar integrates Azure OpenAI to provide AI-powered features for security assessment, analysis, and recommendations.

## Features

### 🤖 AI-Powered Recommendations
- Generate actionable recommendations for security control gaps
- Prioritize tuning existing tools before suggesting new ones
- Provide context-aware guidance based on tenant tool inventory

### 🔍 Tool Research
- Automatically research security vendor tools
- Extract capabilities and features using web search
- Score tool capabilities and maturity levels

### 📊 Gap Analysis Enhancement
- Natural language explanations of security gaps
- Context-aware gap descriptions
- Recommendations for addressing gaps

### 📄 Report Generation
- AI-generated executive summaries
- Automated report content generation
- Customizable report formats

## Configuration

### Prerequisites

1. **Azure OpenAI Resource**: Access to Azure OpenAI service
2. **Key Vault**: Azure Key Vault for secure API key storage
3. **Function App**: Managed Identity enabled for Key Vault access

### Setup

1. **Create Key Vault** (if not already created):
   ```bash
   az keyvault create --name secai-radar-kv --resource-group secai-radar-rg
   ```

2. **Store API Key**:
   ```bash
   KEY_VAULT_NAME=secai-radar-kv ./scripts/store-secrets.sh
   ```

3. **Configure Function App**:
   - Enable Managed Identity
   - Grant "Key Vault Secrets User" role
   - Set `KEY_VAULT_URL` application setting

See [Key Vault Setup](/wiki/Key-Vault-Setup) for detailed instructions.

## API Usage

### Get Gaps with AI Recommendations

```bash
GET /api/tenant/{tenantId}/gaps?ai=true
```

Returns gap analysis with AI-generated recommendations for each control.

### Research Tool Capabilities

```bash
GET /api/tool-research?toolName={name}&vendor={vendor}
```

Researches a security tool and returns its capabilities.

### Map Multiple Tools to Controls

```bash
POST /api/tool-research
{
  "tools": [
    {"name": "Tool Name", "vendor": "Vendor Name"}
  ],
  "tenantId": "optional"
}
```

Researches multiple tools and maps them to all 340 controls.

## AI Service Configuration

The AI service uses these environment variables:

- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_MODEL` - Model name (e.g., "gpt-5-chat")
- `AZURE_OPENAI_DEPLOYMENT` - Deployment name
- `AZURE_OPENAI_API_VERSION` - API version
- `KEY_VAULT_URL` - Key Vault URL (for API key retrieval)

API key is retrieved from Key Vault secret: `azure-openai-api-key`

## Security

- **API Keys**: Stored securely in Azure Key Vault
- **Managed Identity**: Function App authenticates automatically
- **No Hardcoded Secrets**: All secrets retrieved at runtime
- **Fallback Support**: Environment variables for local development

## Cost Considerations

- Azure OpenAI charges per token usage
- Tool research features may incur higher costs
- Consider caching research results
- Monitor usage in Azure Portal

## Troubleshooting

### "AI service not available"
- Check Key Vault is configured
- Verify API key is stored in Key Vault
- Check Function App has Key Vault access
- Verify Managed Identity is enabled

### "API key not found"
- Verify secret exists: `az keyvault secret list --vault-name secai-radar-kv`
- Check Function App has "Key Vault Secrets User" role
- Verify `KEY_VAULT_URL` is set in Function App settings

### Research results are incomplete
- Verify Azure OpenAI has web search enabled
- Check API key has proper permissions
- Review AI service logs for errors

## Related Documentation

- [Key Vault Setup](/wiki/Key-Vault-Setup)
- [Tool Research and Mapping](/wiki/Tool-Research-and-Mapping)
- [Gaps Guide](/wiki/Gaps-Guide)
- [API Reference](/wiki/API-Reference)
