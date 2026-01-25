# Verified MCP Implementation Plan and Preparation Summary

**Date:** 2026-01-23  
**Repository:** https://github.com/zimaxnet/secai-radar  
**Status:** Planning Complete, Ready for Implementation

## Executive Summary

This document summarizes all preparation work completed through the 7-step refactoring process and provides the complete implementation plan to bring the Verified MCP Trust Hub to production MVP. The project has completed all architectural planning, frontend UI development (with mock data), type definitions, documentation, and backlog creation. Implementation can now begin following the 4-phase plan outlined below.

---

## Part 1: Preparation Work Completed (7 Steps)

### Overview of 7-Step Refactoring Process

All 7 planning steps have been completed, establishing a solid foundation for implementation:

1. ✅ **Information Architecture + Wireframe Specs** - Routes, navigation, page structure
2. ✅ **Content Objects + Feed Specs + Daily Story Templates** - Data models, feed generation, social templates
3. ✅ **Automation Blueprint** - Pipeline architecture, agent roles, guardrails
4. ✅ **Data Model + API Spec** - Canonical data models, API contracts, graph schema
5. ✅ **Reference Implementation Plan** - Azure architecture, database schema, security model
6. ✅ **MVP PRD + UI Component Spec + Copy System + Analytics** - Product requirements, UI specs, copy system
7. ✅ **MVP Build Tickets (Backlog)** - 60+ actionable tickets organized by phase

### Step 1: Information Architecture + Wireframe Specs ✅

**Status:** Completed (Initial Implementation)

**What Was Done:**
- Defined complete URL map for public (`/mcp/*`) and private (`app.secairadar.cloud/registry/*`) routes
- Established navigation model with global header and footer
- Created page-by-page wireframe specifications
- Implemented route structure in React Router
- Built core pages with mock data:
  - `/mcp` - Overview Dashboard
  - `/mcp/rankings` - Rankings Dashboard
  - `/mcp/servers/{slug}` - Server Detail Page
  - `/mcp/daily/{date}` - Daily Brief Page
  - `/mcp/methodology` - Methodology Page
  - `/mcp/submit` - Submit Evidence Page

**Key Files Created:**
- `web/src/routes/mcp/MCPLayout.tsx` - Layout component
- `web/src/routes/mcp/Overview.tsx` - Overview dashboard
- `web/src/routes/mcp/Rankings.tsx` - Rankings page
- `web/src/routes/mcp/ServerDetail.tsx` - Server detail page
- `web/src/routes/mcp/DailyBrief.tsx` - Daily brief page
- `web/src/routes/mcp/Methodology.tsx` - Methodology page
- `web/src/routes/mcp/Submit.tsx` - Submit evidence page

**Reference:** `secairadar-mcp-dashboard-ia-wireframes-v0.1.md`

---

### Step 2: Content Objects + Feed Specs + Daily Story Templates ✅

**Status:** Completed (Frontend Implementation)

**What Was Done:**
- Defined TypeScript interfaces for all content objects:
  - `MCPServerRecord` - Public server view
  - `DailyTrustBrief` - Daily brief structure
  - `MoverObject`, `DowngradeObject`, `DriftEventObject`, `NewEntrantObject` - Content objects
- Implemented Daily Brief page with full content structure (narrative, highlights, movers, downgrades, etc.)
- Created feed generation utilities:
  - RSS/Atom feed generator (`generateRSSFeed()`)
  - JSON Feed generator (`generateJSONFeed()`)
- Created social media template generators:
  - X (Twitter) thread generator (5-7 posts)
  - LinkedIn post generator
  - Reddit post generator (weekly format)
  - Hacker News / Lobsters post generator
- Implemented calculation rules for:
  - Top movers (largest score increases)
  - Top downgrades (largest score decreases)
  - New entrants identification
  - Daily tiers snapshot

**Key Files Created:**
- `web/src/types/mcp.ts` - Content object types
- `web/src/utils/feeds.ts` - Feed generation utilities
- `web/src/utils/socialTemplates.ts` - Social media template generators
- `web/src/utils/calculations.ts` - Business logic calculations
- `web/src/api/mcp.ts` - MCP API client (initial)

**Reference:** `secairadar-verified-mcp-step2-content-feeds-templates-v0.1.md`

---

