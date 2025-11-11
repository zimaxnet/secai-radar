---
layout: default
title: Tool Research And Mapping
---

# Tool Research and Dynamic Control Mapping

## Overview

SecAI Radar provides the ability to:
1. **Input a list of security vendor tools** used in the enterprise
2. **Automatically research** each tool's capabilities using AI and web search
3. **Dynamically map** all 340 controls across 12 security domains to the tools
4. **Generate coverage analysis** showing which tools address which controls

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
- **Load requirements**: Get required capabilities for the control from seed data
- **Match capabilities**: Find which tools provide required capabilities
- **Calculate coverage**: Compute how well each tool covers the control
- **Identify gaps**: Find controls with no or insufficient tool coverage

### 3. Coverage Analysis

The system provides:
- **Per-control coverage**: Which tools cover each control and how well
- **Per-tool coverage**: Which controls each tool addresses
- **Gap identification**: Controls with no coverage
- **Recommendations**: Which tools to add or tune

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

## Web Search Integration

### Current Implementation

Uses Azure OpenAI with web search capabilities:
- AI can search the web for current tool information
- Extracts capabilities from vendor documentation
- Finds current feature lists and specifications

### Future Enhancements

- Direct web search API integration (Bing, Google Custom Search)
- Caching of research results
- Scheduled re-research for tool updates
- Notification of capability changes

## AI-Powered Research

The research service uses AI to:
1. **Search the web** for current tool information
2. **Extract capabilities** from documentation and articles
3. **Score capabilities** based on descriptions and reviews
4. **Identify maturity** based on tool age and market presence
5. **Cite sources** for transparency

## Integration with Existing System

The researched tools can be:
- **Saved to TenantTools** table for the tenant
- **Merged with existing tool inventory**
- **Used in gap analysis** immediately
- **Updated automatically** when re-researched

## Best Practices

1. **Research Tools Regularly**: Tool capabilities evolve over time
2. **Validate Results**: Review AI-generated capability mappings
3. **Add Custom Tools**: Manually add tools not found in research
4. **Tune Config Scores**: Adjust ConfigScore based on actual implementation
5. **Track Sources**: Keep research sources for audit and verification

## Related Documentation

- [Key Vault Setup](/wiki/Key-Vault-Setup)
- [AI Integration](/wiki/AI-Integration)
- [Tools Guide](/wiki/Tools-Guide)
- [API Reference](/wiki/API-Reference)
