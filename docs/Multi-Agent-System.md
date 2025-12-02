---
layout: default
title: Multi-Agent System
permalink: /multi-agent-system/
---

# Multi-Agent System

## Overview

SecAI Radar implements **Project Aethelgard** - a sophisticated multi-agent system that simulates a complete security assessment team. The system uses **LangGraph** for orchestration, enabling 7 autonomous agents to collaborate on cloud security assessments.

## Architecture

### Framework: LangGraph

SecAI Radar uses **LangGraph** for multi-agent orchestration because:

- ✅ **Explicit Control Flow**: State machine architecture for production reliability
- ✅ **Recursive Loops**: Support for iterative refinement (e.g., Deep Research pattern)
- ✅ **State Management**: Built-in state persistence and checkpointing
- ✅ **Supervisor Pattern**: Hierarchical routing between agents
- ✅ **Production-Ready**: Better than conversational frameworks for deterministic workflows

### System Components

1. **State Management** (`src/orchestrator/state.py`)
   - Global assessment state
   - Agent-specific contexts
   - Handoff packet structure
   - Cosmos DB persistence

2. **Supervisor** (`src/orchestrator/supervisor.py`)
   - Hierarchical routing logic
   - Phase-based task delegation
   - Conflict detection and escalation

3. **Agent Personas** (`src/orchestrator/agents/`)
   - 7 specialized agent implementations
   - Role-based system prompts
   - Tool capabilities per agent

4. **RAG Layer** (`src/rag/`)
   - Google File Search integration
   - Agentic retrieval pattern
   - Knowledge base queries

5. **Workflow Orchestration** (`src/orchestrator/workflow.py`)
   - Three-phase workflow execution
   - Handoff pattern implementation
   - Event emission

## The 7 Agents

### 1. Marcus Sterling - Senior Manager

**Role**: Executive decision-making and conflict resolution

**Responsibilities**:
- Final authority on critical trade-offs
- Resolves conflicts between security and business requirements
- Approves budget overruns
- Enforces migration directives

**Tools**: `approve_budget()`, `resolve_conflict()`, `phase_transition()`

**Model**: Strategic reasoning (GPT-4o recommended)

### 2. Elena Bridges - Relationship Manager

**Role**: Customer advocacy and business translation

**Responsibilities**:
- Translates technical risks to business consequences
- Assesses downtime and business impact
- Validates migration plans with customers
- Manages MCA billing transition expectations

**Tools**: `assess_business_impact()`, `validate_migration_plan()`, `customer_communication()`

**Model**: Strategic reasoning (GPT-4o recommended)

### 3. Dr. Aris Thorne - Principal Security Architect

**Role**: CAF alignment and security strategy

**Responsibilities**:
- Queries CAF knowledge base for assessment checklists
- Designs Azure Landing Zone architecture
- Conducts threat modeling
- Defines enterprise-wide security policies

**Tools**: `query_caf_knowledge()`, `design_landing_zone()`, `threat_modeling()`

**Model**: Strategic reasoning (GPT-4o recommended)

**RAG Usage**: ✅ Queries CAF knowledge base extensively

### 4. Leo Vance - Security Architect (IAM)

**Role**: Identity and Access Management

**Responsibilities**:
- Analyzes legacy identity configuration
- Designs identity migration to Entra ID
- Maps MCA billing roles
- Designs Conditional Access policies

**Tools**: `design_identity_migration()`, `map_billing_roles()`, `design_conditional_access()`

**Model**: Operational execution (GPT-4-Turbo)

**RAG Usage**: ✅ Queries MCA billing documentation

### 5. Priya Desai - Program Manager (Offshore Lead)

**Role**: Quality control and delivery assurance

**Responsibilities**:
- Reviews code and documentation
- Assigns tasks to engineers
- Enforces quality gates
- Approves work for onshore team

**Tools**: `review_code()`, `assign_tasks()`, `quality_gate()`

**Model**: Operational execution (GPT-4-Turbo)

### 6. Ravi Patel - Security Engineer

**Role**: Implementation and code generation

**Responsibilities**:
- Runs infrastructure security scans
- Generates Terraform/Bicep code
- Implements Azure Policy definitions
- Validates Infrastructure as Code

**Tools**: `generate_terraform()`, `implement_policy()`, `run_scan()`

**Model**: Operational execution (GPT-4-Turbo)

### 7. Kenji Sato - Program Manager