### Step 3: Automation Blueprint (Agents • Pipeline • Guardrails) ✅

**Status:** Completed (Documentation + Utilities)

**What Was Done:**
- Documented complete daily pipeline runbook with agent roles and responsibilities
- Defined 7 agent roles:
  - **Scout** - Discovery ingestor (finds MCP servers from multiple sources)
  - **Curator** - Normalizer + canonicalizer (resolves duplicates, creates stable IDs)
  - **Evidence Miner** - Docs/repo extractor (extracts structured posture signals)
  - **Scorer** - Trust Score v1 evaluator (computes scores + evidence confidence)
  - **Drift Sentinel** - Diff + change classifier (detects meaningful changes)
  - **Publisher** - Dashboards + feeds + API (atomic publishing)
  - **Sage Meridian** - Storyteller + visual director (generates narratives and visuals)
- Created TypeScript types for all agent roles and pipeline stages
- Implemented canonical ID generation utilities:
  - `generateProviderId()` - Creates stable provider IDs
  - `generateServerId()` - Creates stable server IDs
  - Name and URL normalization functions
- Implemented deduplication heuristics:
  - Fuzzy matching for providers, servers, and endpoints
  - Confidence scoring for matches
  - Review queue support for ambiguous matches

**Key Files Created:**
- `docs/automation/automation-blueprint.md` - Complete automation blueprint
- `web/src/types/automation.ts` - Agent and pipeline types
- `web/src/utils/canonicalIds.ts` - Canonical ID generation
- `web/src/utils/dedupe.ts` - Deduplication heuristics

**Reference:** `secairadar-verified-mcp-step3-automation-blueprint-v0.1.md`

---

### Step 4: Data Model + API Spec ✅

**Status:** Completed (Type Definitions + API Clients)

**What Was Done:**
- Defined canonical data model types:
  - `Provider`, `MCPServer`, `EvidenceItem`, `ScoreSnapshot`, `DriftEvent`, `DailyBrief`
- Created extracted claims schema (15 claim types):
  - AuthModel, TokenTTL, Scopes, HostingCustody, ToolList, ToolCapabilities, AuditLogging, DataRetention, DataDeletion, Residency, Encryption, SBOM, Signing, VulnDisclosure, IRPolicy
- Defined explainability payload structure
- Created GK Graph schema:
  - 14 node types (Provider, MCPServer, Endpoint, Tool, PermissionScope, DataDomain, Hosting, EvidenceArtifact, ScoreSnapshot, DriftEvent, Policy, Approval, RunEvent, DailyBrief)
  - 13 edge types (OWNS, HAS_ENDPOINT, EXPOSES, REQUIRES, TOUCHES, HOSTED_BY, SUPPORTS, HAS_SCORE, HAS_DRIFT, GOVERNS, APPROVES, INVOKED, MENTIONS)
- Implemented public API client with all 10 endpoints:
  - `/api/v1/public/mcp/summary` - Overview KPIs
  - `/api/v1/public/mcp/recently-updated` - Recently updated servers
  - `/api/v1/public/mcp/rankings` - Rankings with filters
  - `/api/v1/public/mcp/servers/{id}` - Server detail
  - `/api/v1/public/mcp/servers/{id}/evidence` - Evidence list
  - `/api/v1/public/mcp/servers/{id}/drift` - Drift timeline
  - `/api/v1/public/mcp/servers/{id}/graph` - Graph data
  - `/api/v1/public/mcp/providers/{id}` - Provider portfolio
  - `/api/v1/public/mcp/providers/{id}/servers` - Provider servers
  - `/api/v1/public/mcp/daily/{date}` - Daily brief
- Implemented private API client for Trust Registry:
  - Inventory management (GET/POST/PATCH servers)
  - Policies + approvals (GET/POST policies, approve/deny)
  - Evidence packs (upload, list, validate)
  - Exports (create audit pack, get export status)
  - Automation runs (get runs, trigger run, configure schedules)
  - Outbox (get items, create item, mark sent)

**Key Files Created:**
- `web/src/types/dataModel.ts` - Canonical data model types
- `web/src/types/graph.ts` - GK Graph schema types
- `web/src/api/public.ts` - Public API client
- `web/src/api/private.ts` - Private API client

**Reference:** `secairadar-verified-mcp-step4-data-model-api-spec-v0.1.md`

