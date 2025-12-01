---
layout: default
title: Agent Registry
permalink: /agent-registry/
---

# Agent Registry

## Overview

The Agent Registry is the centralized inventory and management system for all AI agents in SecAI Radar. It serves as the single source of truth for agent discoverability, governance, and lifecycle management.

## What is the Agent Registry?

The Agent Registry provides:

- **Centralized Inventory** - Complete list of all agents in the organization
- **Discoverability** - Agents can find other agents, humans can find agents
- **Collections** - Organize agents into groups (quarantine, assessment-agents, etc.)
- **Status Management** - Track agent status (active, idle, quarantined, disabled)
- **Third-Party Support** - Register external agents with Entra Agent IDs

## Registry Features

### Agent Inventory

View all registered agents:

```http
GET /api/registry/agents
```

**Query Parameters**:
- `status` - Filter by status (active, idle, quarantined, disabled, error)
- `collection` - Filter by collection name
- `blueprint` - Filter by blueprint
- `capability` - Filter by capability

**Example Response**:

```json
{
  "agents": [
    {
      "agent_id": "aris_thorne",
      "entra_agent_id": "12345678-1234-1234-1234-123456789012",
      "name": "Dr. Aris Thorne",
      "role": "Knowledge Base Guardian",
      "status": "active",
      "blueprint": "secai-assessment-agent",
      "capabilities": [
        "query_framework_knowledge",
        "map_control_to_framework"
      ],
      "collections": ["secai-core", "assessment-agents"],
      "last_active_at": "2025-01-15T10:30:00Z",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "count": 1
}
```

### Agent Details

Get detailed information about a specific agent:

```http
GET /api/registry/agents/{agent_id}
```

Returns complete agent profile including:
- Identity information
- Capabilities
- Collections
- Activity timeline
- Metadata

### Agent Status

Agent status values:

- **active** - Agent is operational and ready
- **idle** - Agent is waiting for tasks
- **quarantined** - Agent is isolated (security concern)
- **disabled** - Agent is disabled (maintenance)
- **error** - Agent has encountered an error

### Collections

Collections organize agents into logical groups:

**Built-in Collections**:
- `secai-core` - Core SecAI Radar agents
- `quarantine` - Quarantined agents (not discoverable)
- `assessment-agents` - Agents used in assessments

**Custom Collections**:
Create custom collections for your organization:
- `security-team` - Agents used by security team
- `compliance-agents` - Agents for compliance workflows
- `research-agents` - Experimental agents

### Quarantine

Quarantine isolates agents that may be compromised or need review:

**Quarantine an Agent**:

```http
POST /api/registry/agents/{agent_id}/quarantine
```

**Effects of Quarantine**:
- Agent status set to `quarantined`
- Agent added to `quarantine` collection
- Agent removed from discoverability
- Agent cannot be found by other agents
- Agent actions are logged for review

**Unquarantine an Agent**:

```http
DELETE /api/registry/agents/{agent_id}/quarantine
```

## Using the Registry

### Register a New Agent

```http
POST /api/registry/agents
Content-Type: application/json

{
  "agent_id": "custom-agent",
  "entra_agent_id": "optional-existing-id",
  "name": "Custom Agent",
  "role": "Specialist",
  "blueprint": "secai-assessment-agent",
  "capabilities": ["custom_capability"],
  "collections": ["custom-collection"],
  "metadata": {
    "team": "security",
    "environment": "production"
  }
}
```

### Update Agent Status

```http
PUT /api/registry/agents/{agent_id}/status
Content-Type: application/json

{
  "status": "disabled"
}
```

### Manage Collections

**Add to Collection**:

```http
PUT /api/registry/agents/{agent_id}/collections
Content-Type: application/json

{
  "action": "add",
  "collection_name": "security-team"
}
```

**Remove from Collection**:

```http
PUT /api/registry/agents/{agent_id}/collections
Content-Type: application/json

{
  "action": "remove",
  "collection_name": "security-team"
}
```

## Registry UI

### Agent Command Center

Access the Agent Command Center from the main navigation:

1. Navigate to **Agents** in the main menu
2. View agent health overview
3. See real-time activity feed
4. Monitor performance metrics

### Agent Registry View

View the full registry:

1. Navigate to **Agents** → **Registry**
2. Filter by status, collection, blueprint, or capability
3. View agent details
4. Manage agent status and collections

### Agent Detail View

View individual agent details:

1. Click on an agent in the registry
2. View agent profile
3. See capabilities and collections
4. Review activity timeline
5. Check performance metrics

## Agent Discovery

### Agent-to-Agent Discovery

Agents can discover other agents through the registry:

```python
# In agent code
registry = get_registry_service()
available_agents = registry.list_agents(
    collection="assessment-agents",
    status="active"
)
```

### Human Discovery

Users can discover agents through:

1. **Registry UI** - Browse all agents
2. **Search** - Search by name, role, or capability
3. **Collections** - Browse agents by collection
4. **Agent Store** - Discover agents by use case (future)

## Best Practices

### Registry Management

1. **Regular Audits** - Review registry quarterly
2. **Status Updates** - Keep agent status current
3. **Collection Organization** - Use collections for logical grouping
4. **Cleanup** - Remove unused or deprecated agents

### Quarantine Management

1. **Immediate Action** - Quarantine suspicious agents immediately
2. **Investigation** - Review quarantined agents promptly
3. **Documentation** - Document quarantine reasons
4. **Resolution** - Unquarantine or disable after review

### Third-Party Agents

When registering third-party agents:

1. **Identity Verification** - Verify Entra Agent ID
2. **Capability Mapping** - Map agent capabilities accurately
3. **Collection Assignment** - Assign to appropriate collections
4. **Monitoring** - Monitor third-party agents closely

## API Reference

### List Agents

```http
GET /api/registry/agents?status=active&collection=secai-core
```

### Get Agent

```http
GET /api/registry/agents/{agent_id}
```

### Register Agent

```http
POST /api/registry/agents
```

### Update Status

```http
PUT /api/registry/agents/{agent_id}/status
```

### Quarantine

```http
POST /api/registry/agents/{agent_id}/quarantine
DELETE /api/registry/agents/{agent_id}/quarantine
```

### Manage Collections

```http
PUT /api/registry/agents/{agent_id}/collections
```

## Related Documentation

- [Entra Agent Identity](Entra-Agent-Identity.md) - Agent identity management
- [Foundry Control Plane](Foundry-Control-Plane.md) - Observability and controls
- [Agent Governance](Agent-Governance-Framework.md) - Governance framework