**Role**: Schedule tracking and status reporting

**Responsibilities**:
- Maintains project schedules
- Tracks dependencies
- Generates status reports
- Collates assessment findings

**Tools**: `update_schedule()`, `generate_status_report()`, `track_dependencies()`

**Model**: Operational execution (GPT-4-Turbo)

## Workflow Phases

### Phase 1: Assessment and Discovery

**Objective**: Understand current security posture

**Agent Activities**:
1. **Aris Thorne**: Queries CAF knowledge base for assessment checklist
2. **Leo Vance**: Analyzes legacy identity configuration
3. **Ravi Patel**: Scans infrastructure for security gaps
4. **Kenji Sato**: Collates findings into status report

**Outputs**:
- Assessment checklist
- Identity analysis
- Infrastructure scan results
- Findings report

### Phase 2: Design and Conflict Resolution

**Objective**: Design security architecture and resolve conflicts

**Agent Activities**:
1. **Aris Thorne**: Designs Azure Landing Zone architecture
2. **Elena Bridges**: Assesses business impact and downtime
3. **Marcus Sterling**: Resolves conflicts (if any)

**Outputs**:
- Architecture blueprint
- Business impact assessment
- Conflict resolutions
- Approved design

### Phase 3: Migration Planning

**Objective**: Plan migration to Azure MCA

**Agent Activities**:
1. **Leo Vance**: Designs MCA billing hierarchy
2. **Elena Bridges**: Validates plan with customer
3. **Final Report**: Generated by all agents

**Outputs**:
- MCA billing structure
- Customer validation
- Migration readiness report

## State Management

### Global State

The assessment state tracks:
- Current phase
- Budget and budget remaining
- Critical risks
- Agent contexts
- Findings and artifacts
- Active conflicts
- Events for visualization

### Handoff Pattern

**Purpose**: Reduce token usage by summarizing context

**How it works**:
1. Source agent completes task
2. Supervisor creates handoff packet with summarized context
3. Target agent receives only essential information
4. Context is scoped to task requirements

**Benefits**:
- 60%+ reduction in token usage
- Faster agent handoffs
- Better focus on task-specific context

### State Persistence

- **Storage**: Azure Cosmos DB
- **Free Tier**: 1,000 RU/s + 25 GB free for 12 months
- **Partition Key**: `assessment_id`
- **Recovery**: State can be loaded to resume assessments

## RAG Integration

### Google File Search

Agents use **Google File Search** (Gemini API) to query knowledge base:

- **Fully Managed**: Automatic chunking, embeddings, vector search
- **Cost-Effective**: $0.15 per million tokens for indexing, free queries
- **Agentic Retrieval**: Agents decide when to search and generate queries

### Knowledge Base Documents

Recommended documents to upload:
1. Azure Cloud Adoption Framework (CAF)
2. Azure Well-Architected Framework (WAF)
3. Microsoft Customer Agreement (MCA) guides
4. Azure Security Best Practices

### Agent RAG Usage

**Aris Thorne** queries:
- CAF assessment checklists
- Landing Zone architecture guidance
- Security best practices

**Leo Vance** queries:
- MCA billing hierarchy documentation
- Entra ID migration guides
- RBAC best practices

## Conflict Resolution

### Conflict Detection

The supervisor detects conflicts when:
- Security requirements conflict with business constraints
- Budget limitations block security implementations
- Timeline constraints prevent proper security measures

### Escalation Path

1. **Conflict Detected**: Supervisor identifies deadlock
2. **Escalation**: Routes to Marcus Sterling
3. **Resolution**: Marcus makes executive decision
4. **State Update**: Resolution recorded in state

### Example Conflict

```
Elena: "Client cannot accept 4-hour downtime for firewall insertion"
Aris: "Without firewall, environment is non-compliant with CAF"
Supervisor: Detects conflict → Escalates to Marcus
Marcus: "Approve weekend overtime budget. Proceed during Sunday maintenance window"
```

## Visualization

### SecAI Radar Chart

Real-time visualization showing security posture across 5 domains:
- Identity & Access
- Data Protection
- Network Security
- Governance
- Monitoring

**How it works**:
- Agents emit events as they complete tasks
- Events include impact scores (0-100)
- Radar chart updates in real-time
- Shows progress toward security maturity

### Event Stream

