# AI Integration Setup Guide

## Overview

SecAI Radar now supports Azure OpenAI integration for AI-powered features including:
- Natural language recommendations for gaps
- Gap explanations
- Executive summary generation
- Evidence classification (planned)

## Configuration

### 1. Environment Variables

Add these environment variables to your Azure Function App configuration:

```bash
AZURE_OPENAI_ENDPOINT=https://zimax.cognitiveservices.azure.com/
AZURE_OPENAI_MODEL=gpt-5-chat
AZURE_OPENAI_DEPLOYMENT=gpt-5-chat
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 2. Azure Portal Configuration

1. Go to Azure Portal → Function App → `secai-radar-api`
2. Navigate to **Configuration** → **Application settings**
3. Add the following application settings:
   - `AZURE_OPENAI_ENDPOINT`: `https://zimax.cognitiveservices.azure.com/`
   - `AZURE_OPENAI_MODEL`: `gpt-5-chat`
   - `AZURE_OPENAI_DEPLOYMENT`: `gpt-5-chat`
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_API_VERSION`: `2024-12-01-preview`
4. Click **Save**

### 3. Local Development

Update `api/local.settings.json`:

```json
{
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://zimax.cognitiveservices.azure.com/",
    "AZURE_OPENAI_MODEL": "gpt-5-chat",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-5-chat",
    "AZURE_OPENAI_API_KEY": "<your-api-key>",
    "AZURE_OPENAI_API_VERSION": "2024-12-01-preview"
  }
}
```

**Important**: Never commit API keys to git. Add `local.settings.json` to `.gitignore` if not already there.

## Usage

### Gaps Endpoint with AI Recommendations

The gaps endpoint now supports an optional `?ai=true` parameter to include AI-powered recommendations:

```bash
# Without AI (default)
GET /api/tenant/{tenantId}/gaps

# With AI recommendations
GET /api/tenant/{tenantId}/gaps?ai=true
```

**Response with AI**:
```json
{
  "items": [
    {
      "ControlID": "SEC-NET-0001",
      "Coverage": 0.65,
      "HardGaps": [...],
      "SoftGaps": [...],
      "AIRecommendation": "To improve coverage for SEC-NET-0001, consider..."
    }
  ],
  "aiEnabled": true
}
```

### AI Recommendations Endpoint

New dedicated endpoint for AI-powered recommendations:

```bash
# Get recommendations for a specific control
GET /api/tenant/{tenantId}/ai/recommendations?controlId=SEC-NET-0001

# Get explanation for a specific gap
GET /api/tenant/{tenantId}/ai/recommendations?capabilityId=ns-firewall&gapType=hard
```

## Implementation Details

### AI Service Module

Location: `api/shared/ai_service.py`

**Features**:
- `generate_recommendation()` - Generate recommendations for controls with gaps
- `explain_gap()` - Explain specific gaps in natural language
- `generate_report_summary()` - Generate executive summaries
- `classify_evidence()` - Classify evidence types (planned)

### Graceful Degradation

The AI service is **optional**:
- If not configured, endpoints work without AI features
- AI features are only enabled when `?ai=true` is passed
- Errors are handled gracefully - failures don't break the endpoint

## Testing

### Test AI Service Locally

```python
from shared.ai_service import get_ai_service

ai = get_ai_service()
recommendation = ai.generate_recommendation(
    control_id="SEC-NET-0001",
    control_title="Edge firewall controls",
    gaps=[{"capabilityId": "ns-firewall", "weight": 0.6}],
    tenant_tools=[{"id": "palo-alto", "name": "Palo Alto Firewall", "configScore": 0.8}]
)
print(recommendation)
```

### Test Endpoints

```bash
# Test gaps endpoint with AI
curl "https://secai-radar-api.azurewebsites.net/api/tenant/NICO/gaps?ai=true"

# Test AI recommendations endpoint
curl "https://secai-radar-api.azurewebsites.net/api/tenant/NICO/ai/recommendations?controlId=SEC-NET-0001"
```

## Cost Considerations

- **Token Usage**: Each AI call consumes tokens based on input/output size
- **Cost**: Azure OpenAI charges per token (input + output)
- **Optimization**: 
  - Use streaming for long responses
  - Cache recommendations when possible
  - Use shorter prompts for simple queries

## Security

- **API Key**: Store in Azure Key Vault for production
- **Access Control**: AI endpoints respect authentication
- **Rate Limiting**: Consider implementing rate limits for AI endpoints
- **Data Privacy**: Ensure no sensitive data is sent to AI models

## Next Steps

1. ✅ **AI Service Module** - Created
2. ✅ **Gaps Endpoint Enhancement** - Added AI recommendations
3. ✅ **Requirements Updated** - Added `openai` package
4. ⏳ **Evidence Classification** - Planned
5. ⏳ **Report Generation** - Planned
6. ⏳ **UI Integration** - Add AI recommendations to frontend

## Troubleshooting

### "AI service not configured"
- Check that all environment variables are set
- Verify API key is correct
- Check Azure OpenAI endpoint is accessible

### "AI service error"
- Check API key permissions
- Verify model deployment name matches
- Check API version compatibility

### No AI recommendations in response
- Ensure `?ai=true` parameter is included
- Check that AI service is configured
- Review function logs for errors

## References

- Azure OpenAI Service: https://learn.microsoft.com/azure/ai-services/openai/
- OpenAI Python SDK: https://github.com/openai/openai-python

