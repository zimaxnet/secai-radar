# SecAI Radar: Architecture Comparison Review

## Executive Summary

This document compares the archived version (`archive_v1`) with the current application structure. The migration represents a significant architectural shift from **Azure Functions (serverless)** to a **monolithic FastAPI backend** with a **React frontend**, while introducing a new **multi-agent AI system**.

---

## Architecture Changes

### Archive Version (v1)

**Backend:**
- **Platform**: Azure Functions (serverless)
- **Runtime**: Python 3.12+ 
- **Framework**: Azure Functions Core Tools
- **Orchestration**: Durable Functions with budget guardrails
- **Data Storage**: Azure Table Storage, Cosmos DB
- **AI Services**: Azure OpenAI (GPT-5)

**Frontend:**
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Routing**: React Router
- **UI Components**: Custom components with Tailwind CSS
- **Features**: Full assessment workflow UI (Dashboard, Controls, Tools, Gaps, Reports)

**API Structure:**
- Function-based endpoints (one function per feature)
- Route pattern: `/api/tenant/{tenantId}/...`
- Endpoints include:
  - Controls management
  - Tools inventory
  - Gaps analysis
  - Evidence classification
  - Multi-agent assessment orchestration
  - Report generation
  - AI recommendations

### Current Version (v2)

**Backend:**
- **Platform**: FastAPI (monolithic)
- **Runtime**: Python 3.x
- **Framework**: FastAPI + Uvicorn
- **Orchestration**: Custom orchestrator class
- **Data Storage**: Azure Blob Storage (referenced), but not fully implemented
- **AI Services**: Google Generative AI (Gemini 1.5 Pro)

**Frontend:**
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 7
- **Routing**: React Router 7
- **UI Components**: Custom components with Tailwind CSS 4 + Framer Motion
- **Features**: Agent showcase UI with interactive chat interfaces

**API Structure:**
- RESTful endpoints under `/agents/`
- Route pattern: `/agents/{agent_id}/chat`
- Endpoints:
  - Agent chat interfaces (7 agents)
  - File upload to knowledge base (Aris agent)

---

## Feature Comparison

### Removed Features (Not Yet Migrated)

1. **Security Assessment Workflow**
   - Domain-based control management
   - Control import (CSV/JSON)
   - Evidence collection and classification
   - Gap analysis based on tool capabilities vs control requirements
   - Assessment status tracking
   - Multi-tenant support with tenant isolation

2. **Data Management**
   - Azure Table Storage integration for controls
   - Cosmos DB integration for assessment state
   - Tool capability mapping system
   - Control requirements framework mapping

3. **Reporting & Visualization**
   - Dashboard with domain progress
   - Radar charts for progress visualization
   - Report generation with AI summaries
   - Gap analysis reports
   - Control detail views

4. **Orchestration System**
   - Durable Functions workflow engine
   - Budget guardrails (token/call limits)
   - Workflow YAML definitions
   - Activity functions for async processing

5. **AI Features (Azure OpenAI)**
   - Evidence classification
   - Gap explanations
   - Report summaries
   - AI recommendations for controls

6. **Enterprise Features**
   - Tenant tool inventory management
   - Tool configuration scoring
   - Multi-agent assessment orchestration
   - Realtime session management

### New Features

1. **Multi-Agent AI System**
   - 7 specialized agents:
     - **Aris**: Knowledge Base Guardian (framework knowledge)
     - **Leo**: Identity & Access Analyst
     - **Ravi**: Infrastructure Architect
     - **Kenji**: Findings Analyst
     - **Elena**: Business Impact Strategist
     - **Marcus**: Conflict Resolution
     - **Coordinator**: System Orchestrator
   - Each agent has specialized capabilities and personas
   - Chat-based interaction with each agent

2. **Modern UI/UX**
   - Beautiful agent showcase interface
   - Interactive agent cards with animations
   - Live chat interfaces embedded in agent details
   - Modern gradient designs and glassmorphism effects
   - Framer Motion animations

3. **Knowledge Base Integration**
   - File upload capability (Google GenAI File API)
   - RAG (Retrieval-Augmented Generation) support
   - Document-based context for agents (via Aris)

