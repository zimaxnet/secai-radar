---
layout: default
title: API Reference
---

# API Reference

The SecAI Radar API allows clients (browsers, scripts, and autonomous AI agents) to query the current trust rankings and specific integration details.

All API routes are served under the `/api/v1/public` prefix.

## Endpoints

### 1. `GET /mcp/rankings`

Returns the global rankings for Model Context Protocol (MCP) servers.

**Response Structure:**

```json
{
  "attestation": {
    "assessedBy": "SecAI Radar",
    "methodologyVersion": "v1.0"
  },
  "data": {
    "items": [
      {
        "mcpId": "srv-123",
        "name": "Example MCP",
        "provider": "VendorX",
        "tier": "A",
        "trustScore": 92.5
      }
    ]
  },
  "meta": {
    "total": 150,
    "page": 1,
    "pageSize": 20
  }
}
```

### 2. `GET /agents/rankings`

Returns the global rankings for standalone AI Agents. The response structure maps identically to the MCP rankings.

### 3. `POST /submissions`

Allows integrations to manually register for scouting.

**Request Payload:**

```json
{
  "repoUrl": "https://github.com/organization/my-new-mcp",
  "integrationType": "mcp", 
  "contactEmail": "dev@example.com"
}
```

*(Note: `integrationType` accepts "mcp" or "agent")*

---
*For a full interactive OpenAPI specification, boot the API locally and navigate to `http://localhost:8000/docs`.*
