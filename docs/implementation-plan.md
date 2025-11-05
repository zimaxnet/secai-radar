# SecAI Radar — Comprehensive Implementation Plan

> Complete roadmap for building all 5 layers of the AI Stack according to `blueprint.md`

---

## Current Status Assessment

### ✅ What's Built

1. **Model Layer** ✅
   - `src/models/` — Complete Model Layer abstraction
   - `config/models.yaml` — GPT-5-chat configuration
   - Role-based access (reasoning, classification, generation)
   - Azure OpenAI provider implementation

2. **Documentation** ✅
   - `docs/blueprint.md` — Complete architecture blueprint
   - `docs/data-model.md` — Bronze/Silver schemas
   - `docs/report-template.md` — Report template
   - `docs/model-integration.md` — Model integration guide

3. **Legacy Code** (Needs Migration)
   - `api/` — Azure Functions (old structure)
   - `web/` — React UI (needs alignment with new architecture)
   - `seeds/` — Framework data (needs migration to `config/frameworks.yaml`)

### ❌ What's Missing

1. **Infrastructure Layer** — Containerized API + worker
2. **Data Layer** — Bronze/Silver/Gold implementation
3. **Orchestration Layer** — Complete workflow implementation
4. **Collectors** — Cloud discovery modules
5. **Normalizers** — Bronze → Silver transformation
6. **RAG Layer** — Embeddings and search
7. **Report Builder** — Markdown/HTML/DOCX generation
8. **API Alignment** — REST endpoints aligned with blueprint

---

## Layer-by-Layer Implementation Plan

---

## 1. Infrastructure Layer

**Goal**: Containerized API + worker with background jobs for assessment runs

### 1.1 Containerized API

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create `Dockerfile` for API container
- [ ] Create `docker-compose.yml` for local development
- [ ] Migrate from Azure Functions to containerized API
  - Option A: Flask/FastAPI Python app
  - Option B: Keep Azure Functions but containerize
- [ ] Create `src/api/` with REST endpoints:
  - `POST /assessments` — Start assessment run
  - `GET /assessments` — List assessment runs
  - `GET /assessments/:id` — Get assessment details
  - `GET /assessments/:id/report` — Download report
  - `POST /assessments/:id/cancel` — Cancel running assessment
- [ ] Implement authentication/authorization
- [ ] Add health check endpoint

**Files to Create**:
```
src/api/
  __init__.py
  app.py                 # Main API application
  routes/
    __init__.py
    assessments.py       # Assessment endpoints
    runs.py              # Run management
    health.py            # Health checks
  middleware/
    __init__.py
    auth.py              # Authentication middleware
    logging.py           # Request logging
  config.py              # API configuration
```

**Dependencies**:
- Flask/FastAPI
- Azure SDK (for storage/authentication)
- Model Layer (`src/models/`)

### 1.2 Background Worker

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create worker service for long-running assessment runs
- [ ] Implement job queue (Azure Queue Storage or similar)
- [ ] Create `src/worker/`:
  - Job processor
  - Assessment runner
  - Error handling and retry logic
- [ ] Add job status tracking
- [ ] Implement progress updates

**Files to Create**:
```
src/worker/
  __init__.py
  worker.py              # Main worker service
  job_processor.py       # Process assessment jobs
  queue_client.py        # Queue operations
  status_tracker.py      # Track job progress
```

**Dependencies**:
- Job queue library (Celery or Azure Queue)
- Orchestrator (`src/orchestrator/`)

### 1.3 Configuration Management

**Status**: ✅ Partially Complete

**Tasks**:
- [x] `config/models.yaml` — Model configuration
- [ ] `config/frameworks.yaml` — Control frameworks (migrate from `seeds/`)
- [ ] Environment variable management
- [ ] Secrets management (Azure Key Vault or similar)
- [ ] Configuration validation

**Files to Create/Update**:
```
config/
  models.yaml            ✅ Exists
  frameworks.yaml       ❌ Need to create
  app.yaml              ❌ Application config
  .env.example          ❌ Example env vars
```

---

## 2. Model Layer

**Goal**: Role-based model access (reasoning, classification, generation)

**Status**: ✅ Complete

**What's Done**:
- ✅ `src/models/` — Complete Model Layer abstraction
- ✅ `config/models.yaml` — GPT-5-chat configuration
- ✅ Azure OpenAI provider
- ✅ Role-based access methods

