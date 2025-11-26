# SecAI Radar API (Azure Functions - Python)

Azure Functions backend for SecAI Radar security assessment platform.

## API Endpoints

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/domains` | GET | List all security domains |
| `/api/tools/catalog` | GET | Get vendor tools catalog |
| `/api/tenant/{tenantId}/controls` | GET | List controls for tenant |
| `/api/tenant/{tenantId}/import` | POST | Import controls (CSV/JSON) |
| `/api/tenant/{tenantId}/tools` | GET/POST | Tenant tool inventory |
| `/api/tenant/{tenantId}/summary` | GET | Assessment summary by domain |
| `/api/tenant/{tenantId}/gaps` | GET | Gap analysis with coverage |

### AI-Powered Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tenant/{tenantId}/ai/recommendations` | GET | AI recommendations for controls |
| `/api/tenant/{tenantId}/ai/help` | POST | Contextual AI assistance |
| `/api/tenant/{tenantId}/ai/usage` | GET | AI usage metrics |
| `/api/tenant/{tenantId}/report` | GET | Generate assessment report |

### Evidence Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tenant/{tenantId}/evidence/{controlId}` | GET/POST | Evidence upload/list |
| `/api/tenant/{tenantId}/evidence/classify` | POST | AI evidence classification |

### Voice & Orchestration
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/realtime/session` | POST | Azure OpenAI Realtime proxy |
| `/api/tenant/{tenantId}/multi-agent-assessment` | GET/POST | Multi-agent workflow |
| `/api/orchestration/start` | POST | Durable workflow starter |
| `/api/tool-research` | GET/POST | AI tool research |

## Local Development

```bash
# Prerequisites
- Python 3.12+
- Azure Functions Core Tools
- Azurite (for local storage emulation)

# Setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start Azurite for local storage
azurite

# Start Functions
func start
```

## Environment Variables

```bash
# Storage
TABLES_CONN="UseDevelopmentStorage=true"
BLOBS_CONN="UseDevelopmentStorage=true"

# Azure OpenAI (for AI features)
AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_DEPLOYMENT="gpt-4"

# Voice Features
AZURE_OPENAI_REALTIME_ENDPOINT="wss://your-instance.openai.azure.com/"
AZURE_OPENAI_REALTIME_KEY="your-key"
AZURE_OPENAI_REALTIME_DEPLOYMENT="gpt-realtime"

# Cosmos DB (for multi-agent state)
COSMOS_ENDPOINT="https://your-cosmos.documents.azure.com:443/"
COSMOS_KEY="your-key"

# Key Vault (optional)
KEY_VAULT_URL="https://your-vault.vault.azure.net/"
```

## Data Model

### Tables
- **Controls**: `PartitionKey={tenant}|{domain}`, `RowKey=ControlID`
- **TenantTools**: `PartitionKey={tenant}`, `RowKey=vendorToolId`
- **Evidence**: `PartitionKey={tenant}`, `RowKey={controlId}|{fileName}`
- **AiUsage**: `PartitionKey={tenant}`, `RowKey={workflow}-{uuid}`

### Seeds (JSON catalogs)
- `seeds_domain_codes.json` - Security domain codes and names
- `seeds_vendor_tools.json` - Vendor tool catalog
- `seeds_tool_capabilities.json` - Tool→Capability strength mappings
- `seeds_control_requirements.json` - Control→Capability requirements

## Shared Modules

Located in `shared/`:
- `utils.py` - Storage clients, JSON response helpers, CORS
- `scoring.py` - Deterministic coverage scoring engine
- `ai_service.py` - Azure OpenAI integration
- `key_vault.py` - Azure Key Vault integration
- `workflow_loader.py` - Durable workflow loading
- `tool_research.py` - AI-powered tool research

## Architecture

```
api/
├── shared/              # Shared utilities
├── domains/             # GET /api/domains
├── controls/            # GET /api/tenant/{id}/controls
├── gaps/                # GET /api/tenant/{id}/gaps
├── ai_help/             # POST /api/tenant/{id}/ai/help
├── ai_recommendations/  # GET /api/tenant/{id}/ai/recommendations
├── realtime_session/    # POST /api/realtime/session
├── orchestration/       # Durable Functions orchestrator
├── orchestration_start/ # HTTP starter
├── orchestration_activity/ # Activity functions
└── seeds_*.json         # Seed data catalogs
```

## Notes

- CORS headers are automatically added via `json_response()`
- AI features degrade gracefully when API keys are not configured
- Multi-agent orchestration requires Cosmos DB for state persistence
- Voice features require Azure OpenAI Realtime deployment
