# CLAUDE.md — SecAI Radar

This document provides context for AI assistants working in this repository.

## Project Overview

SecAI Radar is an MCP (Model Context Protocol) server trust-ranking platform. It discovers MCP servers, extracts security evidence, calculates trust scores, detects changes over time, and publishes daily briefings. The platform serves both a public API ("Truth Hub") and a private enterprise registry.

**Core domain**: Security assessment and trust scoring of MCP servers using evidence-based methodology.

## Repository Structure

This is a **monorepo** managed with npm workspaces (`apps/*`, `packages/*`). It contains both TypeScript (frontend) and Python (backend APIs + workers) code.

```
secai-radar/
├── apps/
│   ├── public-api/        # FastAPI — public read-only API (Python)
│   ├── public-web/        # Vite + React — frontend SPA (TypeScript)
│   ├── registry-api/      # FastAPI — private enterprise registry (Python)
│   └── workers/           # 8 pipeline workers (Python, each standalone)
│       ├── scout/             # Discovery ingestor
│       ├── curator/           # Canonicalization & dedup
│       ├── evidence-miner/    # Evidence extraction from docs/repos
│       ├── scorer/            # Trust Score v1 calculation
│       ├── drift-sentinel/    # Change detection
│       ├── sage-meridian/     # Daily brief generator
│       ├── graph-builder/     # Graph snapshot builder
│       └── publisher/         # Atomic staging→production swap
├── packages/
│   └── scoring/           # Reusable Trust Score v1 library (Python)
├── src/                   # Legacy orchestrator & AI agent personas
├── backend/               # Legacy backend (main.py)
├── config/                # YAML configs (models, agents, guardrails, RAG)
├── docs/                  # All documentation (50+ files)
├── infra/                 # Azure Bicep IaC templates
├── scripts/               # 60+ deployment & utility scripts
├── seeds/                 # Seed data (domains, controls, tools)
├── .github/workflows/     # CI/CD pipelines
└── package.json           # Monorepo root (npm workspaces)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TypeScript 5.9, MSAL (Azure AD) |
| Public API | FastAPI, SQLAlchemy 2.0, Pydantic 2, Psycopg2 |
| Registry API | FastAPI, SQLAlchemy 2.0, Entra ID OIDC, RBAC |
| Workers | Python 3.11, Psycopg2 (direct SQL), standalone packages |
| Scoring Library | Python 3.11, Pydantic 2 |
| Database | PostgreSQL (Azure Database for PostgreSQL Flexible Server) |
| Infrastructure | Azure (Static Web Apps, App Service, Key Vault, Storage) |
| IaC | Azure Bicep |
| CI/CD | GitHub Actions |

## Language & Runtime Requirements

- **Python**: >=3.11 (all backend services and workers)
- **Node.js**: >=20.19.0, npm >=10.0.0 (frontend, monorepo tooling)
- **TypeScript**: 5.9.x

## Key Commands

### Frontend (apps/public-web)
```bash
npm ci                          # Install all workspace dependencies
npm run dev:public-web          # Start Vite dev server
npm run build:public-web        # Production build → apps/public-web/dist/
npm run lint --workspaces       # Lint all workspaces
npm run typecheck --workspaces  # Type-check all workspaces
npm run test --workspaces       # Run all workspace tests
```

### Python APIs
```bash
# Public API
cd apps/public-api
pip install -e .[dev]
uvicorn src.main:app --reload

