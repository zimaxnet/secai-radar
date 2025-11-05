# Tool Research and Dynamic Control Mapping

## Overview

SecAI Radar provides the ability to:
1. **Input a list of security vendor tools** used in the enterprise
2. **Automatically research** each tool's capabilities using AI and web search
3. **Dynamically map** all 340 controls across 12 security domains to the tools
4. **Generate coverage analysis** showing which tools address which controls

## Architecture

### Tool Research Service

**Location**: `api/shared/tool_research.py`

**Capabilities**:
- Web search integration for current tool information
- AI-powered capability extraction
- Strength and maturity scoring
- Source tracking for research results

### Dynamic Mapping

The system automatically:
1. Researches each tool's capabilities
2. Maps capabilities to the 340 controls
3. Calculates coverage scores
4. Identifies gaps where tools don't cover controls

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

### Research Multiple Tools and Map to Controls

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
  "tenantId": "NICO"  # Optional, to save results
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
- **Load requirements**: Get required capabilities for the control
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

1. **Network Security (NET)**
2. **Identity & Access (ID)**
3. **Privileged Access (PA)**
4. **Data Protection (DATA)**
5. **Asset Management (ASSET)**
6. **Logging & Monitoring (LOG)**
7. **Incident Response (IR)**
8. **Posture Management (POST)**
9. **Endpoint Security (END)**
10. **Backup & Recovery (BAK)**
11. **Development Security (DEV)**
12. **Governance (GOV)**

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
- Multi-source validation

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

## API Endpoints

### Research Tool
```
GET /api/tool-research?toolName={name}&vendor={vendor}
```

### Research and Map Multiple Tools
```
POST /api/tool-research
Body: {
  "tools": [...],
  "tenantId": "optional"
}
```

## Next Steps

1. ✅ **Research Service** - Implemented
2. ✅ **Mapping Logic** - Implemented
3. ⏳ **Web Search API** - Needs configuration (Bing/Google)
4. ⏳ **Caching Layer** - Cache research results
5. ⏳ **UI Integration** - Add tool research UI
6. ⏳ **Scheduled Updates** - Auto-refresh tool capabilities

