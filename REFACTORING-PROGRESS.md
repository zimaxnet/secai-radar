# SecAI Radar Cloud Refactoring Progress

**Last Updated:** 2026-01-23  
**Reference Document:** `secairadar-cloud-master-services-kickoff-v1.md`  
**Repository:** https://github.com/zimaxnet/secai-radar  
**Azure Resource:** `secai-radar` (Static Web App) in `secai-radar-rg`

## Current Azure Configuration ✅

- **Subscription ID:** `23f4e2c5-0667-4514-8e2e-f02ca7880c95`
- **Resource Group:** `secai-radar-rg`
- **Static Web App:** `secai-radar`
- **Default Hostname:** `purple-moss-0942f9e10.3.azurestaticapps.net`
- **Custom Domain:** `secairadar.cloud` (Status: Ready)
- **Location:** Central US
- **SKU:** Free tier

## Target Architecture (from Master Services Doc)

### Domains
- **Public Trust Hub:** `secairadar.cloud` ✅ (configured)
- **Private Trust Registry:** `app.secairadar.cloud` (to be configured)
- **Corporate:** `zimax.net` (links only)

### Services (from Master Services Doc)

| Service | Type | Domain | Status | Notes |
|---------|------|--------|--------|-------|
| `public-web` | Web app | secairadar.cloud | ✅ | Current Static Web App |
| `public-api` | API | secairadar.cloud | 🔄 | Needs refactoring |
| `private-web` | Web app | app.secairadar.cloud | ⏳ | To be created |
| `private-api` | API | secairadar.cloud | ⏳ | To be created |
| `workers-scout` | Worker | internal | ⏳ | To be created |
| `workers-curator` | Worker | internal | ⏳ | To be created |
| `workers-evidence` | Worker | internal | ⏳ | To be created |
| `workers-scorer` | Worker | internal | ⏳ | To be created |
| `workers-drift` | Worker | internal | ⏳ | To be created |
| `workers-brief` | Worker | internal | ⏳ | To be created |
| `publisher` | Job | internal | ⏳ | To be created |
| `graph-builder` | Worker | internal | ⏳ | To be created |

**Legend:**
- ✅ Configured/Working
- 🔄 In Progress/Needs Refactoring
- ⏳ Not Started

## 7-Step Refactoring Process

### Step 1: Information Architecture + Wireframe Specs ✅
**Status:** Completed (Initial Implementation)  
**Document:** `secairadar-mcp-dashboard-ia-wireframes-v0.1.md`

**Deliverables:**
- ✅ URL map (public + private) - Defined in wireframe spec
- ✅ Navigation model - Defined in wireframe spec
- 🔄 Page-by-page wireframe specs (components + interactions) - In progress
- ⏳ Data contracts (what each page needs from the API) - To be implemented
- ⏳ MVP vs v1 feature gates - Defined in wireframe spec

**Public Routes to Implement:**
- `/mcp` - Overview Dashboard
- `/mcp/rankings` - Rankings Dashboard
- `/mcp/servers/{serverSlug}` - Server Detail
- `/mcp/providers/{providerSlug}` - Provider Portfolio
- `/mcp/daily/{YYYY-MM-DD}` - Daily Trust Brief
- `/mcp/methodology` - Scoring methodology
- `/mcp/changelog` - Rubric changes
- `/mcp/feed.xml` - RSS/Atom feed
- `/mcp/feed.json` - JSON Feed

**Private Routes (Future):**
- `app.secairadar.cloud/registry` - Org inventory
- `app.secairadar.cloud/registry/servers/{id}` - Internal server detail
- `app.secairadar.cloud/registry/policies` - Allow/deny rules
- `app.secairadar.cloud/registry/evidence` - Evidence packs
- `app.secairadar.cloud/registry/exports` - Audit packs
- `app.secairadar.cloud/registry/agents` - Automation runs

### Step 2: Content Objects + Feed Specs + Daily Story Templates ✅
**Status:** Completed (Frontend Implementation)  
**Document:** `secairadar-verified-mcp-step2-content-feeds-templates-v0.1.md`