**Remaining Tasks**:
- [ ] Add error handling and retry logic
- [ ] Add fallback model support
- [ ] Add usage tracking and metrics
- [ ] Add rate limiting
- [ ] Unit tests

**Files Status**:
```
src/models/
  __init__.py            ✅ Complete
  config.py              ✅ Complete
  providers.py            ✅ Complete
  model_layer.py          ✅ Complete
  tests/                  ❌ Need to add
    __init__.py
    test_model_layer.py
    test_providers.py
```

---

## 3. Data Layer

**Goal**: Bronze (raw), Silver (normalized), Gold/RAG (embedded)

### 3.1 Bronze Layer (Raw Evidence)

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create Bronze storage interface
- [ ] Implement storage backend (Azure Blob Storage or similar)
- [ ] Create Bronze schema validator
- [ ] Add metadata management
- [ ] Implement retention policies

**Files to Create**:
```
src/data/
  __init__.py
  bronze/
    __init__.py
    storage.py            # Bronze storage interface
    schema.py             # Bronze schema validation
    metadata.py          # Metadata management
  silver/
    __init__.py
    storage.py            # Silver storage interface
    schema.py             # Silver schema validation
  gold/
    __init__.py
    embeddings.py         # Embedding generation
    search.py             # Vector search
    storage.py            # Vector database interface
```

**Dependencies**:
- Azure Blob Storage SDK
- JSON schema validation
- Vector database (Azure Cognitive Search, Pinecone, etc.)

### 3.2 Silver Layer (Normalized)

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create Silver storage interface
- [ ] Implement database (Azure Table Storage, Cosmos DB, or PostgreSQL)
- [ ] Create Silver schema validator
- [ ] Add indexing for queries
- [ ] Implement data lineage tracking

**Files to Create**:
```
src/data/silver/
  storage.py              # Silver storage
  schema.py               # Silver schema
  normalizer.py           # Base normalizer interface
  lineage.py              # Data lineage tracking
```

**Dependencies**:
- Database SDK (Azure Tables/Cosmos/PostgreSQL)
- Normalizers (`src/normalizers/`)

### 3.3 Gold/RAG Layer (Embeddings & Search)

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create embedding service
- [ ] Implement chunking strategy
- [ ] Create vector database interface
- [ ] Implement semantic search
- [ ] Add metadata filtering

**Files to Create**:
```
src/data/gold/
  embeddings.py           # Generate embeddings
  chunking.py             # Text chunking strategy
  search.py               # Semantic search
  storage.py              # Vector database interface
```

**Dependencies**:
- Embedding model (Azure OpenAI embeddings or similar)
- Vector database (Azure Cognitive Search, Pinecone, Weaviate)

---

## 4. Orchestration Layer

**Goal**: Multi-step AI workflows (plan → collect → normalize → analyze → report)

**Status**: ⚠️ Partial (Example code only)

**Tasks**:
- [ ] Create orchestrator service
- [ ] Implement assessment workflow:
  1. Plan collectors to call
  2. Call collectors (async)
  3. Normalize bronze → silver
  4. Generate embeddings (silver → gold)
  5. AI analysis per domain
  6. Self-review loop
  7. Assemble report sections
- [ ] Add error handling and recovery
- [ ] Add progress tracking
- [ ] Implement self-review workflow

**Files to Create**:
```
src/orchestrator/
  __init__.py
  orchestrator.py         # Main orchestrator
  workflow.py              # Assessment workflow
  planning.py              # Plan collectors
  analysis.py              # AI analysis per domain
  review.py                # Self-review loop
  example_usage.py         ✅ Exists (example)
```

**Dependencies**:
- Model Layer (`src/models/`)
- Collectors (`src/collectors/`)
- Normalizers (`src/normalizers/`)
- RAG Layer (`src/data/gold/`)
- Report Builder (`src/report/`)

---

## 5. Collectors

**Goal**: Cloud discovery modules (generic names)

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create collector interface/base class
- [ ] Implement example collectors:
  - `collectInventory` — Resource inventory
  - `collectPolicyState` — Policy configuration
  - `collectSecurityFindings` — Security findings
  - `collectLoggingConfig` — Logging configuration
