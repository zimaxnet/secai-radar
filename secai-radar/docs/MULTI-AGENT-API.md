# Multi-Agent Assessment API

## Overview

The Multi-Agent Assessment API provides HTTP endpoints for triggering and managing automated security assessments using the 7-agent orchestration system.

## Endpoints

### Start Assessment

**POST** `/api/tenant/{tenantId}/multi-agent-assessment`

Start a new multi-agent security assessment.

**Request Body:**
```json
{
  "assessment_id": "assessment-001",  // Optional, auto-generated if not provided
  "budget": 100000.0                  // Optional, default: 100000.0
}
```

**Response:**
```json
{
  "assessment_id": "assessment-001",
  "tenant_id": "CONTOSO",
  "status": "completed",
  "phase": "completed",
  "findings_count": 15,
  "events_count": 42,
  "budget_used": 1250.50,
  "summary": {
    "total_findings": 15,
    "critical_risks": 3,
    "active_conflicts": 0,
    "resolved_conflicts": 1
  },
  "findings": [...]
}
```

### Get Assessment Status

**GET** `/api/tenant/{tenantId}/multi-agent-assessment/{assessmentId}`

Get the current status and results of an assessment.

**Response:**
```json
{
  "assessment_id": "assessment-001",
  "tenant_id": "CONTOSO",
  "status": "completed",
  "phase": "completed",
  "findings_count": 15,
  "events_count": 42,
  "budget_used": 1250.50,
  "summary": {
    "total_findings": 15,
    "critical_risks": 3,
    "active_conflicts": 0,
    "resolved_conflicts": 1
  },
  "updated_at": "2025-11-18T20:30:00"
}
```

### List Assessments

**GET** `/api/tenant/{tenantId}/multi-agent-assessment`

List all assessments for a tenant.

**Response:**
```json
{
  "assessments": [
    {
      "assessment_id": "assessment-001",
      "tenant_id": "CONTOSO",
      "status": "completed",
      "phase": "completed",
      "updated_at": "2025-11-18T20:30:00"
    }
  ]
}
```

## Configuration

### Required Environment Variables

- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key (or in Key Vault)
- `COSMOS_ENDPOINT` - Azure Cosmos DB endpoint (optional, for state persistence)
- `COSMOS_KEY` - Azure Cosmos DB key (optional)
- `GOOGLE_API_KEY` - Google API key for RAG (optional, for Google File Search)

### Optional Configuration

- `AZURE_OPENAI_MODEL` - Model name (default: "gpt-5-chat")
- `AZURE_OPENAI_DEPLOYMENT` - Deployment name (default: "gpt-5-chat")

## Workflow Phases

1. **Assessment Phase**: Discovery and analysis
   - Aris queries CAF knowledge base
   - Leo analyzes identity configuration
   - Ravi scans infrastructure
   - Kenji collates findings

2. **Design Phase**: Architecture and planning
   - Aris proposes architecture
   - Elena assesses business impact
   - Marcus resolves conflicts (if any)

3. **Migration Phase**: Migration planning
   - Leo designs MCA billing hierarchy
   - Elena validates with customer
   - Final report generation

## Error Handling

- **503 Service Unavailable**: Orchestrator not available (check dependencies/config)
- **500 Internal Server Error**: Assessment failed (check logs)
- **504 Gateway Timeout**: Assessment exceeded timeout (check status later)
- **404 Not Found**: Assessment not found
- **403 Forbidden**: Access denied (tenant mismatch)

## Notes

- Assessments may take several minutes to complete
- For long-running assessments, consider using Durable Functions or a queue pattern
- State is persisted to Cosmos DB (if configured) for recovery
- Budget tracking helps monitor token usage and costs