**Deliverables:**
- ✅ TypeScript types/interfaces for all content objects (Server Record, Daily Brief, Mover, Downgrade, Drift, Scorecard, New Entrant)
- ✅ Daily Brief page implementation with full content structure
- ✅ Feed generation utilities (RSS/Atom and JSON Feed)
- ✅ Social media template generators (X/Twitter, LinkedIn, Reddit, HN)
- ✅ Calculation rules for movers, downgrades, new entrants, drift
- ✅ MCP API client functions
- ⏳ RSS/Atom feed endpoint (`/mcp/feed.xml`) - Requires backend API
- ⏳ JSON Feed endpoint (`/mcp/feed.json`) - Requires backend API

**Content Objects Defined:**
- MCP Server Record (public view)
- Daily Trust Brief
- Mover Object
- Downgrade Object
- Drift Event Object
- New Entrant Object
- Scorecard Update Object

**Social Templates:**
- X (Twitter) thread generator (5-7 posts)
- LinkedIn post generator
- Reddit post generator (weekly format)
- Hacker News / Lobsters post generator (major events only)

### Step 3: Automation Blueprint (Agents • Pipeline • Guardrails) ✅
**Status:** Completed (Documentation + Utilities)  
**Document:** `secairadar-verified-mcp-step3-automation-blueprint-v0.1.md`

**Deliverables:**
- ✅ Complete daily pipeline runbook documentation
- ✅ Agent architecture definitions (Scout, Curator, Evidence Miner, Scorer, Drift Sentinel, Publisher, Sage Meridian)
- ✅ TypeScript types for all agent roles and pipeline stages
- ✅ Canonical ID generation utilities
- ✅ Dedupe heuristics utilities (providers, servers, endpoints)
- ✅ Source connector plan documentation
- ✅ Guardrails and safety rules documentation
- ⏳ Backend implementation of agents (requires backend development)

**Agent Roles Defined:**
- **Scout** - Discovery ingestor (finds MCP servers from multiple sources)
- **Curator** - Normalizer + canonicalizer (resolves duplicates, creates stable IDs)
- **Evidence Miner** - Docs/repo extractor (extracts structured posture signals)
- **Scorer** - Trust Score v1 evaluator (computes scores + evidence confidence)
- **Drift Sentinel** - Diff + change classifier (detects meaningful changes)
- **Publisher** - Dashboards + feeds + API (atomic publishing)
- **Sage Meridian** - Storyteller + visual director (generates narratives and visuals)

**Pipeline Schedule:**
- 02:30 Scout → 03:00 Curator → 03:20 Evidence Miner → 04:00 Scorer → 04:20 Drift Sentinel → 04:40 Publisher → 05:00 Sage Meridian → 05:20 Outbox

**Key Utilities Created:**
- `canonicalIds.ts` - Provider/server ID generation, name normalization, URL normalization
- `dedupe.ts` - Dedupe heuristics with confidence scoring and review queue support

### Step 4: Data Model + API Spec ✅
**Status:** Completed (Type Definitions + API Clients)  
**Document:** `secairadar-verified-mcp-step4-data-model-api-spec-v0.1.md`

**Deliverables:**
- ✅ Canonical data model types (Provider, MCPServer, EvidenceItem, ScoreSnapshot, DriftEvent, DailyBrief)
- ✅ Extracted claims schema types (15 claim types)
- ✅ Explainability payload types
- ✅ GK Graph schema types (nodes and edges, openContextGraph-aligned)
- ✅ Public API client with all 9 endpoints
- ✅ Private API client with Trust Registry endpoints (inventory, policies, evidence, exports, agents, outbox)
- ✅ API response envelope types with methodology versioning
- ⏳ JSON schema definitions (can be added as needed for validation)

