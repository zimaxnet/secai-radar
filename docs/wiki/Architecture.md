---
layout: default
title: Architecture
---

# Architecture Overview

Complete architecture overview for SecAI Radar.

---

## 5-Layer Architecture

SecAI Radar follows a **5-layer architecture**:

1. **Infrastructure Layer** - Containerized API + worker
2. **Model Layer** - Role-based AI models
3. **Data Layer** - Bronze/Silver/Gold data patterns
4. **Orchestration Layer** - Multi-step AI workflows
5. **Application Layer** - Web UI

---

## Layer 1: Infrastructure Layer

### Components

- **Containerized API**: RESTful API service
- **Background Worker**: Long-running assessment jobs
- **Configuration Management**: Environment variables and secrets

### Responsibilities

- Handle HTTP requests
- Process background jobs
- Manage configuration and secrets
- Provide authentication/authorization

### Technologies

- Container runtime (Docker, Kubernetes)
- API framework (Flask/FastAPI)
- Job queue (Celery, Azure Queue)
- Configuration (Environment variables, Key Vault)

---

## Layer 2: Model Layer

### Components

- **Model Configuration**: `config/models.yaml`
- **Model Providers**: Azure OpenAI, etc.
- **Model Abstraction**: Role-based access

### Model Roles

- **Reasoning Model**: Multi-step security analysis
- **Classification Model**: Evidence classification
- **Generation Model**: Report generation

### Responsibilities

- Provide role-based model access
- Abstract model providers
- Handle model configuration
- Manage model lifecycle

### Technologies

- Azure OpenAI Service
- Model abstraction layer
- Configuration management

See [Model Integration](docs/wiki/model-integration.md) for details.

---

## Layer 3: Data Layer

### Bronze Layer (Raw Evidence)

**Purpose**: Store raw, unprocessed evidence

**Characteristics**:
- Immutable (append-only)
- Timestamped
- Preserves original structure

**Storage**:
- Azure Blob Storage
- JSON format

**Schema**:
```json
{
  "source": "cloud_api",
  "collected_at": "2025-01-15T10:00:00Z",
  "scope": {
    "tenant": "tenant-alpha",
    "subscription": "subscription-001"
  },
  "payload": { /* raw provider response */ }
}
```

### Silver Layer (Normalized)

**Purpose**: Normalize evidence into common data model

**Characteristics**:
- Normalized structure
- Mapped to controls/domains
- Queryable

**Storage**:
- Azure Table Storage / Cosmos DB
- Structured records

**Schema**:
```json
{
  "resource_id": "/subscriptions/.../storageAccounts/appfiles001",
  "resource_type": "storage_account",
  "tenant": "tenant-alpha",
  "domain": "Logging & Monitoring",
  "control_id": "GEN-LM-001",
  "status": "non_compliant",
  "evidence_ref": "bronze/2025-01-15/cloud_api/storage.json"
}
```

### Gold/RAG Layer (Embedded)

**Purpose**: Embeddings for AI/RAG retrieval

**Characteristics**:
- Text chunks
- Vector embeddings
- Searchable

**Storage**:
- Vector database (Azure Cognitive Search, Pinecone)
- Embeddings + metadata

**Schema**:
```json
{
  "chunk_id": "gold-tenant-alpha-NET-SEC-NET-0001-0",
  "text_content": "Network Security Group NSG-001...",
  "embedding": { "vector": [...], "model": "text-embedding-ada-002" },
  "silver_ref": "silver-{id}"
}
```

See [Data Model](docs/wiki/data-model.md) for detailed schemas.

---

## Layer 4: Orchestration Layer

### Components

- **Multi-Agent Orchestrator**: LangGraph-based agent coordination
- **Supervisor**: Hierarchical routing and task delegation
- **7 Agent Personas**: Specialized agents for different roles
- **State Management**: Cosmos DB persistence
- **Handoff Pattern**: Efficient context management
- **Workflow Engine**: Three-phase workflow execution
- **Planning**: Collector selection
- **Analysis**: AI-powered analysis
- **Review**: Self-review loop

### Multi-Agent System

SecAI Radar implements a **7-agent multi-agent system** using **LangGraph** for orchestration:

#### Agent Personas

1. **Marcus Sterling** (Senior Manager)
   - Executive decision-making
   - Conflict resolution
   - Budget approvals
   - Phase transitions

2. **Elena Bridges** (Relationship Manager)
   - Business impact assessment
   - Customer validation
   - Downtime calculations
   - Communication

3. **Dr. Aris Thorne** (Principal Architect)
   - CAF knowledge base queries
   - Architecture design
   - Threat modeling
   - Security strategy