---

### Step 5: Reference Implementation Plan ✅

**Status:** Completed (Documentation + Infrastructure Planning)

**What Was Done:**
- Documented Azure architecture recommendations:
  - Compute: Azure Container Apps (public-api, registry-api, pipeline-workers)
  - Data Stores: PostgreSQL Flexible Server, Graph store (MVP: JSON in Postgres), Azure Storage
  - Search: MVP: Postgres full-text, v1: Azure AI Search
  - Messaging: MVP: Scheduled jobs, v1: Azure Service Bus
  - Identity: Managed Identities, Azure Key Vault, Entra ID OIDC
  - Edge: Azure Front Door (WAF, caching, routing)
- Created comprehensive database schema:
  - 20+ tables defined (providers, mcp_servers, evidence_items, score_snapshots, drift_events, daily_briefs, workspaces, policies, approvals, etc.)
  - Materialized views for performance (`latest_assessments_view`)
  - Indexes optimized for common queries
  - Append-only tables for auditability
- Created Bicep infrastructure templates:
  - PostgreSQL Flexible Server
  - Storage Account with containers (evidence-private, public-assets, exports-private)
  - Key Vault
  - Container Apps Environment
  - Container Apps for public-api, registry-api, and workers
- Documented build order (week-by-week phases)
- Documented security model (RBAC, multi-tenant isolation, audit logging)
- Documented publishing model (staging swap, anti-partial updates)

**Key Files Created:**
- `docs/implementation/reference-implementation-plan.md` - Implementation plan
- `docs/implementation/database-schema.sql` - Complete database schema
- `docs/implementation/build-order.md` - Week-by-week build order
- `docs/implementation/security-model.md` - Security model documentation
- `infra/mcp-infrastructure.bicep` - Azure infrastructure template

**Reference:** `secairadar-verified-mcp-step5-reference-implementation-plan-v0.1.md`

---

### Step 6: MVP PRD + UI Component Spec + Copy System + Analytics Plan ✅

**Status:** Completed (Product Documentation + UI Components)

**What Was Done:**
- Created MVP Product Requirements Document:
  - Problem statement and target personas
  - MVP goals and non-goals
  - Success metrics (freshness, engagement, trust, growth, conversion)
  - MVP scope (in-scope vs. out-of-scope for v1+)
  - User flows
- Documented UI component specifications:
  - Header, footer, and page module specifications
  - Component interactions and states
  - Loading and error states
- Implemented copy system:
  - Centralized constants for Trust Score labels, Tier definitions (A-D), Evidence Confidence levels (0-3), Flag definitions
  - Helper functions for retrieving copy values
  - Consistent CTA text
- Created UI components utilizing copy system:
  - `TierBadge` - Displays Trust Score tier with color coding
  - `EvidenceConfidenceBadge` - Displays Evidence Confidence with tooltip
  - `FlagTooltip` - Shows flag definitions on hover/click
  - `Disclaimer` - Reusable disclaimer component
- Created analytics plan:
  - 20+ event types defined (page_view, search_used, filter_applied, server_clicked, etc.)
  - 4 funnels defined (Discovery → Transparency, Daily Brief → Deep Dive, Provider Engagement, Commercial Conversion)
  - Tracking utilities for all events
  - Support for multiple analytics providers (GA4, Plausible, custom)
- Enhanced Methodology and Submit Evidence pages with full content

**Key Files Created:**
- `docs/product/mvp-prd.md` - MVP PRD
- `docs/product/ui-component-spec.md` - UI component specifications
- `docs/product/launch-checklist.md` - Launch checklist
- `web/src/utils/copy.ts` - Copy system
- `web/src/utils/analytics.ts` - Analytics tracking utilities
- `web/src/components/mcp/TierBadge.tsx` - Tier badge component
- `web/src/components/mcp/EvidenceConfidenceBadge.tsx` - Evidence confidence badge
- `web/src/components/mcp/FlagTooltip.tsx` - Flag tooltip component
- `web/src/components/mcp/Disclaimer.tsx` - Disclaimer component

**Reference:** `secairadar-verified-mcp-step6-mvp-prd-ui-copy-analytics-v0.1.md`

---

### Step 7: MVP Build Tickets (Backlog) ✅