**Public API Endpoints Implemented:**
- `/api/v1/public/mcp/summary` - Overview dashboard KPIs
- `/api/v1/public/mcp/recently-updated` - Recently updated servers
- `/api/v1/public/mcp/rankings` - Rankings with filters and sorting
- `/api/v1/public/mcp/servers/{id}` - Server detail
- `/api/v1/public/mcp/servers/{id}/evidence` - Server evidence
- `/api/v1/public/mcp/servers/{id}/drift` - Server drift timeline
- `/api/v1/public/mcp/servers/{id}/graph` - Server graph (GK)
- `/api/v1/public/mcp/providers/{id}` - Provider portfolio
- `/api/v1/public/mcp/providers/{id}/servers` - Provider servers
- `/api/v1/public/mcp/daily/{date}` - Daily brief

**Private API Endpoints Implemented:**
- Registry inventory (GET/POST/PATCH servers)
- Policies + approvals (GET/POST policies, approve/deny)
- Evidence packs (upload, list, validate)
- Exports (create audit pack, get export status)
- Automation runs (get runs, trigger run, configure schedules)
- Outbox (get items, create item, mark sent)

**GK Graph Schema:**
- 14 node types (Provider, MCPServer, Endpoint, Tool, PermissionScope, DataDomain, Hosting, EvidenceArtifact, ScoreSnapshot, DriftEvent, Policy, Approval, RunEvent, DailyBrief)
- 13 edge types (OWNS, HAS_ENDPOINT, EXPOSES, REQUIRES, TOUCHES, HOSTED_BY, SUPPORTS, HAS_SCORE, HAS_DRIFT, GOVERNS, APPROVES, INVOKED, MENTIONS)

### Step 5: Reference Implementation Plan ✅
**Status:** Completed (Documentation + Infrastructure Planning)  
**Document:** `secairadar-verified-mcp-step5-reference-implementation-plan-v0.1.md`

**Deliverables:**
- ✅ Implementation plan documentation (Azure architecture, build order, security)
- ✅ Database schema definitions (PostgreSQL tables for public core, projections, private registry)
- ✅ Bicep infrastructure templates (Container Apps, PostgreSQL, Storage, Key Vault)
- ✅ Build order documentation (week-by-week phases: Phase 0-4 + v1)
- ✅ Security model documentation (RBAC, multi-tenant isolation, audit logging)
- ✅ Publishing model documentation (staging swap, anti-partial updates)

**Azure Architecture Defined:**
- **Compute**: Azure Container Apps (public-api, registry-api, pipeline-workers, storyteller)
- **Data Stores**: PostgreSQL (Flexible Server), Graph store (MVP: JSON in Postgres, v1: Cosmos DB/Neo4j), Azure Storage (evidence, assets, exports)
- **Search**: MVP: Postgres full-text, v1: Azure AI Search
- **Messaging**: MVP: Scheduled jobs, v1: Azure Service Bus
- **Identity**: Managed Identities, Azure Key Vault, Entra ID OIDC
- **Edge**: Azure Front Door (WAF, caching, routing)

**Database Schema:**
- 20+ tables defined (providers, mcp_servers, evidence_items, score_snapshots, drift_events, daily_briefs, workspaces, policies, approvals, etc.)
- Materialized views for performance (latest_assessments_view)
- Indexes optimized for common queries
- Append-only tables for auditability (score_snapshots, drift_events)

**Build Order (4 Weeks MVP):**
- Phase 0 (Day 1-2): Repo + CI skeleton
- Phase 1 (Week 1): Public MVP "Truth Hub" (API + UI + Feeds)
- Phase 2 (Week 2): Automation Pipeline MVP (Scout → Curator → Evidence Miner → Scorer → Drift → Brief)
- Phase 3 (Week 3): Private Trust Registry MVP (Auth + RBAC + Workspaces + Policies)
- Phase 4 (Week 4): GK "Look Behind the Veil" MVP (Graph explorer)
- v1 (Weeks 5-8): Production hardening + flair

### Step 6: MVP PRD + UI Component Spec + Copy System + Analytics Plan ✅
**Status:** Completed (Product Documentation + UI Components)  
**Document:** `secairadar-verified-mcp-step6-mvp-prd-ui-copy-analytics-v0.1.md`