# Registry API
cd apps/registry-api
pip install -e .[dev]
uvicorn src.main:app --reload
```

### Scoring Library
```bash
cd packages/scoring
pip install -e .[dev]
pytest tests/ -v
```

### Workers (each is standalone)
```bash
cd apps/workers/<worker-name>
pip install -e .
python src/<worker_module>.py
```

### Linting
```bash
# Python — Ruff
ruff check apps/public-api/ apps/registry-api/ packages/scoring/
ruff check apps/workers/*/

# TypeScript — via workspace scripts
npm run lint --workspaces --if-present
```

## Architecture

### Daily Pipeline (02:30 UTC)

The automated pipeline runs as a sequential GitHub Actions workflow (`daily-pipeline.yml`). Each stage depends on the previous:

```
record-start → scout → curator → evidence-miner → scorer → drift-sentinel → sage-meridian → publisher
```

1. **Scout**: Fetches MCP servers from tier-1 sources → `raw_observations` table
2. **Curator**: Normalizes, deduplicates → `mcp_servers` table
3. **Evidence Miner**: Crawls docs/repos, extracts claims → `evidence_items` + `evidence_claims`
4. **Scorer**: Calculates trust scores (D1–D6 domains) → `score_snapshots` (staging via `WRITE_TO_STAGING=1`)
5. **Drift Sentinel**: Detects score/evidence changes → `drift_events`
6. **Sage Meridian**: Generates daily narrative briefing → `daily_briefs`
7. **Publisher**: Validates integrity and swaps staging→production via `latest_scores` pointer flip

### Staging/Production Swap Pattern

During the pipeline, the scorer writes to `latest_scores_staging`. The publisher validates data integrity and atomically swaps the pointer in `latest_scores` for zero-downtime updates.

### Trust Score v1

Defined in `packages/scoring/`. Scores MCP servers across 6 security domains (D1–D6), each scored 0–5, producing a final 0–100 trust score with:
- **Tiers**: A (80–100), B (60–79), C (40–59), D (0–39)
- **Enterprise Fit**: Regulated, Standard, Experimental
- **Flags**: Fail-fast flags (e.g., missing auth) and risk flags with severity
- **Evidence Confidence**: 0–3 scale (None → ValidatedPack)
- **Explainability**: JSON payload explaining score derivation

### API Design

Both APIs follow a consistent response envelope:
```json
{
  "attestation": { "methodologyVersion", "asOf", "assessmentRunId" },
  "methodologyVersion": "v1.0",
  "generatedAt": "<ISO timestamp>",
  "data": { ... },
  "meta": { ... }
}
```

**Public API** (`/api/v1/public/`): Read-only, public access. Rankings, server details, evidence, drift, daily briefs, RSS/JSON feeds.

**Registry API** (`/api/v1/private/registry/`): Multi-tenant, Entra ID OIDC auth, 5 RBAC roles (REGISTRY_ADMIN, POLICY_APPROVER, EVIDENCE_VALIDATOR, VIEWER, AUTOMATION_OPERATOR). Workspace-scoped data.

### Database

PostgreSQL with 15+ tables. Key patterns:
- **Append-only tables**: `raw_observations`, `score_snapshots`, `drift_events` — never updated, only inserted
- **Pointer tables**: `latest_scores` / `latest_scores_staging` — reference current score snapshots
- **JSONB columns**: `flags_json`, `explainability_json`, `metadata_json`, `diff_json`, `value_json` for flexible structured data
- **Migrations**: Sequential numbered files in `apps/public-api/migrations/` (001–009)

### Authentication & Security

- **Public API**: Unauthenticated (read-only public data)
- **Registry API**: Entra ID OIDC tokens, workspace isolation, RBAC enforcement
- **Frontend**: MSAL.js for Azure AD login
- **Middleware**: Rate limiting, ETag caching, sensitive data redaction

## Code Conventions

### Python
- **Formatter/Linter**: Ruff with `line-length = 100`, `target-version = "py311"`
- **Type checking**: mypy with `warn_return_any = true`
- **Framework**: FastAPI with Pydantic v2 models
- **DB access**: SQLAlchemy 2.0 in APIs; raw psycopg2 in workers (for simplicity)
- **Imports**: Standard library → third-party → local, consistent with Ruff defaults
- **Testing**: pytest (testpaths = `tests/`, files = `test_*.py`)

### TypeScript/React
- **Build**: Vite
- **Language**: TypeScript 5.9 strict
- **Package manager**: npm with workspaces
- **Components**: Functional React components
- **API client**: Centralized in `apps/public-web/src/api.ts` and `src/api/` modules
- **Types**: Defined in `apps/public-web/src/types/`

### General
- **Config**: YAML files in `config/` for model roles, agent personas, guardrails, RAG
- **Env vars**: `.env` (never committed), template in `.env.example`; primary var is `DATABASE_URL`
- **Secrets**: Azure Key Vault in production; `DATABASE_URL` GitHub secret for CI

## Branch & Documentation Conventions

### Branches
- **`main`**: Application development and Azure deployment
- **`wiki`**: GitHub Pages user-facing wiki (`docs/wiki/`)
- Application development always happens on `main`

### Documentation
- **All docs go in `docs/`** — no scattered markdown files in source directories
- **ADRs**: `docs/adr/` with numbered format (`0001-*.md`)
- **Decision log**: `docs/decision-log.md`
- Module-level READMEs (if needed) should be minimal and link to `docs/`
- Developer docs → `main` branch `docs/`
- User/wiki docs → `wiki` branch `docs/wiki/`

## CI/CD

### CI (`ci.yml`) — on push/PR to `main`
1. **lint-and-typecheck**: Node.js lint + TypeScript type checking
2. **lint-python**: Ruff on all Python code
3. **test**: npm workspace tests + pytest on `packages/scoring/tests/`
4. **build**: Builds `public-web` → uploads artifact

### Daily Pipeline (`daily-pipeline.yml`) — 02:30 UTC or manual
Sequential 8-stage pipeline (see Architecture section above). Uses `WRITE_TO_STAGING=1` during scoring, atomic swap at publish.

### Deployment
- **Frontend**: Azure Static Web Apps (`azure-static-web-apps.yml`)
- **API**: Azure App Service (`azure-functions-deploy.yml`)
- **Infrastructure**: Bicep templates (`deploy-infrastructure.yml`)
- **Staging**: Separate staging deployment (`deploy-staging.yml`)

## Environment Setup

1. Copy `.env.example` to `.env` and fill in `DATABASE_URL`
2. `npm ci` at repo root (installs all workspace deps)
3. For Python: `pip install -e .[dev]` in the relevant `apps/` or `packages/` directory
4. See `docs/CREDENTIALS-SETUP.md` for Azure credential configuration

## Key Files to Understand

| File | Purpose |
|------|---------|
| `apps/public-api/src/main.py` | Public API entry point |
| `apps/public-api/src/routers/public.py` | All public API endpoints |
| `apps/public-api/src/models/` | SQLAlchemy models (server, evidence, score, drift, brief) |
| `apps/registry-api/src/routers/registry.py` | Private registry endpoints |
| `apps/registry-api/src/middleware/auth.py` | Entra ID authentication |
| `apps/registry-api/src/middleware/rbac.py` | Role-based access control |
| `packages/scoring/src/scoring/calculator.py` | Trust Score v1 algorithm |
| `packages/scoring/src/scoring/models.py` | Scoring domain models (Tier, Flag, DomainScore, etc.) |
| `apps/public-web/src/api.ts` | Frontend API client |
| `apps/public-web/src/App.tsx` | React root component |
| `config/models.yaml` | LLM role assignments |
| `config/agent_personas.yaml` | AI agent persona definitions |
| `.github/workflows/daily-pipeline.yml` | Daily automated pipeline |
| `.github/workflows/ci.yml` | CI checks |
| `docs/implementation/database-schema.sql` | Full database schema |

## Common Tasks

### Adding a new public API endpoint
1. Define route in `apps/public-api/src/routers/public.py`
2. Add service logic in `apps/public-api/src/services/`
3. Add/update SQLAlchemy models in `apps/public-api/src/models/` if needed
4. Follow the response envelope pattern with `attestation`, `methodologyVersion`, `generatedAt`

### Adding a new worker
1. Create directory under `apps/workers/<name>/`
2. Add `pyproject.toml` with `psycopg2-binary` dependency
3. Create `src/<name>.py` with main logic using direct psycopg2 queries
4. Add job to `.github/workflows/daily-pipeline.yml` in the correct position
5. Add run script in `scripts/run-<name>.sh`

### Modifying the scoring algorithm
1. Edit `packages/scoring/src/scoring/calculator.py`
2. Update models in `packages/scoring/src/scoring/models.py` if domain structure changes
3. Run tests: `pytest packages/scoring/tests/ -v`
4. Bump `methodology_version` if the scoring contract changes

### Adding a database migration
1. Create next numbered file in `apps/public-api/migrations/` (e.g., `010_description.sql`)
2. Update `docs/implementation/database-schema.sql` to reflect the change
3. Run migration against the database

### Working with the frontend
1. Types go in `apps/public-web/src/types/`
2. API calls go in `apps/public-web/src/api/` or `apps/public-web/src/api.ts`
3. MCP-specific components live in `apps/public-web/src/components/mcp/`
4. Shared UI components live in `apps/public-web/src/components/ui/`
