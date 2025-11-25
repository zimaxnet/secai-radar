# Tool Research and Dynamic Control Mapping Feature

## Overview

This feature enables consultants and users to:
1. **Input a list of security vendor tools** used in the enterprise
2. **Automatically research** each tool's capabilities using AI and web search
3. **Dynamically map** all 340 controls across 12 security domains to the tools
4. **Generate coverage analysis** showing which tools address which controls

## Architecture

### Components

1. **Key Vault Service** (`api/shared/key_vault.py`)
   - Secure storage for API keys and secrets
   - Uses Managed Identity for authentication
   - Falls back to environment variables for local dev

2. **AI Service** (`api/shared/ai_service.py`)
   - Updated to retrieve API keys from Key Vault
   - Provides web-augmented research capabilities
   - Generates tool capability mappings

3. **Tool Research Service** (`api/shared/tool_research.py`)
   - Researches vendor tools using AI and web search
   - Extracts capabilities and scores them
   - Maps tools to controls dynamically

4. **Tool Research Endpoint** (`api/tool_research/__init__.py`)
   - REST API for tool research
   - Supports single tool research (GET)
   - Supports batch tool research and mapping (POST)

## Setup

### 1. Create Azure Key Vault

```bash
KV_NAME=secai-radar-kv-$(openssl rand -hex 4)
az keyvault create \
  --name "$KV_NAME" \
  --resource-group secai-radar-rg \
  --location centralus \
  --enable-rbac-authorization true
```

### 2. Store Azure OpenAI API Key

Run the secure input script:

```bash
KEY_VAULT_NAME=$KV_NAME ./scripts/store-secrets.sh
```

You'll be prompted to enter the API key securely (input is hidden).

### 3. Grant Function App Access

```bash
FUNCTION_APP_NAME=secai-radar-api
PRINCIPAL_ID=$(az functionapp identity show \
  --name "$FUNCTION_APP_NAME" \
  --resource-group secai-radar-rg \
  --query principalId -o tsv)

az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee "$PRINCIPAL_ID" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/secai-radar-rg/providers/Microsoft.KeyVault/vaults/$KV_NAME"
```

### 4. Configure Function App

```bash
az functionapp config appsettings set \
  --name "$FUNCTION_APP_NAME" \
  --resource-group secai-radar-rg \
  --settings "KEY_VAULT_URL=https://$KV_NAME.vault.azure.net/"
```

## Usage

### Research Single Tool

```bash
GET /api/tool-research?toolName=Palo%20Alto%20Firewall&vendor=Palo%20Alto%20Networks
```

**Response**:
```json
{
  "toolName": "Palo Alto Firewall",
  "vendor": "Palo Alto Networks",
  "capabilities": [
    {
      "capabilityId": "ns-firewall",
      "strength": 0.9,
      "maturity": 0.85,
      "notes": "Industry-leading next-generation firewall"
    },
    {
      "capabilityId": "url-filtering",
      "strength": 0.85,
      "maturity": 0.8,
      "notes": "Advanced URL filtering with threat intelligence"
    }
  ],
  "sources": ["https://paloaltonetworks.com/...", "..."],
  "lastResearched": "2025-11-05"
}
```

### Research and Map Multiple Tools

```bash
POST /api/tool-research
Content-Type: application/json

{
  "tools": [
    {"name": "Palo Alto Firewall", "vendor": "Palo Alto Networks"},
    {"name": "CrowdStrike Falcon", "vendor": "CrowdStrike"},
    {"name": "Google SecOps", "vendor": "Google"},
    {"name": "Wiz", "vendor": "Wiz"}
  ],
  "tenantId": "NICO"
}
```

**Response**:
```json
{
  "toolResearch": {
    "palo-alto-firewall": {
      "toolName": "Palo Alto Firewall",
      "vendor": "Palo Alto Networks",
      "capabilities": [...]
    },
    ...
  },
  "controlMappings": {
    "SEC-NET-0001": {
      "controlId": "SEC-NET-0001",
      "toolCoverage": {
        "palo-alto-firewall": {
          "coverage": 0.75,
          "matchedCapabilities": [...]
        }
      },
      "bestTool": "palo-alto-firewall"
    },
    ...
  },
  "summary": {
    "toolsResearched": 4,
    "controlsMapped": 340,
    "totalControls": 340
  }
}
```

## How It Works

### 1. Tool Research Phase

For each tool:
- **AI-powered web search**: Uses Azure OpenAI with web search to find current information
- **Capability extraction**: Identifies security capabilities from research
- **Strength scoring**: Rates how well the tool performs each capability (0.0-1.0)
- **Maturity scoring**: Rates how established/proven the capability is (0.0-1.0)
- **Source tracking**: Records URLs used for research

### 2. Control Mapping Phase

For each of the 340 controls:
- **Load requirements**: Get required capabilities for the control from `seeds_control_requirements.json`
- **Match capabilities**: Find which tools provide required capabilities
- **Calculate coverage**: Compute how well each tool covers the control
- **Identify gaps**: Find controls with no or insufficient tool coverage

### 3. Coverage Analysis

The system provides:
- **Per-control coverage**: Which tools cover each control and how well
- **Per-tool coverage**: Which controls each tool addresses
- **Gap identification**: Controls with no coverage
- **Recommendations**: Which tools to add or tune

## 340 Controls Across 12 Domains

The system maps to all controls across these domains:

1. **NET** - Network Security
2. **ID** - Identity & Access
3. **PA** - Privileged Access
4. **DATA** - Data Protection
5. **ASSET** - Asset Management
6. **LOG** - Logging & Monitoring
7. **IR** - Incident Response
8. **POST** - Posture Management
9. **END** - Endpoint Security
10. **BAK** - Backup & Recovery
11. **DEV** - Development Security
12. **GOV** - Governance

Each control has:
- Required capabilities (with weights)
- Minimum strength thresholds
- Domain classification

## Security

### Key Vault Integration

- All secrets stored in Azure Key Vault
- Managed Identity for automatic authentication
- No secrets in code or environment variables (in production)
- Secure credential input via terminal script

### API Key Management

- API keys stored as Key Vault secrets
- Retrieved at runtime, not hardcoded
- Fallback to environment variables for local development
- Proper access controls via RBAC

## Future Enhancements

1. **Web Search API Integration**
   - Direct integration with Bing Search API or Google Custom Search
   - More reliable web search results
   - Better source citation

2. **Caching Layer**
   - Cache research results to reduce API calls
   - TTL-based expiration for tool updates
   - Invalidate cache when tools are updated

3. **Scheduled Updates**
   - Periodic re-research of tools
   - Automatic capability updates
   - Notification of capability changes

4. **UI Integration**
   - Tool research interface in web app
   - Bulk tool import
   - Research results visualization

5. **Multi-source Validation**
   - Cross-reference multiple sources
   - Confidence scoring
   - Source reliability ratings

## Troubleshooting

### "AI service not available"
- Check Key Vault is configured
- Verify API key is stored in Key Vault
- Check Function App has Key Vault access
- Verify Managed Identity is enabled

### "Control requirements seed file not found"
- Ensure `seeds_control_requirements.json` exists in `api/` directory
- Check file permissions

### Research results are incomplete
- Verify Azure OpenAI has web search enabled
- Check API key has proper permissions
- Review AI service logs for errors

## Related Documentation

- [Key Vault Setup Guide](./KEY-VAULT-SETUP.md)
- [Tool Research and Mapping](./TOOL-RESEARCH-AND-MAPPING.md)
- [AI Implementation Status](./AI-IMPLEMENTATION-STATUS.md)

