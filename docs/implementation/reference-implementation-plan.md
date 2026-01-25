# SecAI Radar — Verified MCP Reference Implementation Plan

**Version:** v0.1  
**Date:** 2026-01-23  
**Timezone:** America/Phoenix  
**Reference:** Step 5 Reference Implementation Plan Document

## Overview

This document provides a concrete implementation plan for building:
- **Public trust hub**: secairadar.cloud/mcp dashboards + feeds
- **Private Trust Registry**: app.secairadar.cloud (org workspaces)
- **ctxeco integration**: api.ctxeco.com/mcp (managed MCP endpoint) + "Verified MCP" guarantees
- **GK layer**: openContextGraph-backed "look behind the veil"

## Implementation Goals (Non-Negotiables)

1. **Transparency**: every score has "why + evidence + drift"
2. **Freshness**: daily automation with drift and deltas
3. **Separation of concerns**:
   - Public hub (no auth) is a read-only projection
   - Private registry (auth) holds evidence packs and org policy
4. **Auditability**: append-only history for score snapshots and drift events
5. **Operational safety**: never publish partial datasets; always stamp Last Assessed + Evidence Confidence
6. **Multi-tenant security**: strict tenant/workspace isolation and RBAC

## Recommended Azure Architecture

### Compute

**Azure Container Apps (ACA)** for:
- `public-api` (read-only endpoints for dashboards/feeds)
- `public-web` (Next.js/SPA static or SSR; optional)
- `registry-api` (private workspace API)
- `pipeline-workers` (jobs/consumers: Scout, Curator, Evidence Miner, Scorer, Drift, Publisher)
- `storyteller` (Sage Meridian content generator integration)

Alternative: Functions for jobs; but ACA Jobs provide consistent container runtime.

### Data Stores

**PostgreSQL (Azure Database for PostgreSQL Flexible Server)**:
- Authoritative relational store for Providers, Servers, Evidence metadata, ScoreSnapshots, DriftEvents, DailyBriefs, Workspaces, Policies, Approvals

**Graph store (choose 1 initially; add later if needed)**
- MVP: store graph as JSON subgraph in Postgres (`server_graph_snapshot`) and generate explorer from that
- v1: add a dedicated graph DB:
  - Option A: **Azure Cosmos DB (Gremlin)** for graph queries
  - Option B: Neo4j Aura / self-host (if you prefer)
  - Option C: Postgres + pgvector + adjacency (if you want to keep infra simple)

**Object storage (Azure Storage)**
- Evidence artifacts (private): uploaded packs, PDFs, screenshots
- Public generated assets: image cards, JSON dataset exports (optional)
- Use separate containers: `evidence-private`, `public-assets`, `exports-private`

**Search index**
- MVP: Postgres full-text + simple filters
- v1: **Azure AI Search** to power fast search/facets for servers/providers and "typeahead"

### Messaging / Orchestration

- MVP: simple scheduled jobs (ACA Jobs) + direct DB coordination
- v1: add **Azure Service Bus** for:
  - `ingest.raw`
  - `normalize.canonical`
  - `evidence.extract`
  - `score.compute`
  - `drift.detect`
  - `publish.update`
  - `outbox.queue`

This improves reliability and allows horizontal scaling per agent.

### Identity & Secrets

- **Managed Identities** for all services
- **Azure Key Vault** for:
  - API keys to external sources (if any)
  - signing keys for your own tokens
  - database credentials (if not using MI auth)
- **Entra ID** OIDC for users accessing `registry-api`

### Networking

- Public endpoints for public web/API (Front Door optional)
- Private endpoints for DB, Key Vault, Storage where feasible
- Consider separate ACA environments for public and private services

### Edge / CDN / Routing

- **Azure Front Door** (recommended) for:
  - TLS + WAF + caching for public dashboards and feeds
  - routing: `secairadar.cloud` → public web/API, `app.secairadar.cloud` → private web/API
- Or start with DNS + direct endpoints; add Front Door for v1

## Build Order (MVP → v1) — Week-by-Week

### Phase 0 (Day 1–2): Repo + CI Skeleton

- Mono-repo structure:
  - `/apps/public-web`
  - `/apps/public-api`
  - `/apps/registry-api`
  - `/apps/workers/*` (scout, curator, miner, scorer, drift, publisher)
  - `/packages/shared` (types, schemas, scoring rubric)
- GitHub Actions pipeline: build → test → deploy (ACA)

### Phase 1 (Week 1): Public MVP "Truth Hub"

**Goal:** Rankings + server pages + daily brief, driven by manual seed + Batch 1.

**Deliverables:**
1. Postgres schema + migrations
2. Public API:
   - summary, rankings, server detail, evidence, drift, daily brief
3. Public web UI:
   - /mcp, /mcp/rankings, /mcp/servers/:slug, /mcp/daily/:date, /mcp/methodology
4. RSS + JSON feeds
5. Publisher "staging swap" mechanism

### Phase 2 (Week 2): Automation Pipeline MVP (Daily Refresh)

**Goal:** Daily run that updates scores/deltas and generates briefs.