**Status:** Completed (Backlog Created)

**What Was Done:**
- Created structured backlog with 60+ actionable tickets
- Organized tickets by phase:
  - **Phase 0** (Day 1-2): 4 tickets - Repo + CI Skeleton
  - **Phase 1** (Week 1): 22 tickets - Public MVP "Truth Hub"
  - **Phase 2** (Week 2): 12 tickets - Automation Pipeline MVP
  - **Phase 3** (Week 3): 14 tickets - Private Trust Registry MVP
  - **Phase 4** (Week 4): 8 tickets - GK Explorer MVP + Hardening
  - **Post-MVP**: 6 tickets - Optional nice-to-have features
- Categorized tickets by type (FE, BE, DATA, PIPE, SEC, DEVOPS, UX)
- Added acceptance criteria for each ticket (checklist format)
- Mapped dependencies between tickets
- Assigned priority levels (P0 Critical, P1 High, P2 Nice-to-have)
- Created ticket template for future tickets
- Created backlog management documentation

**Key Files Created:**
- `docs/backlog/mvp-build-tickets.md` - Complete backlog (60+ tickets)
- `docs/backlog/ticket-template.md` - Ticket template
- `docs/backlog/README.md` - Backlog management guide

**Reference:** `secairadar-verified-mcp-step7-mvp-build-tickets-backlog-v0.1.md`

---

## Part 2: Implementation Plan

### Current State Assessment

**Completed:**
- ✅ All 7 planning steps (architecture, types, documentation)
- ✅ Frontend UI components and routes (using mock data)
- ✅ Type definitions and API client stubs
- ✅ Database schema design
- ✅ Infrastructure Bicep templates
- ✅ Backlog with 60+ tickets

**Remaining:**
- ⏳ Backend API implementation (10 public endpoints)
- ⏳ Database deployment and migrations
- ⏳ Automation pipeline (7 workers)
- ⏳ Private registry (auth, RBAC, workspace management)
- ⏳ Graph explorer
- ⏳ Production hardening

### Implementation Phases

The implementation is organized into 4 phases over 4 weeks, plus hardening:

#### Phase 0: Foundation (Days 1-2)

**Goal:** Set up development infrastructure and monorepo structure

**Key Tasks:**
1. **Monorepo Restructure** (T-001)
   - Create `apps/public-web/`, `apps/public-api/`, `apps/registry-api/`
   - Create `apps/workers/*` (scout, curator, evidence-miner, scorer, drift-sentinel, publisher, sage-meridian)
   - Create `packages/shared/` and `packages/scoring/`
   - Move existing `web/` content to `apps/public-web/`
   - Configure workspace (pnpm/npm workspaces)

2. **CI/CD Pipeline Setup** (T-002, T-003)
   - Create GitHub Actions workflows (build, test, deploy)
   - Set up deployment to Azure Container Apps (staging)
   - Configure secrets management (Azure Key Vault)

3. **Infrastructure Deployment** (T-003)
   - Deploy PostgreSQL Flexible Server
   - Deploy Storage Account (evidence, assets, exports containers)
   - Deploy Key Vault
   - Deploy Container Apps Environment
   - Deploy Container Registry (ACR)

**Deliverables:**
- Monorepo structure with all apps and packages
- Working CI/CD pipeline
- Azure infrastructure deployed and configured

---

#### Phase 1: Public MVP "Truth Hub" (Week 1)

**Goal:** Launch public-facing trust hub with rankings, server detail, daily brief, and feeds

**Key Tasks:**

1. **Database Setup** (T-010, T-011, T-012)
   - Run database migrations (create all tables, indexes, views)
   - Create seed data (10-20 providers, 30-50 servers, sample evidence and scores)
   - Set up connection pooling
   - Create `latest_scores` pointer table and materialized views
   - Create rankings cache table