4. **Leo Vance** (Security Architect - IAM)
   - Identity migration planning
   - MCA billing hierarchy design
   - Conditional Access policies
   - RBAC design

5. **Priya Desai** (Program Manager - Offshore)
   - Code/documentation review
   - Task assignment
   - Quality gates
   - Delivery assurance

6. **Ravi Patel** (Security Engineer)
   - Infrastructure scanning
   - IaC generation (Terraform/Bicep)
   - Policy implementation
   - Vulnerability scanning

7. **Kenji Sato** (Program Manager)
   - Schedule tracking
   - Status reporting
   - Dependency management
   - Findings collation

#### Workflow Phases

**Phase 1: Assessment and Discovery**
- Aris queries CAF knowledge base
- Leo analyzes identity configuration
- Ravi scans infrastructure
- Kenji collates findings

**Phase 2: Design and Conflict Resolution**
- Aris designs Azure Landing Zone
- Elena assesses business impact
- Marcus resolves conflicts (if any)

**Phase 3: Migration Planning**
- Leo designs MCA billing hierarchy
- Elena validates with customer
- Final report generation

### State Management

- **Global State**: Assessment state with agent contexts
- **Handoff Pattern**: Context summarization for token efficiency
- **Persistence**: Azure Cosmos DB (Free Tier supported)
- **Event Stream**: Real-time events for visualization

### RAG Integration

- **Google File Search**: Managed RAG for knowledge base
- **Agentic Retrieval**: Agents decide when to search
- **Knowledge Base**: CAF, WAF, MCA guides, security best practices

### Responsibilities

- Coordinate multi-agent workflows
- Manage workflow state and handoffs
- Handle errors and retries
- Provide progress updates
- Emit events for visualization

---

## Layer 5: Application Layer

### Components

- **Web UI**: React application
- **Dashboard**: Overview and metrics
- **Controls**: Control management
- **Tools**: Tool configuration
- **Gaps**: Gap analysis

### Technologies

- React + TypeScript
- Vite build tool
- Tailwind CSS
- Recharts (visualizations)

---

## Data Flow

### Assessment Flow

```
1. User starts assessment
   ↓
2. Orchestrator plans collectors
   ↓
3. Collectors gather evidence → Bronze
   ↓
4. Normalizers transform → Silver
   ↓
5. Embeddings create → Gold/RAG
   ↓
6. AI analyzes per domain
   ↓
7. Report generated
   ↓
8. Results displayed in UI
```

### Real-time Flow

```
User Action → UI → API → Data Layer
                    ↓
                   Model Layer (if needed)
                    ↓
                   Response → UI
```

---

## Security

### Authentication

- Azure Static Web Apps authentication
- Azure AD / Entra ID integration
- Role-based access control (RBAC)

### Data Security

- Tenant-scoped data
- No hardcoded credentials
- Secure API communication
- Encryption at rest and in transit

### Best Practices

- Principle of least privilege
- Secure configuration management
- Regular security audits
- Vulnerability scanning

---

## Scalability

### Horizontal Scaling

- API can scale horizontally
- Worker processes can scale independently
- Data layer supports distributed storage

### Performance

- Caching for frequently accessed data
- Async processing for long-running tasks
- Connection pooling
- Query optimization

---

## Deployment

### Containerized Deployment

- Docker containers
- Kubernetes orchestration (optional)
- Container registry

### Cloud Deployment

- Azure Static Web Apps (UI)
- Azure Functions (API)
- Azure Storage (data)
- Azure OpenAI (AI)

---

## Monitoring

### Metrics

- API request rates
- Error rates
- Response times
- Worker job status

### Logging

- Application logs
- Error logs
- Audit logs
- Performance logs

### Observability

- Health checks
- Status endpoints
- Metrics dashboards
- Alerting

---

## Extensibility

### Custom Collectors

- Implement collector interface
- Register in collector registry
- Deploy with application

### Custom Normalizers

- Implement normalizer interface
- Register in normalizer registry
- Handle specific resource types

### Custom Models

- Configure in `config/models.yaml`
- Add model provider if needed
- Use role-based access

---

## References

- [Blueprint](docs/wiki/blueprint.md) - Complete architecture blueprint
- [Data Model](docs/wiki/data-model.md) - Data layer schemas
- [Model Integration](docs/wiki/model-integration.md) - Model layer details
- [Implementation Plan](docs/wiki/implementation-plan.md) - Implementation details

---

**Related**: [Installation](/wiki/Installation) | [Configuration](/wiki/Configuration)
