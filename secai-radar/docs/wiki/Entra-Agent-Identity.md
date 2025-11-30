---
layout: default
title: Entra Agent Identity
permalink: /entra-agent-identity/
---

# Entra Agent Identity

## Overview

SecAI Radar integrates with Microsoft Entra Agent ID to provide unique identities for each AI agent, enabling enterprise-grade identity management, access control, and auditing capabilities.

## What is Entra Agent ID?

Entra Agent ID provides a unique identity for every agent in SecAI Radar, similar to how user identities work in Microsoft Entra ID. This enables:

- **Granular Access Control** - Define specific permissions for each agent
- **Comprehensive Auditing** - Track all agent actions with identity context
- **Lifecycle Management** - Manage agent identities from creation to decommissioning
- **Security Integration** - Integrate with Microsoft Defender and Purview

## Agent Identity Architecture

### Agent Blueprints

All SecAI Radar agents are created from a **blueprint** that defines:

- Base permissions and capabilities
- Default authentication scopes
- Security policies
- Tool access rights

**Default Blueprint**: `secai-assessment-agent`

This blueprint provides:
- Storage read/write access
- Table storage access
- Key Vault read access
- Graph API access (for identity operations)

### Registered Agents

Each of the 7 SecAI Radar agents has a unique Entra Agent ID:

1. **Dr. Aris Thorne** (`aris_thorne`) - Knowledge Base Guardian
2. **Leo Vance** (`leo_vance`) - Identity & Access Analyst
3. **Ravi Patel** (`ravi_patel`) - Infrastructure Architect
4. **Kenji Sato** (`kenji_sato`) - Findings Analyst
5. **Elena Bridges** (`elena_bridges`) - Business Impact Strategist
6. **Marcus Sterling** (`marcus_sterling`) - Conflict Resolution & Governance
7. **Supervisor** (`supervisor`) - System Orchestrator

## Identity Provisioning

### Automatic Registration

Agent identities are automatically provisioned when the orchestrator initializes:

1. System reads agent configuration from `config/agent_identities.yaml`
2. Each agent is registered with Microsoft Entra ID
3. Service principal is created with appropriate permissions
4. Identity is stored in the agent registry

### Manual Registration

You can also manually register agents via the API:

```http
POST /api/registry/agents
Content-Type: application/json

{
  "agent_id": "custom-agent",
  "name": "Custom Agent",
  "role": "Specialist",
  "blueprint": "secai-assessment-agent",
  "capabilities": ["custom_capability"],
  "entra_agent_id": "optional-existing-id"
}
```

## Authentication Flow

### Token Acquisition

Agents acquire access tokens using their Entra Agent ID:

```python
# In agent code
token = agent.get_agent_token(scopes=["https://graph.microsoft.com/.default"])
```

### Token Caching

Tokens are automatically cached and refreshed:
- Tokens cached for 1 hour
- Automatic refresh before expiration
- Per-agent, per-scope caching

## Access Control

### Tool Authorization

Each agent is authorized to use specific tools based on their blueprint and configuration:

**Example**: Aris Thorne can use:
- `query_framework_knowledge`
- `map_control_to_framework`
- `validate_framework_alignment`
- `generate_framework_citation`
- `assess_best_practices`

Tool authorization is enforced by the guardrails service.

### Resource Access

Agents can access Azure resources based on their identity:

- **Storage Accounts** - Read/write access to assessment data
- **Table Storage** - Access to controls and tools data
- **Key Vault** - Read access to secrets (API keys, etc.)
- **Graph API** - Identity and directory operations

## Auditing

### Action Auditing

All agent actions are automatically audited:

```python
# Automatic auditing in agent code
agent.audit_action(
    action="tool_call",
    resource="storage_account",
    details={"tool": "query_framework_knowledge", "result": "success"}
)
```

### Audit Logs

Audit logs include:
- Agent ID and Entra Agent ID
- Action performed
- Resource accessed
- Timestamp
- Success/failure status
- Additional context

Audit logs are sent to Application Insights for compliance reporting.

## Configuration

### Agent Identity Configuration

Agent identities are configured in `config/agent_identities.yaml`:

```yaml
agents:
  aris-thorne:
    agent_id: "aris_thorne"
    blueprint_id: "secai-assessment-agent"
    display_name: "Dr. Aris Thorne"
    status: "active"
    capabilities:
      - "query_framework_knowledge"
      - "map_control_to_framework"
```

### Blueprint Configuration

Blueprints define base permissions:

```yaml
blueprints:
  secai-assessment-agent:
    name: "SecAI Assessment Agent"
    permissions:
      - "Storage.Read"
      - "Storage.Write"
      - "Tables.Read"
      - "Tables.Write"
      - "KeyVault.Read"
```

## Security Best Practices

### Identity Management

1. **Regular Audits** - Review agent identities quarterly
2. **Least Privilege** - Grant only necessary permissions
3. **Rotation** - Rotate service principal credentials annually
4. **Monitoring** - Monitor for unusual agent activity

### Access Control

1. **Tool Restrictions** - Limit tools per agent based on role
2. **Resource Scoping** - Restrict resource access to required scope
3. **Network Policies** - Use Conditional Access for agent identities
4. **MFA** - Enable MFA for agent service principals (where supported)

## Troubleshooting

### Identity Not Found

**Problem**: Agent identity not found during initialization

**Solution**:
1. Check `config/agent_identities.yaml` for agent configuration
2. Verify agent is registered: `GET /api/registry/agents/{agent_id}`
3. Re-register agent if needed

### Token Acquisition Failed

**Problem**: Agent cannot acquire access token

**Solution**:
1. Verify Entra Agent ID is valid
2. Check service principal permissions
3. Verify tenant ID configuration
4. Check Key Vault for client secrets

### Access Denied

**Problem**: Agent cannot access required resource

**Solution**:
1. Check agent blueprint permissions
2. Verify resource access policies
3. Review tool authorization configuration
4. Check guardrails configuration

## API Reference

### Get Agent Identity

```http
GET /api/registry/agents/{agent_id}
```

Returns agent identity information including Entra Agent ID.

### Validate Identity

```http
GET /api/registry/agents/{agent_id}
```

Validates that agent identity is active and valid.

### Audit Agent Action

Agent actions are automatically audited. View audit logs in Application Insights.

## Related Documentation

- [Agent Registry](Agent-Registry.md) - Centralized agent inventory
- [Agent Governance](Agent-Governance-Framework.md) - Governance framework
- [Foundry Control Plane](Foundry-Control-Plane.md) - Observability and controls
- [Security Integration](Security-Integration.md) - Defender and Purview integration