**Deliverables:**
- Scout + Curator for Tier 1 sources
- Evidence Miner for doc/repo extraction (basic signals)
- Scorer implementing Trust Score v1 + Evidence Confidence
- Drift Sentinel diffing score/flags/evidence changes
- Daily Brief generator (Sage Meridian prompt inputs + output storage)
- Outbox drafts created in DB (posting handled later)

### Phase 3 (Week 3): Private Trust Registry MVP

**Goal:** Customer workspace can govern servers.

**Deliverables:**
- Entra login + RBAC roles
- Workspace creation and membership
- Inventory (add server to workspace)
- Policies (allow/deny/require approval)
- Evidence pack upload (private blob)
- Export "audit pack" v0 (JSON first; PDF later)

### Phase 4 (Week 4): GK "Look Behind the Veil" MVP

**Goal:** Graph explorer on server pages.

**Deliverables:**
- Graph snapshot builder in pipeline:
  - Server → Tools → Scopes → Data Domains → Evidence → Flags
- Store graph JSON in Postgres
- Public `/graph` endpoint and UI explorer (basic interactive)

### v1 (Weeks 5–8): Production Hardening + Flair

- Move to Service Bus for pipeline events
- Add Azure AI Search for fast faceted search
- Implement provider right-to-respond workflow
- Enhanced drift detection (docs hash diffing + endpoint/cert monitoring where feasible)
- Visual card pipeline (store images in public-assets with immutable URLs)
- Front Door + WAF + caching rules
- SOC2-ready logging, alerts, and incident runbooks (internal)

## Security Model

### Public API
- No auth
- Rate limiting + caching + WAF
- No private evidence artifacts exposed
- Public redaction policy enforced in API layer

### Private Registry API
- OIDC (Entra ID) JWT validation
- Workspace isolation:
  - Every row keyed by `workspaceId`
  - Enforce row-level security (RLS) where possible
- Roles:
  - `RegistryAdmin`: manage workspace + members + policies
  - `PolicyApprover`: approve/deny policies
  - `EvidenceValidator`: validate evidence packs
  - `Viewer`: read-only
  - `AutomationOperator`: run/schedule agents and view runs
- Strong audit logging:
  - every policy change and approval stored
  - evidence pack access logged

### Secrets, Tokens, and Integrations
- All service-to-service auth via Managed Identity
- Tokens to external platforms (posting service) stored in Key Vault
- Prefer "draft outbox" creation only inside SecAI Radar; posting performed by a separate component with minimal privileges

### Data Protection
- Encryption at rest by default
- Separate storage containers for public vs private
- Export artifacts are time-limited signed URLs
- PII minimization: do not store user PII beyond required identity claims (subject ID)

## Public Dataset Publishing Model (Anti-Partial Updates)

Use a two-phase publish:
1. Pipeline writes to `staging` tables / blob paths
2. Publisher validates completeness (counts, checksums, sanity rules)
3. Publisher swaps:
   - update `latest_scores` pointers
   - publish `rankings_cache`
   - update `/public-datasets/latest.json` pointer (optional)
4. Pages/API read only "latest stable" pointers

If validation fails:
- keep yesterday's stable dataset live
- add "staleness banner" to public UI

## Daily Media Implementation Plan (Outbox + Distribution)

### Outbox Schema
- `outbox_items` (id, date, channel, content, mediaUrls, status, scheduledAt, sentAt, error)

### Distribution Service (Separate Component)
- Reads queued items per channel
- Applies per-channel cadence policy:
  - X + LinkedIn: daily
  - Reddit: weekly
  - HN/Lobsters: major events only
- Handles retries + rate limits + token refresh
- Writes back status and permalinks

> If you want zero external posting automation at first, keep "outbox drafts" and post manually.

## Implementation "Definition of Done" (MVP Launch)

**Public:**
- /mcp overview + rankings + server pages + daily brief
- RSS + JSON feed live
- Each server has Trust Score + Evidence Confidence + last assessed
- Drift timeline shows at least score/evidence/flag changes

**Automation:**
- Daily run completes end-to-end with stable publish
- Daily brief text generated and stored
- Outbox drafts created

**Private:**
- (optional for MVP) basic workspace + inventory + policy skeleton

## Suggested Engineering Tasks (Top 20 Backlog)

1. Create DB schema + migrations
2. Implement scoring library package (`packages/scoring`)
3. Implement evidence claim types + parser framework
4. Build public API endpoints (summary/rankings/server/evidence/drift/daily)
5. Build public web pages (4 core routes)
6. Implement publisher staging swap + validation
7. Build Scout ingestors (Tier 1 sources)
8. Build Curator canonical IDs + dedupe queue
9. Build Evidence Miner (docs/repo extraction baseline)
10. Build Scorer (Trust Score v1 + Evidence Confidence)
11. Build Drift Sentinel (diff + severity)
12. Build Daily Brief generator (Sage Meridian prompt + storage)
13. Create RSS feed renderer
14. Create JSON Feed renderer
15. Implement outbox drafts + UI page to review drafts
16. Entra auth for private API
17. Workspace + membership model (RBAC)
18. Policy objects + approval workflow
19. Evidence pack upload to blob + metadata + validation status
20. Audit pack JSON export v0
