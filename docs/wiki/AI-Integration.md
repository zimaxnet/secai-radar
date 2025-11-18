# AI Integration

## Overview

SecAI Radar integrates Azure OpenAI and Google Gemini to provide AI-powered features for security assessment, analysis, and recommendations. The system includes a **multi-agent orchestration layer** with **RAG (Retrieval-Augmented Generation)** for knowledge base queries.

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

### 🤖 Multi-Agent Orchestration
- 7 autonomous agents working together
- LangGraph-based state machine orchestration
- Three-phase workflow (Assessment → Design → Migration)
- Conflict resolution and escalation
- Real-time event stream for visualization

### 📚 RAG Knowledge Base
- Google File Search integration
- Agentic retrieval (agents decide when to search)
- CAF, WAF, MCA documentation access
- Context-aware knowledge queries

### 💬 Help Assistant
- Floating in-app widget with Azure OpenAI responses
- Context-aware prompts built from current route metadata
- FAQ quick actions and guided tour shortcuts
- Backend endpoint: `POST /api/tenant/{tenantId}/ai/help`

### 🛰️ Realtime Voice Proxy
- Allows the web UI to stream microphone audio to Azure OpenAI Realtime (`gpt-realtime`).
- Azure Function: `POST /api/realtime/session`
  - Body: `{ "sdpOffer": "..." }`
  - Returns: SDP answer text used to complete the WebRTC handshake.
- Required environment variables:
  - `AZURE_OPENAI_REALTIME_ENDPOINT`
  - `AZURE_OPENAI_REALTIME_KEY`
  - `AZURE_OPENAI_REALTIME_DEPLOYMENT` (defaults to `gpt-realtime`)
  - Optional: `AZURE_OPENAI_REALTIME_API_VERSION` (defaults `2024-10-01-preview`)
  - Optional: `REALTIME_PROXY_ALLOWED_ORIGIN` for CORS tightening

### 🗣️ Voice Interaction
- Uses WebRTC to connect the browser to Azure OpenAI `gpt-realtime`.
- Voice mode is opt-in via the help assistant microphone toggle; typed chat continues to use `gpt-5-chat`.
- Browser prerequisites: WebRTC support (Chromium, Safari 17+) and microphone permission.
- Audio responses stream directly from Azure Realtime; text responses remain available in the transcript for accessibility.

### 📈 AI Usage Telemetry
- Token consumption surfaced directly in the Gaps view when AI mode is enabled
- Data captured in Azure Table Storage (`AiUsage` table)
- REST endpoint: `GET /api/tenant/{tenantId}/ai/usage`

## Configuration

### Prerequisites

1. **Azure OpenAI Resource**: Access to Azure OpenAI service
2. **Google API Key**: For RAG (Google File Search) - Optional but recommended
3. **Key Vault**: Azure Key Vault for secure API key storage
4. **Function App**: Managed Identity enabled for Key Vault access
5. **Cosmos DB**: For state persistence (Free Tier available)

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

### Contextual Help

```bash
POST /api/tenant/{tenantId}/ai/help
{
  "question": "How do I interpret hard gaps?",
  "context": {
    "page": "Gaps",
    "pathname": "/tenant/CONTOSO/gaps"
  }
}
```

Returns an Azure OpenAI answer tailored to the active screen.

### Realtime Session Handshake

```bash
POST /api/realtime/session
{
  "sdpOffer": "v=0..."
}
```

Returns the SDP answer used to establish a WebRTC session with Azure OpenAI `gpt-realtime`.

### AI Usage Summary

```bash
GET /api/tenant/{tenantId}/ai/usage
```

Returns token totals, run counts, and per-model breakdown for transparency and cost control.

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

### Help assistant shows "AI service not available"
- Confirm `azure-openai-api-key` exists in Key Vault
- Ensure the Function App identity has `Key Vault Secrets User`
- Verify `/api/tenant/{tenantId}/ai/help` returns a 200 when called from Postman or curl

## Multi-Agent System

SecAI Radar includes a sophisticated multi-agent system for autonomous security assessments. See **[Multi-Agent System](Multi-Agent-System)** for complete documentation.

### Quick Start

```python
from src.orchestrator.initialize import initialize_orchestrator

# Auto-initializes Model Layer, RAG, and state management
graph = initialize_orchestrator()

# Run assessment workflow
state = await graph.run(initial_state)
```

### RAG Setup

1. Set `GOOGLE_API_KEY` environment variable
2. Upload knowledge base documents to Google File Search
3. Agents automatically query RAG when needed

See [RAG Integration](../RAG-INTEGRATION.md) for detailed setup.

## Related Documentation

- [Multi-Agent System](Multi-Agent-System) - Complete multi-agent documentation
- [Key Vault Setup](Key-Vault-Setup) - Secure API key storage
- [Tool Research and Mapping](Tool-Research-and-Mapping) - Tool capability research
- [Gaps Guide](Gaps-Guide) - Security gap analysis
- [API Reference](API-Reference) - API documentation
- [RAG Integration](../RAG-INTEGRATION.md) - RAG setup and usage
- [Cosmos DB Setup](../COSMOS-DB-SETUP.md) - State persistence