- [ ] Add collector registry
- [ ] Implement async collection
- [ ] Add error handling and retry

**Files to Create**:
```
src/collectors/
  __init__.py
  base.py                  # Base collector interface
  registry.py              # Collector registry
  inventory/
    __init__.py
    collector.py           # Inventory collector
  policy/
    __init__.py
    collector.py           # Policy collector
  security/
    __init__.py
    collector.py           # Security findings collector
  logging/
    __init__.py
    collector.py           # Logging config collector
```

**Dependencies**:
- Cloud SDK (Azure SDK, AWS SDK, etc.)
- Bronze storage (`src/data/bronze/`)

---

## 6. Normalizers

**Goal**: Bronze → Silver transformation

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create normalizer interface/base class
- [ ] Implement normalizers by resource type:
  - Storage account normalizer
  - Network security group normalizer
  - RBAC normalizer
  - etc.
- [ ] Add framework mapping (control_id, domain)
- [ ] Implement classification model integration
- [ ] Add confidence scoring

**Files to Create**:
```
src/normalizers/
  __init__.py
  base.py                  # Base normalizer interface
  registry.py              # Normalizer registry
  storage_account.py       # Storage account normalizer
  nsg.py                   # NSG normalizer
  rbac.py                  # RBAC normalizer
  classification.py        # Use classification_model
```

**Dependencies**:
- Bronze storage (`src/data/bronze/`)
- Silver storage (`src/data/silver/`)
- Classification model (`src/models/`)
- Frameworks (`config/frameworks.yaml`)

---

## 7. RAG Layer

**Goal**: Embeddings and semantic search for AI context

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create embedding service
- [ ] Implement chunking strategy
- [ ] Create vector database interface
- [ ] Implement semantic search
- [ ] Add metadata filtering

**Files to Create**:
```
src/rag/
  __init__.py
  embeddings.py            # Embedding service
  chunking.py               # Text chunking
  search.py                 # Semantic search
  vector_db.py              # Vector database interface
```

**Dependencies**:
- Gold storage (`src/data/gold/`)
- Embedding model (Azure OpenAI embeddings)

---

## 8. Report Builder

**Goal**: Assemble Markdown/HTML/DOCX reports

**Status**: ❌ Not Started

**Tasks**:
- [ ] Create report builder service
- [ ] Implement template engine
- [ ] Generate report sections:
  - Executive summary
  - Overall findings
  - Domain details
  - Remediation roadmap
- [ ] Add Markdown → HTML conversion
- [ ] Add Markdown → DOCX conversion
- [ ] Implement report caching

**Files to Create**:
```
src/report/
  __init__.py
  builder.py               # Report builder
  templates.py             # Report templates
  sections/
    __init__.py
    executive_summary.py   # Executive summary generator
    findings.py            # Findings generator
    roadmap.py             # Roadmap generator
  converters/
    __init__.py
    markdown_to_html.py    # Markdown → HTML
    markdown_to_docx.py    # Markdown → DOCX
```

**Dependencies**:
- Generation model (`src/models/`)
- Report template (`docs/report-template.md`)
- Assessment results (Silver/Gold data)

---

## 9. Application Layer (UI)

**Goal**: Web UI for browsing runs and downloading reports

**Status**: ⚠️ Partial (Legacy UI exists)

**Tasks**:
- [ ] Align UI with new architecture
- [ ] Create assessment runs list view
- [ ] Create run detail view:
  - Summary
  - Findings by domain
  - AI narrative with evidence links
- [ ] Add download report functionality
- [ ] Add real-time progress updates
- [ ] Remove hardcoded customer/vendor references

**Files to Update**:
```
ui/webapp/              # Rename from web/
  src/
    routes/
      Assessments.tsx    # Assessment runs list
      AssessmentDetail.tsx  # Run detail view
      Reports.tsx        # Report download
    components/
      RunList.tsx
      DomainSummary.tsx
      FindingsList.tsx
      ReportDownload.tsx
```

**Dependencies**:
- API endpoints (`src/api/`)
- WebSocket for progress updates (optional)

---

## 10. Configuration & Frameworks

**Goal**: Framework definitions in YAML

**Status**: ⚠️ Partial