4. **Simplified Deployment**
   - Single backend server (vs. multiple Azure Functions)
   - Local development script (`start_app.sh`)
   - Easier local testing and debugging

---

## Technology Stack Changes

### Backend Dependencies

**Archive Version:**
```python
azure-functions>=1.18.0
azure-functions-durable>=1.2.8
azure-data-tables>=12.4.0
azure-storage-blob>=12.19.0
azure-keyvault-secrets>=4.7.0
azure-identity>=1.15.0
openai>=1.12.0  # Azure OpenAI
langgraph>=0.2.0
langchain>=0.3.0
google-generativeai>=0.8.0  # Secondary option
azure-cosmos>=4.5.0
```

**Current Version:**
```python
fastapi
uvicorn
google-generativeai  # Primary AI provider
azure-identity
azure-mgmt-resource
azure-storage-blob
python-dotenv
pydantic
requests
python-multipart
```

**Key Changes:**
- Removed: Azure Functions, Durable Functions, LangGraph, LangChain, Azure Cosmos, Azure Tables
- Added: FastAPI, Uvicorn
- Switched: Azure OpenAI → Google Generative AI (primary)

### Frontend Dependencies

**Archive Version:**
- React Router
- Recharts (for radar charts)
- Standard React hooks

**Current Version:**
- React 19 (latest)
- React Router 7 (latest)
- Framer Motion (animations)
- Lucide React (icons)
- Tailwind CSS 4 (latest)

---

## API Endpoints Comparison

### Archive Endpoints
```
GET    /api/tenant/{tenantId}/controls
POST   /api/tenant/{tenantId}/import
GET    /api/tenant/{tenantId}/tools
POST   /api/tenant/{tenantId}/tools
GET    /api/tenant/{tenantId}/gaps
GET    /api/tenant/{tenantId}/summary
POST   /api/tenant/{tenantId}/multi-agent-assessment
GET    /api/tenant/{tenantId}/multi-agent-assessment/{assessmentId}
POST   /api/orchestration/start
GET    /api/orchestration/{instanceId}
POST   /api/evidence/classify
POST   /api/report/generate
... (and more)
```

### Current Endpoints
```
GET    /health
POST   /agents/{agent_id}/chat
POST   /agents/aris/upload
```

**Observations:**
- Vast reduction in API surface area (from ~15+ endpoints to 3)
- Loss of tenant-scoped endpoints (multi-tenancy removed)
- Loss of assessment workflow endpoints
- Focus shifted to agent interaction only

---

## Code Structure Comparison

### Archive Backend Structure
```
archive_v1/api/
├── controls/          # Control management
├── domains/           # Domain queries
├── evidence/          # Evidence collection
├── gaps/              # Gap analysis
├── tools/             # Tool inventory
├── multi_agent_assessment/  # Assessment orchestration
├── orchestration/     # Durable Functions workflows
├── report/            # Report generation
├── shared/            # Shared utilities
│   ├── ai_service.py  # Azure OpenAI wrapper
│   ├── scoring.py     # Capability scoring
│   └── tool_research.py
└── seeds/             # Seed data (JSON files)
```

### Current Backend Structure
```
backend/
├── main.py            # FastAPI app entry
└── src/
    ├── orchestrator.py      # Agent orchestrator
    ├── agents/              # Agent implementations
    │   ├── base.py
    │   ├── aris.py
    │   ├── leo.py
    │   ├── ravi.py
    │   ├── kenji.py
    │   ├── elena.py
    │   ├── marcus.py
    │   └── coordinator.py
    └── integrations/
        └── google_genai.py  # Google AI wrapper
```

**Observations:**
- Simplified structure (no function-per-feature)
- Agent-centric organization
- Removed shared utilities (scoring, tool research, etc.)
- Removed seed data management

---

## Frontend Route Comparison

### Archive Routes
```typescript
/                               # Landing page
/assessments                    # Assessment list
/tenant/:id/dashboard          # Domain progress dashboard
/tenant/:id/controls           # Control management
/tenant/:id/tools              # Tool inventory
/tenant/:id/gaps               # Gap analysis
/tenant/:id/report             # Assessment report
/tenant/:id/domain/:domainCode # Domain detail
/tenant/:id/control/:controlId # Control detail
/tenant/:id/assessment         # Assessment overview
/tenant/:id/setup              # Assessment setup
```