2. **Public API Implementation** (T-020-T-031, T-050)
   - Create FastAPI application structure
   - Implement all 10 public endpoints:
     - `/api/v1/public/health` - Health check
     - `/api/v1/public/mcp/summary` - Overview KPIs
     - `/api/v1/public/mcp/recently-updated` - Recently updated servers
     - `/api/v1/public/mcp/rankings` - Rankings with filters
     - `/api/v1/public/mcp/servers/{idOrSlug}` - Server detail
     - `/api/v1/public/mcp/servers/{idOrSlug}/evidence` - Evidence list
     - `/api/v1/public/mcp/servers/{idOrSlug}/drift` - Drift timeline
     - `/api/v1/public/mcp/daily/{YYYY-MM-DD}` - Daily brief
     - `/mcp/feed.xml` - RSS feed
     - `/mcp/feed.json` - JSON Feed
   - Implement response envelope (methodologyVersion, generatedAt)
   - Add ETag and caching support
   - Add redaction middleware (remove private blob refs)

3. **Frontend API Integration** (T-040-T-048)
   - Update API client to point to real endpoints
   - Replace mock data with API calls
   - Add error handling and loading states
   - Integrate analytics tracking

4. **Staging Swap Publishing** (T-051)
   - Implement staging swap mechanism
   - Create publisher job for atomic dataset swap

**Deliverables:**
- Working database with seed data
- All 10 public API endpoints implemented
- Frontend connected to real API
- Feeds (RSS and JSON) working
- Staging swap publishing mechanism

---

#### Phase 2: Automation Pipeline (Week 2)

**Goal:** Daily automation pipeline that discovers, scores, and publishes updates

**Key Tasks:**

1. **Shared Types & Scoring Library** (T-060, T-061, T-062)
   - Port TypeScript types to Python dataclasses
   - Create Trust Score v1 calculation library
   - Implement Evidence Confidence calculator
   - Write unit tests

2. **Pipeline Workers** (T-070-T-076)
   - **Scout** (T-070): Discovery ingestor from Tier 1 sources
   - **Curator** (T-071): Canonicalization and deduplication
   - **Evidence Miner** (T-072): Doc/repo extraction
   - **Scorer** (T-073): Trust Score calculation
   - **Drift Sentinel** (T-074): Change detection
   - **Daily Brief Generator** (T-075): Narrative generation and social media drafts
   - **Publisher** (T-076): Atomic dataset swap

3. **Pipeline Orchestration** (T-080, T-081)
   - Set up daily pipeline schedule (02:30 UTC)
   - Run workers in sequence
   - Add observability (run logs, status endpoint)
   - Handle failures (retry logic, alerts)

**Deliverables:**
- Trust Score calculation library with tests
- All 7 pipeline workers implemented
- Daily pipeline orchestration working
- Observability and status tracking

---

#### Phase 3: Private Trust Registry (Week 3)

**Goal:** Enterprise workspace management with inventory, policies, and evidence packs

**Key Tasks:**

1. **Authentication & RBAC** (T-090, T-091, T-092)
   - Set up Entra ID app registration
   - Implement OIDC JWT validation middleware
   - Implement RBAC (RegistryAdmin, PolicyApprover, EvidenceValidator, Viewer, AutomationOperator)
   - Enforce workspace isolation

2. **Workspace Management** (T-091)
   - Implement workspace CRUD
   - Implement membership management

3. **Registry API Endpoints** (T-100-T-105, T-131)
   - Inventory endpoints (list, add, update servers)
   - Policy endpoints (create, list, approve/deny)
   - Evidence pack endpoints (upload, list, validate)
   - Export endpoints (create audit pack, get status)
   - Audit logging

4. **Private Web UI** (T-110-T-113)
   - Create private web app with authentication
   - Implement registry pages (inventory, policies, evidence packs, exports)

**Deliverables:**
- Entra ID authentication working
- RBAC middleware enforcing roles
- All registry API endpoints implemented
- Private web UI for registry management

---

#### Phase 4: Graph Explorer + Hardening (Week 4)

**Goal:** Graph visualization and production hardening

**Key Tasks:**

1. **Graph Snapshot Builder** (T-120)
   - Build per-server graph (Server → Tools → Scopes → DataDomains → Evidence → Flags)
   - Store graph JSON in database

2. **Graph API & UI** (T-121, T-122)
   - Implement graph API endpoint
   - Build graph explorer UI component

3. **Security Hardening** (T-130, T-132)
   - Add rate limiting
   - Add WAF rules (Azure Front Door)
   - Enable backups (DB and blobs)

4. **Observability** (T-133)
   - Set up monitoring (Application Insights)
   - Create dashboard (pipeline success rate, API latency, errors)

