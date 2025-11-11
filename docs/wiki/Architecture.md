---
layout: default
title: Architecture
permalink: /Architecture/
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

See [Model Integration](../model-integration.md) for details.

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

See [Data Model](../data-model.md) for detailed schemas.

---

## Layer 4: Orchestration Layer

### Components

- **Orchestrator**: Main workflow coordinator
- **Workflow Engine**: Multi-step task execution
- **Planning**: Collector selection
- **Analysis**: AI-powered analysis
- **Review**: Self-review loop

### Workflow

1. **Plan**: Decide which collectors to call
2. **Collect**: Gather evidence (Bronze)
3. **Normalize**: Transform to Silver
4. **Embed**: Create Gold/RAG chunks
5. **Analyze**: AI analysis per domain
6. **Review**: Self-review loop
7. **Generate**: Report assembly

### Responsibilities

- Coordinate multi-step workflows
- Manage workflow state
- Handle errors and retries
- Provide progress updates

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

- [Blueprint](../blueprint.md) - Complete architecture blueprint
- [Data Model](../data-model.md) - Data layer schemas
- [Model Integration](../model-integration.md) - Model layer details
- [Implementation Plan](../implementation-plan.md) - Implementation details

---

**Related**: [Installation](/wiki/Installation) | [Configuration](/wiki/Configuration)