Structured events for visualization:
```json
{
  "timestamp": "2025-01-15T10:00:00Z",
  "agent_id": "aris_thorne",
  "domain": "Governance",
  "action": "CAF Knowledge Query",
  "impact_score": 80.0,
  "description": "Generated CAF assessment checklist"
}
```

## Getting Started

### Prerequisites

1. **Environment Variables**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"  # For RAG
   export COSMOS_ENDPOINT="..."  # For state persistence (optional)
   export COSMOS_KEY="..."  # For state persistence (optional)
   ```

2. **Dependencies**:
   ```bash
   pip install langgraph langchain langchain-openai google-generativeai plotly azure-cosmos
   ```

### Initialize System

```python
from src.orchestrator.initialize import initialize_orchestrator
from src.orchestrator.state import StateManager

# Auto-initializes Model Layer, RAG, and Cosmos DB
graph = initialize_orchestrator()

# Create initial state
state_manager = StateManager()
initial_state = state_manager.create_initial_state(
    assessment_id="assessment-001",
    tenant_id="tenant-alpha",
    budget=100000.0
)

# Run assessment workflow
final_state = await graph.run(initial_state)
```

### Manual Initialization

```python
from src.models import get_model_layer
from src.rag.factory import get_rag_retriever
from src.orchestrator import (
    StateManager, CosmosStatePersistence,
    Supervisor, LangGraphConfig, MultiAgentGraph
)

# Initialize components
model_layer = get_model_layer()
rag_retriever = get_rag_retriever(model_layer=model_layer)
cosmos_persistence = CosmosStatePersistence()
state_manager = StateManager(cosmos_persistence=cosmos_persistence)

# Create orchestrator
supervisor = Supervisor(state_manager, model_layer)
config = LangGraphConfig(model_layer, state_manager, rag_retriever)
graph = MultiAgentGraph(config, supervisor)
```

## Configuration

### Agent Personas

Configured in `config/agent_personas.yaml`:
- System prompts
- Personality traits
- Responsibilities
- Available tools

### RAG Configuration

Configured in `config/rag.yaml`:
- Provider selection (Google File Search)
- Agentic retrieval settings
- Knowledge base documents

### Model Configuration

Configured in `config/models.yaml`:
- Model roles (reasoning, classification, generation)
- Provider settings
- Model parameters

## Monitoring

### State Inspection

```python
# Load assessment state
state = await state_manager.load_state("assessment-001")

# Check current phase
print(f"Phase: {state['phase']}")

# View agent contexts
for agent_id, context in state['agent_contexts'].items():
    print(f"{agent_id}: {context.current_task}")

# View events
for event in state['events'][-10:]:  # Last 10 events
    print(f"{event['agent_id']}: {event['action']}")
```

### Cost Monitoring

**Cosmos DB**:
```bash
./scripts/check-cosmos-costs.sh
```

**Google File Search**:
- Monitor in Google Cloud Console
- Check API usage quotas
- Review file store storage

## Best Practices

### 1. Use Free Tier for Development

- Cosmos DB: Free tier (1,000 RU/s + 25 GB)
- Google File Search: Free tier (1 GB storage)

### 2. Monitor Token Usage

- Handoff pattern reduces tokens by 60%+
- Archive old assessments to reduce state size
- Use agentic retrieval to avoid unnecessary searches

### 3. Optimize RAG Queries

- Upload relevant documents to file store
- Use specific queries (not too broad)
- Let agents generate their own queries (agentic retrieval)

### 4. State Management

- Persist state after significant milestones
- Load state to resume interrupted assessments
- Archive completed assessments to Blob Storage

## Troubleshooting

### Agents Not Processing

- Check `current_agent` is set in state
- Verify handoff packets are created
- Review supervisor routing logic

### RAG Not Working

- Verify `GOOGLE_API_KEY` is set
- Check file store has documents
- Review RAG factory initialization

### State Not Persisting

- Verify Cosmos DB credentials
- Check free tier limits (1,000 RU/s)
- Review state serialization

## Related Documentation

- [Architecture](Architecture) - Complete architecture overview
- [AI Integration](AI-Integration) - AI features and configuration
- [RAG Integration](../RAG-INTEGRATION.md) - RAG setup and usage
- [Cosmos DB Setup](../COSMOS-DB-SETUP.md) - State persistence setup
- [Cosmos DB Cost Analysis](../COSMOS-DB-COST-ANALYSIS.md) - Cost optimization

---

**Last Updated**: 2025-01-27