5. **Legal & Fairness** (T-134)
   - Create fairness page (right-to-respond process)

**Deliverables:**
- Graph explorer working
- Security hardening complete
- Monitoring and alerts set up
- Fairness page published

---

## Part 3: GitHub Project Structure

### Project Organization

The GitHub project should be organized with the following structure:

**Project Name:** "Verified MCP MVP Implementation"

**Columns:**
1. **Backlog** - All tickets not yet started
2. **Phase 0: Foundation** - Monorepo, CI/CD, Infrastructure
3. **Phase 1: Public MVP** - Database, API, Frontend Integration
4. **Phase 2: Automation** - Pipeline Workers
5. **Phase 3: Private Registry** - Auth, RBAC, Registry API/UI
6. **Phase 4: Graph + Hardening** - Graph Explorer, Security, Observability
7. **In Progress** - Currently active tickets
8. **Review** - Completed tickets awaiting review
9. **Done** - Completed and merged

### Issue Templates

Each ticket from the backlog should be created as a GitHub issue with:

- **Title:** Ticket ID and name (e.g., "T-001: Monorepo scaffolding")
- **Labels:** Category (FE, BE, DATA, PIPE, SEC, DEVOPS, UX), Priority (P0, P1, P2), Phase (Phase 0-4)
- **Body:** Full ticket description, acceptance criteria, dependencies, estimated effort
- **Milestone:** Phase milestone (Phase 0, Phase 1, etc.)
- **Assignees:** Team members (as available)

### Issue Creation Script

The following tickets should be created as GitHub issues (60+ total):

**Phase 0 (4 issues):**
- T-001: Monorepo scaffolding
- T-002: GitHub Actions: build/test pipeline
- T-003: Deploy pipeline skeleton (staging)
- T-004: Standard copy + disclaimer snippets package (✅ Completed)

**Phase 1 (22 issues):**
- T-010: Postgres schema + migrations v0
- T-011: Latest projections
- T-012: Rankings cache table
- T-020: Public API skeleton + response envelope
- T-021: GET summary endpoint
- T-022: GET rankings endpoint with filters
- T-023: GET server detail endpoint
- T-024: GET server evidence endpoint
- T-025: GET server drift endpoint
- T-026: GET daily brief endpoint
- T-027: HTTP caching (ETag + Cache-Control)
- T-030: RSS/Atom renderer
- T-031: JSON Feed renderer
- T-040: Public web shell + routing (✅ Completed)
- T-041: Overview dashboard modules (✅ Completed)
- T-042: Rankings dashboard with facet filters (✅ Completed)
- T-043: Server detail page: Overview tab (✅ Completed)
- T-044: Server detail page: Evidence tab (🔄 Partial)
- T-045: Server detail page: Drift tab (🔄 Partial)
- T-046: Daily brief page (✅ Completed)
- T-047: Methodology page (✅ Completed)
- T-048: Submit evidence page (✅ Completed)
- T-050: Redaction middleware for public responses
- T-051: Staging swap publishing pattern

**Phase 2 (12 issues):**
- T-060: Shared types + JSON schemas (✅ Completed)
- T-061: Scoring library (Trust Score v1)
- T-062: Evidence Confidence calculator
- T-070: Worker: Scout (discovery ingest)
- T-071: Worker: Curator (canonicalize + dedupe)
- T-072: Worker: Evidence Miner (basic docs/repo extraction)
- T-073: Worker: Scorer
- T-074: Worker: Drift Sentinel
- T-075: Worker: Daily Brief generator (Sage Meridian integration stub)
- T-076: Publisher job hooks
- T-080: Run logs + run status table
- T-081: Status endpoint + stale banner support

**Phase 3 (14 issues):**
- T-090: Entra OIDC auth for registry-api
- T-091: Workspace + membership tables
- T-092: RBAC middleware
- T-100: Registry: list/add servers to workspace inventory
- T-101: Registry: policies CRUD
- T-102: Registry: policy approvals
- T-103: Evidence pack upload (private blob)
- T-104: Evidence pack validation workflow
- T-105: Audit pack export v0 (JSON)
- T-110: Private shell + login redirect
- T-111: Registry inventory UI
- T-112: Policy UI (create + list)
- T-113: Evidence pack upload UI
- T-131: Audit logging (private)

