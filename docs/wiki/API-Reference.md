---
layout: default
title: Api Reference
permalink: /API-Reference/
---

# API Reference

Complete API documentation for SecAI Radar.

---

## Base URL

All API endpoints are relative to:
```
/api
```

---

## Authentication

API authentication is handled via Azure Static Web Apps authentication. Include authentication headers as required by your deployment.

---

## Endpoints

### Domains

#### GET /domains

Get list of security domains.

**Response**:
```json
{
  "items": [
    {
      "code": "NET",
      "name": "Network Security"
    },
    {
      "code": "IDM",
      "name": "Identity Management"
    }
  ]
}
```

---

### Summary

#### GET /tenant/{tenantId}/summary

Get summary statistics for a tenant.

**Parameters**:
- `tenantId` (path): Tenant identifier

**Response**:
```json
{
  "byDomain": [
    {
      "domain": "Network Security",
      "total": 25,
      "complete": 15,
      "inProgress": 5,
      "notStarted": 5
    }
  ]
}
```

---

### Controls

#### GET /tenant/{tenantId}/controls

Get list of controls for a tenant.

**Parameters**:
- `tenantId` (path): Tenant identifier
- `domain` (query, optional): Filter by domain code
- `status` (query, optional): Filter by status
- `q` (query, optional): Search query

**Example**:
```
GET /api/tenant/tenant-alpha/controls?domain=NET&status=Complete&q=firewall
```

**Response**:
```json
{
  "items": [
    {
      "PartitionKey": "tenant-alpha|NET",
      "RowKey": "SEC-NET-0001",
      "Domain": "NET",
      "ControlTitle": "Network Security Group Rules",
      "Status": "Complete",
      "Owner": "Network Team"
    }
  ],
  "total": 1
}
```

#### POST /tenant/{tenantId}/import

Import controls from CSV.

**Parameters**:
- `tenantId` (path): Tenant identifier

**Body**:
- Content-Type: `text/csv`
- CSV content with required headers

**Required Headers**:
```
ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,
Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
```

**Response**:
```json
{
  "ok": true,
  "message": "Controls imported successfully"
}
```

---

### Tools

#### GET /tenant/{tenantId}/tools

Get list of tools for a tenant.

**Parameters**:
- `tenantId` (path): Tenant identifier

**Response**:
```json
{
  "items": [
    {
      "PartitionKey": "tenant-alpha",
      "RowKey": "wiz-cspm",
      "Enabled": true,
      "ConfigScore": 0.8
    }
  ]
}
```

#### POST /tenant/{tenantId}/tools

Add or update tool configuration.

**Parameters**:
- `tenantId` (path): Tenant identifier

**Body**:
```json
{
  "vendorToolId": "wiz-cspm",
  "Enabled": true,
  "ConfigScore": 0.8
}
```

**Response**:
```json
{
  "ok": true,
  "message": "Tool configuration saved"
}
```

---

### Gaps

#### GET /tenant/{tenantId}/gaps

Get gap analysis for a tenant.

**Parameters**:
- `tenantId` (path): Tenant identifier

**Response**:
```json
{
  "items": [
    {
      "ControlID": "SEC-NET-0001",
      "DomainPartition": "tenant-alpha|NET",
      "Coverage": 0.704,
      "HardGaps": [
        {
          "capabilityId": "url-filtering",
          "weight": 0.4
        }
      ],
      "SoftGaps": [
        {
          "capabilityId": "ns-firewall",
          "weight": 0.6,
          "best": 0.65,
          "min": 0.7,
          "tool": "paloalto-fw"
        }
      ]
    }
  ],
  "total": 1
}
```

---

## Error Responses

### 400 Bad Request

Invalid request format or missing required fields.

**Response**:
```json
{
  "error": "Invalid request",
  "message": "Missing required field: vendorToolId"
}
```

### 404 Not Found

Resource not found.

**Response**:
```json
{
  "error": "Not found",
  "message": "Tenant not found"
}
```

### 500 Internal Server Error

Server error.

**Response**:
```json
{
  "error": "Internal server error",
  "message": "An error occurred processing your request"
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse. Rate limits depend on your deployment configuration.

---

## Pagination

Some endpoints support pagination. Check response headers for pagination information.

---

## Data Models

### Control

```json
{
  "ControlID": "SEC-NET-0001",
  "Domain": "NET",
  "ControlTitle": "Network Security Group Rules",
  "ControlDescription": "Ensure NSG rules restrict access appropriately",
  "Status": "Complete",
  "Owner": "Network Team",
  "ScoreNumeric": 85,
  "Weight": 0.5
}
```

### Tool

```json
{
  "vendorToolId": "wiz-cspm",
  "Enabled": true,
  "ConfigScore": 0.8
}
```

### Gap

```json
{
  "ControlID": "SEC-NET-0001",
  "Coverage": 0.704,
  "HardGaps": [],
  "SoftGaps": [
    {
      "capabilityId": "ns-firewall",
      "weight": 0.6,
      "best": 0.65,
      "min": 0.7,
      "tool": "paloalto-fw"
    }
  ]
}
```

---

## Examples

### JavaScript/TypeScript

```typescript
// Get summary
const response = await fetch('/api/tenant/tenant-alpha/summary')
const data = await response.json()

// Get controls
const controls = await fetch('/api/tenant/tenant-alpha/controls?domain=NET')
const controlsData = await controls.json()

// Add tool
await fetch('/api/tenant/tenant-alpha/tools', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    vendorToolId: 'wiz-cspm',
    Enabled: true,
    ConfigScore: 0.8
  })
})

// Import controls
await fetch('/api/tenant/tenant-alpha/import', {
  method: 'POST',
  headers: { 'Content-Type': 'text/csv' },
  body: csvContent
})
```

### Python

```python
import requests

# Get summary
response = requests.get('/api/tenant/tenant-alpha/summary')
data = response.json()

# Add tool
requests.post('/api/tenant/tenant-alpha/tools', json={
    'vendorToolId': 'wiz-cspm',
    'Enabled': True,
    'ConfigScore': 0.8
})
```

---

## Versioning

API versioning is handled via URL path. Current version is v1 (default).

---

## Support

For API support:
- Check [FAQ](/wiki/FAQ) for common questions
- Review [Troubleshooting](/wiki/Troubleshooting) guide
- Open an issue on GitHub

---

**Related**: [Architecture](/wiki/Architecture) | [Installation](/wiki/Installation)