### Current Routes
```typescript
/                              # Agent showcase (only route)
```

**Observations:**
- Complete removal of assessment workflow UI
- Single-page application focused on agent showcase
- No tenant management UI
- No data visualization (charts, dashboards)

---

## Data Model Comparison

### Archive Data Models

**Controls (Table Storage):**
- PartitionKey: `{tenant}|{domain}`
- RowKey: `ControlID`
- Fields: status, evidence, notes, etc.

**TenantTools (Table Storage):**
- PartitionKey: `{tenant}`
- RowKey: `vendorToolId`
- Fields: enabled, configScore, etc.

**Assessment State (Cosmos DB):**
- Assessment ID, tenant ID, findings, conflicts, budget usage, phase

**Seed Data:**
- `seeds_control_requirements.json` - Framework mappings
- `seeds_tool_capabilities.json` - Tool capability catalog
- `seeds_vendor_tools.json` - Vendor tool definitions
- `seeds_domain_codes.json` - Domain code mappings

### Current Data Models

**None explicitly defined** - The current version does not persist data beyond in-memory agent state.

---

## Assessment Workflow Comparison

### Archive Workflow

1. **Setup Phase**
   - Import controls (CSV/JSON)
   - Configure tenant tools
   - Set up assessment scope

2. **Evidence Collection**
   - Collect evidence per control
   - Classify evidence (AI-powered)
   - Attach evidence to controls

3. **Analysis Phase**
   - Calculate capability gaps
   - Compare tool capabilities vs. control requirements
   - Identify hard gaps (missing) vs. soft gaps (config issues)

4. **Orchestration**
   - Multi-agent assessment workflow
   - Durable Functions orchestration
   - Budget tracking (tokens, API calls)
   - Conflict resolution between agents

5. **Reporting**
   - Generate executive summary (AI-powered)
   - Create detailed reports
   - Visualize progress (radar charts)

### Current Workflow

1. **Agent Interaction**
   - Select an agent from showcase
   - Chat with individual agents
   - Upload documents to Aris (knowledge base)
   - Receive agent responses

**Observations:**
- No structured assessment workflow
- No data persistence
- No progress tracking
- Focus shifted to conversational AI only

---

## Migration Recommendations

### To Restore Full Functionality

1. **Add Back Data Persistence**
   - Integrate Azure Table Storage for controls
   - Add Cosmos DB for assessment state
   - Implement data models in FastAPI

2. **Restore Assessment Endpoints**
   - Implement tenant-scoped endpoints
   - Add control management APIs
   - Restore gap analysis logic
   - Add evidence collection endpoints

3. **Integrate Assessment UI**
   - Add routing for assessment pages
   - Restore dashboard and visualization
   - Add control detail views
   - Implement gap analysis UI

4. **Hybrid Approach**
   - Keep new agent system as enhancement
   - Integrate agents into assessment workflow
   - Use agents for AI recommendations (Elena, Marcus)
   - Use Aris for framework queries during assessment

5. **Unify AI Providers**
   - Support both Azure OpenAI and Google GenAI
   - Use Azure OpenAI for structured tasks (classification, reports)
   - Use Google GenAI for conversational agents
   - Implement fallback mechanisms

6. **Orchestration**
   - Implement workflow engine (simpler than Durable Functions)
   - Add budget tracking
   - Integrate agent coordination for assessments

---

## Conclusion

The current version represents a **pivot toward a conversational AI agent showcase**, sacrificing the comprehensive security assessment workflow that existed in v1. While the new agent system is innovative and well-designed, the loss of the assessment management features significantly reduces the practical utility of the application.

**Recommendation:** The architecture should evolve to **combine both approaches**:
- Keep the modern agent showcase UI
- Restore the assessment workflow features
- Integrate agents into the assessment process
- Maintain the FastAPI backend but expand its capabilities

This would create a hybrid system that combines structured assessment workflows with intelligent agent assistance.