**Tasks**:
- [x] `config/models.yaml` — Model configuration ✅
- [ ] `config/frameworks.yaml` — Migrate from `seeds/`
  - Convert `seeds/domain_codes.json` → YAML
  - Convert `seeds/control_requirements.json` → YAML
  - Add control definitions with severity
- [ ] Create framework loader
- [ ] Add framework validation

**Files to Create**:
```
config/
  frameworks.yaml        # Control frameworks
  framework_loader.py    # Load and validate frameworks
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Infrastructure Layer — Containerized API
- [ ] Data Layer — Bronze/Silver storage interfaces
- [ ] Configuration — Frameworks migration
- [ ] Basic orchestrator skeleton

### Phase 2: Collection & Normalization (Weeks 3-4)
- [ ] Collectors — At least 2 example collectors
- [ ] Normalizers — Bronze → Silver transformation
- [ ] Framework mapping — Control/domain classification

### Phase 3: AI Integration (Weeks 5-6)
- [ ] Orchestrator — Complete workflow
- [ ] AI Analysis — Per-domain analysis using reasoning_model
- [ ] Self-review — Iterative review loop

### Phase 4: RAG & Search (Week 7)
- [ ] Gold Layer — Embeddings and vector storage
- [ ] RAG Service — Semantic search for context
- [ ] Integration with AI analysis

### Phase 5: Reporting (Week 8)
- [ ] Report Builder — Section generation
- [ ] Template Engine — Markdown/HTML/DOCX
- [ ] Report Assembly — Full report generation

### Phase 6: UI & Polish (Weeks 9-10)
- [ ] UI Alignment — Update with new architecture
- [ ] API Integration — Connect UI to new endpoints
- [ ] Testing & Documentation
- [ ] Deployment preparation

---

## Dependencies & Prerequisites

### Required Services
- Azure OpenAI (GPT-5-chat) ✅ Configured
- Azure Blob Storage (Bronze)
- Azure Table Storage / Cosmos DB (Silver)
- Vector Database (Gold/RAG) — Azure Cognitive Search or similar
- Container Registry (for deployment)

### Required Libraries
- Python:
  - `azure-identity` ✅
  - `openai` ✅
  - `pyyaml` ✅
  - `azure-storage-blob`
  - `azure-data-tables` or `azure-cosmos`
  - `flask` or `fastapi`
  - `celery` or Azure Queue SDK
  - `pydantic` (for validation)
- TypeScript/JavaScript:
  - React (existing)
  - API client updates

---

## Testing Strategy

### Unit Tests
- [ ] Model Layer tests
- [ ] Collector tests
- [ ] Normalizer tests
- [ ] Report builder tests

### Integration Tests
- [ ] End-to-end assessment workflow
- [ ] Bronze → Silver → Gold pipeline
- [ ] Report generation

### E2E Tests
- [ ] Full assessment run
- [ ] UI workflows

---

## Migration Plan

### From Legacy Code
1. **Migrate `api/` Azure Functions** → `src/api/` containerized API
2. **Migrate `seeds/`** → `config/frameworks.yaml`
3. **Update `web/`** → `ui/webapp/` aligned with new architecture
4. **Preserve existing functionality** during migration

### Data Migration
- [ ] Migrate existing Controls data to Silver format
- [ ] Preserve tenant data
- [ ] Update schema versions

---

## Success Criteria

### MVP Definition
- ✅ Can start assessment run
- ✅ Collectors gather bronze evidence
- ✅ Normalizers create silver records
- ✅ AI analyzes findings per domain
- ✅ Report generated (Markdown)
- ✅ UI displays assessment results
- ✅ Download report works

### Quality Gates
- [ ] All 5 layers implemented
- [ ] No hardcoded customer/vendor names
- [ ] Role-based model access
- [ ] Bronze/Silver/Gold separation
- [ ] End-to-end workflow functional

---

## Next Steps

1. **Start with Infrastructure Layer** — Containerized API
2. **Build Data Layer interfaces** — Bronze/Silver storage
3. **Create first collector** — Example implementation
4. **Create first normalizer** — Bronze → Silver
5. **Integrate orchestrator** — Complete workflow

---

## References

- `docs/blueprint.md` — Architecture blueprint
- `docs/data-model.md` — Data schemas
- `docs/model-integration.md` — Model Layer guide
- `docs/report-template.md` — Report template