**Deliverables:**
- ✅ MVP PRD document (problem statement, personas, goals, non-goals, success metrics)
- ✅ UI component specifications (pages, states, components, interactions)
- ✅ Copy system implementation (labels, disclaimers, badges, flag definitions, CTAs)
- ✅ Analytics plan and event tracking utilities (events, funnels, tracking functions)
- ✅ Launch checklist (pre-launch, launch day, post-launch)
- ✅ Enhanced Methodology page with full content
- ✅ Enhanced Submit Evidence page with form

**MVP Goals Defined:**
- Public trust hub at secairadar.cloud/mcp
- Rankings + server detail with Trust Score, Evidence Confidence, drift timeline, explainability
- Daily Trust Brief page + RSS/JSON feeds
- Outbox drafts for daily social posts

**Success Metrics:**
- Freshness: Daily run success rate ≥ 95%
- Engagement: CTR overview → server detail ≥ 25%
- Trust: Evidence tab open rate ≥ 30%
- Growth: Tracked servers increases week-over-week
- Conversion: Evidence submissions, enterprise inquiries

**Copy System Components:**
- TierBadge component (A/B/C/D with descriptions)
- EvidenceConfidenceBadge component (0-3 with tooltips)
- FlagTooltip component (flag definitions)
- Disclaimer component (short/long/methodology variants)
- Copy utilities (labels, CTAs, flag definitions)

**Analytics Events:**
- 20+ event types defined (page_view, search_used, filter_applied, server_clicked, tab_opened, etc.)
- 4 funnels defined (Discovery → Transparency, Daily Brief → Deep Dive, Provider Engagement, Commercial Conversion)
- Tracking utilities for all events
- Support for multiple analytics providers (GA4, Plausible, custom)

### Step 7: MVP Build Tickets (Backlog) ✅
**Status:** Completed (Backlog Created)  
**Document:** `secairadar-verified-mcp-step7-mvp-build-tickets-backlog-v0.1.md`

**Deliverables:**
- ✅ Structured backlog document with 60+ actionable tickets
- ✅ Tickets organized by phase (Phase 0-4 + Post-MVP)
- ✅ Tickets categorized by type (FE, BE, DATA, PIPE, SEC, DEVOPS, UX)
- ✅ Acceptance criteria for each ticket
- ✅ Dependencies mapped between tickets
- ✅ Priority levels assigned (P0, P1, P2)
- ✅ Ticket template for future tickets
- ✅ Backlog management documentation

**Ticket Breakdown:**
- **Phase 0** (Day 1-2): 4 tickets - Repo + CI Skeleton
- **Phase 1** (Week 1): 22 tickets - Public MVP "Truth Hub"
- **Phase 2** (Week 2): 12 tickets - Automation Pipeline MVP
- **Phase 3** (Week 3): 14 tickets - Private Trust Registry MVP
- **Phase 4** (Week 4): 8 tickets - GK Explorer MVP + Hardening
- **Post-MVP**: 6 tickets - Optional nice-to-have features

**Status Summary:**
- ✅ Completed: 8 tickets (mostly frontend work from Steps 1-6)
- 🔄 In Progress / Partial: 4 tickets (needs API integration)
- ⏳ Pending: 48+ tickets (ready for implementation)

**Key Completed Tickets:**
- T-004: Copy system package
- T-040: Public web shell + routing
- T-041: Overview dashboard modules
- T-042: Rankings dashboard
- T-043: Server detail Overview tab
- T-046: Daily brief page
- T-047: Methodology page
- T-048: Submit evidence page
- T-060: Shared types + JSON schemas

**Critical Path (P0 Tickets):**
- Phase 0: Monorepo, CI/CD setup
- Phase 1: Database schema, Public API endpoints, Feeds
- Phase 2: Scoring library, Pipeline workers (Scout → Curator → Evidence Miner → Scorer → Drift → Brief → Publisher)
- Phase 3: Auth + RBAC, Registry endpoints and UI
- Phase 4: Graph builder, Graph endpoint, Graph UI