**Phase 4 (8 issues):**
- T-120: Graph snapshot builder job
- T-121: Public server graph endpoint
- T-122: Graph tab UI (MVP viewer) (🔄 Partial)
- T-130: Public rate limiting + WAF rules (baseline)
- T-132: Backups + retention policy for DB + blobs
- T-133: Observability dashboard
- T-134: Fairness + right-to-respond page + contact channel

**Post-MVP (6 issues):**
- T-200: Compare tray (rankings)
- T-201: Provider portfolio endpoints + pages
- T-202: Doc hash diff + richer drift classification
- T-203: Visual cards gallery + immutable asset URLs
- T-204: Service Bus eventing for pipeline scaling
- T-205: Search via Azure AI Search (typeahead + facets)

---

## Part 4: Success Criteria and Launch Checklist

### MVP Success Criteria

MVP is considered complete when:

- ✅ Public hub has Overview, Rankings, Server Detail (Overview/Evidence/Drift/Graph), Daily Brief, Methodology, Feeds
- ✅ Daily pipeline produces scores, drift, daily brief, and publishes with atomic swap
- ✅ Private registry supports: auth, workspace, inventory, policies, evidence pack upload, JSON export
- ✅ Every public score has visible explainability, evidence confidence, and last assessed timestamp

### Launch Checklist

**Before Launch:**
- [ ] All Phase 1-4 tickets completed
- [ ] End-to-end testing (seed data → pipeline → API → UI)
- [ ] Performance testing (API response times < 500ms)
- [ ] Security audit
- [ ] Legal review (disclaimers, fairness page)
- [ ] Analytics configured (GA4 or Plausible)
- [ ] Monitoring and alerts set up

**Launch Day:**
- [ ] Deploy to production
- [ ] Verify custom domain (secairadar.cloud)
- [ ] Run first production pipeline
- [ ] Verify feeds (RSS, JSON)
- [ ] Test all public pages
- [ ] Monitor error rates

**Post-Launch:**
- [ ] Track success metrics (freshness, engagement, trust, growth)
- [ ] Gather user feedback
- [ ] Iterate on issues

### Success Metrics

- **Freshness:** Daily run success rate ≥ 95%
- **Engagement:** CTR overview → server detail ≥ 25%
- **Trust:** Evidence tab open rate ≥ 30%
- **Growth:** Tracked servers increases week-over-week
- **Conversion:** Evidence submissions, enterprise inquiries

---

## Next Steps

1. ✅ **Create GitHub Project** - ✅ Complete (Project #3 created)
2. ✅ **Create GitHub Issues** - ✅ Complete (30+ unique tickets converted to issues)
3. ✅ **Create Milestones & Labels** - ✅ Complete (6 milestones, all labels created)
4. **Organize Project Board** - Set up columns and organize issues by phase
5. **Begin Phase 0** - Start with monorepo restructure and CI/CD setup
6. **Follow Implementation Plan** - Work through phases sequentially

## GitHub Setup Status ✅

**Completed:**
- ✅ GitHub Project created (Project #3: "Verified MCP MVP Implementation")
- ✅ 6 Milestones created (Phase 0-4 + MVP Launch)
- ✅ All labels created (categories, priorities, phases, status)
- ✅ 30+ GitHub issues created from backlog tickets
- ✅ Completed tickets properly closed (T-004, T-040-T-048, T-060)
- ✅ All issues added to project board

**Project URL:** https://github.com/orgs/zimaxnet/projects/3

---

## References

- **Master Services Document:** `secairadar-cloud-master-services-kickoff-v1.md`
- **Backlog:** `docs/backlog/mvp-build-tickets.md`
- **Implementation Plan:** `docs/implementation/reference-implementation-plan.md`
- **Database Schema:** `docs/implementation/database-schema.sql`
- **Build Order:** `docs/implementation/build-order.md`
- **Security Model:** `docs/implementation/security-model.md`
- **Automation Blueprint:** `docs/automation/automation-blueprint.md`
- **MVP PRD:** `docs/product/mvp-prd.md`
- **Refactoring Summary:** `REFACTORING-SUMMARY.md`
- **Refactoring Progress:** `REFACTORING-PROGRESS.md`

---

**Document Status:** Complete  
**Last Updated:** 2026-01-23  
**Ready for Implementation:** Yes