**MVP Acceptance Criteria:**
- Public hub has Overview, Rankings, Server Detail (Overview/Evidence/Drift/Graph), Daily Brief, Methodology, Feeds
- Daily pipeline produces scores, drift, daily brief, and publishes with atomic swap
- Private registry supports: auth, workspace, inventory, policies, evidence pack upload, JSON export
- Every public score has visible explainability, evidence confidence, and last assessed timestamp

## Key Decisions & Notes

- Using Azure Static Web Apps for `public-web` (already configured)
- Target domains align with master services document
- Infrastructure as Code (Bicep) exists in `infra/` directory
- Current deployment uses `secai-radar.zimax.net` but target is `secairadar.cloud` (already configured)

## GitHub Project Setup ✅

**Status:** Complete (2026-01-23)

**Accomplishments:**
- ✅ GitHub Project created (Project #3: "Verified MCP MVP Implementation")
- ✅ 6 Milestones created (Phase 0-4 + MVP Launch)
- ✅ All labels created (categories, priorities, phases, status)
- ✅ 30+ GitHub issues created from backlog tickets
- ✅ Completed tickets properly closed (T-004, T-040-T-048, T-060)
- ✅ All issues added to project board

**Project URL:** https://github.com/orgs/zimaxnet/projects/3

**Documentation:**
- `docs/GITHUB-SETUP-COMPLETE.md` - Complete setup status
- `docs/GITHUB-SETUP-FINAL.md` - Final status summary
- `docs/GITHUB-SETUP-ACCOMPLISHMENTS.md` - Detailed accomplishments
- `docs/GITHUB-PROJECT-SETUP.md` - Setup instructions

## Implementation Status ✅

**Status:** All phases (0-4) implementation complete (2026-01-23)

**Accomplishments:**
- ✅ Phase 0: Monorepo structure, CI/CD pipelines, infrastructure templates
- ✅ Phase 1: Database models, Public API (10 endpoints), Frontend integration, Publishing mechanism
- ✅ Phase 2: Scoring library, 7 workers (Scout, Curator, Evidence Miner, Scorer, Drift Sentinel, Sage Meridian, Publisher), Pipeline orchestration
- ✅ Phase 3: Authentication, RBAC, Registry API, Workspace management
- ✅ Phase 4: Graph builder, Graph API, Security middleware

**Files Created:** 167 files across monorepo structure

**See:** `IMPLEMENTATION-COMPLETE.md` for full details

## Next Actions

1. ✅ **GitHub Project Setup** - Complete
2. ✅ **Issue Templates Updated** - Complete
3. ✅ **All Implementation Phases** - Complete
4. ✅ **Database Created** - `secairadar` database on `ctxeco-db` (2026-01-23)
5. **Update Azure Static Web App Configuration** - Change app_location from `web/` to `apps/public-web/`
6. **Run Database Migrations** - Execute migration scripts to create schema
7. **Deploy Infrastructure** - Run Bicep templates (without PostgreSQL, using existing)
8. **Deploy Public API** - Build and deploy Container App
9. **Test End-to-End** - Verify all components work together
10. Update this document as deployment progresses

## Database Configuration ✅

**Using Existing PostgreSQL Server:**
- **Resource Group:** `ctxeco-rg`
- **Server:** `ctxeco-db`
- **Database:** `secairadar` (created)
- **FQDN:** `ctxeco-db.postgres.database.azure.com`
- **Admin User:** `ctxecoadmin`
- **Firewall:** Azure services allowed

**Next:** Run migrations after setting DATABASE_URL environment variable.

See `DATABASE-READY.md` for connection details and next steps.

## Getting Started

**When you return to start implementation:**

👉 **See `GETTING-STARTED.md` for a complete guide on where to begin!**

**Quick Start:**
1. Start with **T-001: Monorepo scaffolding** (4 hours)
2. Then **T-002: CI/CD pipeline** (6 hours)
3. Then **T-003: Infrastructure deployment** (8 hours)
4. Then proceed to **Phase 1: Database and API implementation**

All planning is complete. Ready to begin implementation!

---

**Azure Portal Link:**
https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
