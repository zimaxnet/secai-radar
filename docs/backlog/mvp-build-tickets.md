# SecAI Radar Verified MCP - MVP Build Tickets (Backlog)

**Version:** v0.1  
**Date:** 2026-01-23  
**Total Tickets:** 60+  
**Legend:** FE=Frontend • BE=Backend/API • DATA=Data • PIPE=Pipeline/Agents • SEC=Security • DEVOPS=CI/CD/Infra • UX=Copy/Docs

## Phase 0 — Repo + CI Skeleton (Day 1–2)

### T-001 (DEVOPS) Monorepo scaffolding
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Create repo structure (`apps/public-web`, `apps/public-api`, `apps/registry-api`, `apps/workers/*`, `packages/shared`).  
**Dependencies:** none  
**Acceptance criteria:**
- [ ] Folder structure exists with readme per app
- [ ] `packages/shared` exports types + schemas placeholder
- [ ] Workspace configured; one command builds all apps

**Estimated Effort:** 4 hours

---

### T-002 (DEVOPS) GitHub Actions: build/test pipeline
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** CI workflow for PRs (lint + unit tests + build).  
**Dependencies:** T-001  
**Acceptance criteria:**
- [ ] Workflow runs on PR and main
- [ ] Fails on lint/test/build errors
- [ ] Artifacts generated for public-web build

**Estimated Effort:** 6 hours

---

### T-003 (DEVOPS) Deploy pipeline skeleton (staging)
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** CD workflow to deploy to Azure (ACA) for staging environment.  
**Dependencies:** T-002  
**Acceptance criteria:**
- [ ] One-click deploy to staging
- [ ] Uses secrets from GH + Key Vault reference (placeholder ok)
- [ ] Rollback documented (manual ok)

**Estimated Effort:** 8 hours

---

### T-004 (UX) Standard copy + disclaimer snippets package
**Status:** ✅ Completed  
**Priority:** P1  
**Description:** Create `packages/shared/copy` with labels, disclaimers, flag tooltips.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [x] Export constants for: Evidence Confidence labels, Tier labels, disclaimers, flag definitions
- [x] Used by at least one FE page

**Estimated Effort:** 2 hours  
**Notes:** Already implemented in `web/src/utils/copy.ts`

---

## Phase 1 — Public MVP "Truth Hub" (Week 1)

### Data + Migrations

### T-010 (DATA) Postgres schema + migrations v0
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Create baseline tables: providers, mcp_servers, evidence_items, evidence_claims, score_snapshots, drift_events, daily_briefs, rubric_versions.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [ ] Migration scripts run end-to-end
- [ ] Primary keys + indexes for `serverSlug`, `providerId`, `assessedAt`
- [ ] Seed script inserts sample provider/server/score

**Estimated Effort:** 8 hours  
**Notes:** Schema already defined in `docs/implementation/database-schema.sql`

---

### T-011 (DATA) Latest projections
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Implement `latest_scores` pointer table + materialized view for latest assessments.  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Query returns server + latest score in <200ms on 1k rows (local dev)
- [ ] Refresh job script exists (manual invocation ok)

**Estimated Effort:** 4 hours

---

### T-012 (DATA) Rankings cache table
**Status:** ⏳ Pending  
**Priority:** P1  
**Description:** Create `rankings_cache` table keyed by filters hash + window.  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Cache read/write helpers exist
- [ ] TTL behavior documented (e.g., 5 min)

**Estimated Effort:** 3 hours

---

### Public API (Read-Only)

### T-020 (BE) Public API skeleton + response envelope
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Implement `/api/v1/public/*` base with standard envelope and error schema.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [ ] `GET /health` returns ok
- [ ] Envelope includes `methodologyVersion` + `generatedAt`
- [ ] Consistent error shape with codes

**Estimated Effort:** 4 hours

---

### T-021 (BE) GET summary endpoint
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/summary?window=24h`  
**Dependencies:** T-011  
**Acceptance criteria:**
- [ ] Returns KPIs + highlights (empty-safe)
- [ ] Includes tier counts + evidence confidence counts
- [ ] Window parameter validates (24h/7d/30d)

**Estimated Effort:** 6 hours

---

### T-022 (BE) GET rankings endpoint with filters
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/rankings`  
**Dependencies:** T-011  
**Acceptance criteria:**
- [ ] Supports q, category/tag, authModel, deploymentType, toolAgency, tier, evidenceConfidence, flags
- [ ] Pagination (page/pageSize) + total count
- [ ] Sort works: trustScore, evidenceConfidence, lastAssessedAt, deltas

**Estimated Effort:** 8 hours

---

### T-023 (BE) GET server detail endpoint
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Accepts slug or id
- [ ] Returns server metadata + latestScore + explainability
- [ ] Returns 404 with error schema when missing

**Estimated Effort:** 6 hours

---

### T-024 (BE) GET server evidence endpoint
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}/evidence`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Returns evidence list + extracted claims (public-safe)
- [ ] Evidence items include confidence + capturedAt
- [ ] Claims include sourceUrl + sourceEvidenceId

**Estimated Effort:** 4 hours

---

### T-025 (BE) GET server drift endpoint
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}/drift?window=90d`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Returns ordered drift events with severity
- [ ] Window validates; default 30d
- [ ] Event types normalized

**Estimated Effort:** 4 hours

---

### T-026 (BE) GET daily brief endpoint
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/daily/{YYYY-MM-DD}`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Returns brief object (long+short+lists)
- [ ] Returns 404 if missing (until generated)
- [ ] Includes methodologyVersion

**Estimated Effort:** 4 hours

---

### T-027 (BE) HTTP caching (ETag + Cache-Control)
**Status:** ⏳ Pending  
**Priority:** P1  
**Description:** Add ETag and caching headers to public endpoints.  
**Dependencies:** T-020  
**Acceptance criteria:**
- [ ] Rankings and summary return ETag
- [ ] 304 works with If-None-Match
- [ ] Cache-Control set per endpoint policy

**Estimated Effort:** 4 hours

---

### Feeds (Public)

### T-030 (BE) RSS/Atom renderer
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /mcp/feed.xml`  
**Dependencies:** T-026  
**Acceptance criteria:**
- [ ] Valid XML feed; includes at least DailyBrief items
- [ ] Items include link + pubDate + description
- [ ] Feed validates in common readers (manual check)

**Estimated Effort:** 4 hours  
**Notes:** Feed generation utilities already exist in `web/src/utils/feeds.ts`

---

### T-031 (BE) JSON Feed renderer
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /mcp/feed.json`  
**Dependencies:** T-026  
**Acceptance criteria:**
- [ ] Valid JSON Feed fields: version, title, feed_url, items
- [ ] Items include id, url, title, content_text, date_published

**Estimated Effort:** 3 hours  
**Notes:** Feed generation utilities already exist in `web/src/utils/feeds.ts`

---

### Public Web UI (secairadar.cloud/mcp)

### T-040 (FE) Public web shell + routing
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Implement routes: /mcp, /mcp/rankings, /mcp/servers/:slug, /mcp/daily/:date, /mcp/methodology, /mcp/submit.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [x] All routes render and fetch from public API
- [x] Global nav + footer present
- [x] 404 page exists

**Estimated Effort:** 4 hours  
**Notes:** Already implemented in Step 1

---

### T-041 (FE) Overview dashboard modules
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Build Today's Brief hero, KPI strip, Movers/Downgrades/New, Flags trending, Recently Updated table.  
**Dependencies:** T-021, T-022  
**Acceptance criteria:**
- [x] Modules render with loading + empty states
- [x] Clicking items navigates to server pages
- [x] "Updated in last" control changes window query

**Estimated Effort:** 8 hours  
**Notes:** Already implemented in Step 1

---

### T-042 (FE) Rankings dashboard with facet filters
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-022  
**Acceptance criteria:**
- [x] Facets update URL query string
- [x] Table supports sorting and pagination
- [x] Evidence Confidence badge shows popover definitions

**Estimated Effort:** 8 hours  
**Notes:** Already implemented in Step 1

---

### T-043 (FE) Server detail page: Overview tab
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-023  
**Acceptance criteria:**
- [x] Shows score, tier, evidence confidence, last assessed, enterprise fit
- [x] Displays D1–D6 breakdown chart (simple bars ok)
- [x] Shows flags + mitigations card

**Estimated Effort:** 6 hours  
**Notes:** Already implemented in Step 1

---

### T-044 (FE) Server detail page: Evidence tab
**Status:** 🔄 Partial  
**Priority:** P0  
**Dependencies:** T-024  
**Acceptance criteria:**
- [x] Evidence table renders with links (placeholder)
- [ ] Claims panel renders (auth model, hosting, retention, audit)
- [ ] "Evidence gaps" callout shows when unknown

**Estimated Effort:** 6 hours  
**Notes:** Basic structure exists, needs API integration

---

### T-045 (FE) Server detail page: Drift tab
**Status:** 🔄 Partial  
**Priority:** P0  
**Dependencies:** T-025  
**Acceptance criteria:**
- [x] Timeline shows severity badges + event summary (placeholder)
- [ ] "What changed since yesterday?" summary computed from latest events

**Estimated Effort:** 4 hours  
**Notes:** Basic structure exists, needs API integration

---

### T-046 (FE) Daily brief page
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-026  
**Acceptance criteria:**
- [x] Renders narrative + lists + links
- [x] Shows methodologyVersion + disclaimers

**Estimated Effort:** 6 hours  
**Notes:** Already implemented in Step 2

---

### T-047 (FE/UX) Methodology page
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-004  
**Acceptance criteria:**
- [x] Defines Trust Score + Evidence Confidence + disclaimers
- [x] Links to changelog (stub ok)
- [x] Provides "submit evidence" instructions

**Estimated Effort:** 4 hours  
**Notes:** Already implemented in Step 6

---

### T-048 (FE) Submit evidence page (public)
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** none  
**Acceptance criteria:**
- [x] Provider submission form (email + server URL + evidence links)
- [ ] Submits to placeholder endpoint or stores as "submission record"
- [x] Shows "not a certification" acknowledgement checkbox

**Estimated Effort:** 4 hours  
**Notes:** Form implemented, needs backend API

---

### Publish Safety

### T-050 (BE) Redaction middleware for public responses
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Ensure public endpoints never expose private blob refs or sensitive artifact fields.  
**Dependencies:** T-024  
**Acceptance criteria:**
- [ ] Unit test: private-only fields are removed
- [ ] Public evidence items include only safe fields
- [ ] Slug/id cannot retrieve private records

**Estimated Effort:** 4 hours

---

### T-051 (BE/DEVOPS) Staging swap publishing pattern
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Implement "staging dataset" + atomic pointer swap for latest.  
**Dependencies:** T-011  
**Acceptance criteria:**
- [ ] Pipeline writes to staging tables or staging partitions
- [ ] Publisher validates counts then flips pointer
- [ ] Failure keeps previous "stable" dataset live

**Estimated Effort:** 8 hours

---

## Phase 2 — Automation Pipeline MVP (Week 2)

### T-060 (PIPE/DATA) Shared types + JSON schemas
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Define shared TS/JSON schemas for Provider, Server, Evidence, ScoreSnapshot, DriftEvent, DailyBrief.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [x] Schemas compile/validate
- [x] Used by at least one worker and one API response

**Estimated Effort:** 4 hours  
**Notes:** Already implemented in Steps 2-4

---

### T-061 (PIPE) Scoring library (Trust Score v1)
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Implement scoring function and flag rules in `packages/scoring`.  
**Dependencies:** T-060  
**Acceptance criteria:**
- [ ] Deterministic scoring from inputs
- [ ] Unit tests for 5 sample servers (including fail-fast)
- [ ] Returns d1..d6, trustScore, tier, enterpriseFit, flags, explainability skeleton

**Estimated Effort:** 16 hours

---

### T-062 (PIPE) Evidence Confidence calculator
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-060  
**Acceptance criteria:**
- [ ] Computes 0–3 from evidence item types/confidence
- [ ] Test cases: none→0, public docs→1, verifiable artifacts→2, validated pack→3

**Estimated Effort:** 4 hours

---

### Workers / Jobs (Tier 1 Sources First)

### T-070 (PIPE) Worker: Scout (discovery ingest)
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Pull from Tier 1 sources and store raw observations.  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Stores raw items with sourceUrl + retrievedAt + rawHash
- [ ] Does not overwrite; append-only
- [ ] Runs as scheduled job locally and in staging

**Estimated Effort:** 12 hours

---

### T-071 (PIPE) Worker: Curator (canonicalize + dedupe)
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-070  
**Acceptance criteria:**
- [ ] Produces canonical provider/server records
- [ ] Implements ID precedence: repoUrl > endpoint host > docs URL > name+source
- [ ] Creates alias records or logs review queue when ambiguous

**Estimated Effort:** 12 hours  
**Notes:** Dedupe utilities already exist in `web/src/utils/dedupe.ts`

---

### T-072 (PIPE) Worker: Evidence Miner (basic docs/repo extraction)
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-071  
**Acceptance criteria:**
- [ ] Captures docs/repo evidence items (Docs/Repo) when available
- [ ] Extracts minimum claims: AuthModel, HostingCustody (if present), ToolAgency hints
- [ ] Stores claims with sourceEvidenceId and capturedAt

**Estimated Effort:** 16 hours

---

### T-073 (PIPE) Worker: Scorer
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-072, T-061, T-062  
**Acceptance criteria:**
- [ ] Computes latest score snapshot per server
- [ ] Writes append-only score_snapshots
- [ ] Updates latest_scores pointer (staging first)

**Estimated Effort:** 12 hours

---

### T-074 (PIPE) Worker: Drift Sentinel
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-073  
**Acceptance criteria:**
- [ ] Detects changes in score, tier, flags, evidence additions/removals
- [ ] Writes drift events with severity
- [ ] Produces "top movers/downgrades" candidate lists

**Estimated Effort:** 12 hours  
**Notes:** Calculation utilities already exist in `web/src/utils/calculations.ts`

---

### T-075 (PIPE) Worker: Daily Brief generator (Sage Meridian integration stub)
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-074  
**Acceptance criteria:**
- [ ] Generates DailyBrief payload from structured movers/downgrades/new/drift
- [ ] Uses prompt template stored in repo
- [ ] Stores narrativeShort + placeholder narrativeLong (or generated text)

**Estimated Effort:** 8 hours  
**Notes:** Social template generators already exist in `web/src/utils/socialTemplates.ts`

---

### T-076 (PIPE/BE) Publisher job hooks
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-075, T-051  
**Acceptance criteria:**
- [ ] Runs validation checks and flips stable pointers
- [ ] Refreshes rankings_cache for common filter combos
- [ ] Ensures feeds read latest daily brief

**Estimated Effort:** 8 hours

---

### Observability + Reliability

### T-080 (DEVOPS) Run logs + run status table
**Status:** ⏳ Pending  
**Priority:** P1  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Each pipeline run writes a run record (started, finished, success, errors)
- [ ] Public UI can show "last updated" time
- [ ] Basic alert on failure (email/webhook stub ok)

**Estimated Effort:** 6 hours

---

### T-081 (BE) Status endpoint + stale banner support
**Status:** ⏳ Pending  
**Priority:** P1  
**Dependencies:** T-080  
**Acceptance criteria:**
- [ ] `GET /api/v1/public/status` returns last successful run timestamp
- [ ] FE shows stale banner when >24h

**Estimated Effort:** 4 hours

---

## Phase 3 — Private Trust Registry MVP (Week 3)

### T-090 (SEC/BE) Entra OIDC auth for registry-api
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-001  
**Acceptance criteria:**
- [ ] Validates JWTs
- [ ] Rejects unauthenticated requests
- [ ] Extracts user subject + tenant info

**Estimated Effort:** 12 hours

---

### T-091 (SEC/DATA) Workspace + membership tables
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-010  
**Acceptance criteria:**
- [ ] Tables for workspaces + members + roles
- [ ] Seed script creates demo workspace and admin user

**Estimated Effort:** 4 hours  
**Notes:** Schema already defined in `docs/implementation/database-schema.sql`

---

### T-092 (SEC/BE) RBAC middleware
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-090, T-091  
**Acceptance criteria:**
- [ ] Enforces roles per endpoint
- [ ] Denies cross-workspace access
- [ ] Unit tests for each role

**Estimated Effort:** 12 hours

---

### T-100 (BE) Registry: list/add servers to workspace inventory
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoints:** `GET/POST /api/v1/private/registry/servers`  
**Dependencies:** T-092  
**Acceptance criteria:**
- [ ] Can add serverId to workspace inventory with owner/purpose/environment fields
- [ ] List returns only workspace items
- [ ] Audit log record created

**Estimated Effort:** 8 hours

---

### T-101 (BE) Registry: policies CRUD
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoints:** `GET/POST /api/v1/private/registry/policies`  
**Dependencies:** T-092  
**Acceptance criteria:**
- [ ] Create policy with decision Allow/Deny/RequireApproval
- [ ] Supports conditions: evidenceConfidence >= N, toolAgency constraints, expiresAt
- [ ] List returns workspace policies only

**Estimated Effort:** 12 hours

---

### T-102 (BE) Registry: policy approvals
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoints:** `POST /policies/{id}/approve|deny`  
**Dependencies:** T-101  
**Acceptance criteria:**
- [ ] Approval requires PolicyApprover role
- [ ] Approval records stored with timestamps
- [ ] Policy state updates

**Estimated Effort:** 6 hours

---

### T-103 (BE/SEC) Evidence pack upload (private blob)
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `POST /api/v1/private/registry/evidence-packs`  
**Dependencies:** T-092  
**Acceptance criteria:**
- [ ] Upload stores blob in private container
- [ ] Metadata stored with serverId + workspaceId + status=submitted
- [ ] Download requires workspace membership

**Estimated Effort:** 12 hours

---

### T-104 (BE) Evidence pack validation workflow
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `POST /evidence-packs/{id}/validate`  
**Dependencies:** T-103  
**Acceptance criteria:**
- [ ] EvidenceValidator role required
- [ ] Updates status to validated + validatedAt
- [ ] Triggers recalculation hook (async stub ok)

**Estimated Effort:** 6 hours

---

### T-105 (BE) Audit pack export v0 (JSON)
**Status:** ⏳ Pending  
**Priority:** P1  
**Endpoint:** `POST /api/v1/private/registry/exports/audit-pack`  
**Dependencies:** T-100, T-101  
**Acceptance criteria:**
- [ ] Generates JSON export containing inventory, policies, scores, drift (date range)
- [ ] Export stored in private blob
- [ ] Status endpoint returns ready + signed URL

**Estimated Effort:** 12 hours

---

### T-110 (FE) Private shell + login redirect
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-090  
**Acceptance criteria:**
- [ ] Authenticated route loads workspace context
- [ ] Shows user role + workspace selector (single ok)

**Estimated Effort:** 8 hours

---

### T-111 (FE) Registry inventory UI
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-100  
**Acceptance criteria:**
- [ ] List inventory items
- [ ] Add server to inventory (by slug/id search)
- [ ] Show latest trust score in list

**Estimated Effort:** 12 hours

---

### T-112 (FE) Policy UI (create + list)
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-101  
**Acceptance criteria:**
- [ ] Create Allow/Deny/RequireApproval
- [ ] Shows approval state + expiry
- [ ] Validates evidenceConfidence threshold

**Estimated Effort:** 12 hours

---

### T-113 (FE) Evidence pack upload UI
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-103  
**Acceptance criteria:**
- [ ] Upload file and show status
- [ ] Shows "validated" state when approved
- [ ] No public exposure of blob refs

**Estimated Effort:** 8 hours

---

## Phase 4 — GK Explorer MVP + Hardening (Week 4)

### T-120 (PIPE/DATA) Graph snapshot builder job
**Status:** ⏳ Pending  
**Priority:** P0  
**Description:** Build per-server graph snapshot JSON: Server→Tools→Scopes→DataDomains→Evidence→Flags.  
**Dependencies:** T-072, T-073  
**Acceptance criteria:**
- [ ] Writes graph JSON to a `server_graph_snapshots` table keyed by serverId + assessedAt
- [ ] Includes nodes + edges; nodes reference evidence IDs when applicable

**Estimated Effort:** 12 hours

---

### T-121 (BE) Public server graph endpoint
**Status:** ⏳ Pending  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}/graph`  
**Dependencies:** T-120  
**Acceptance criteria:**
- [ ] Returns redacted nodes/edges (no private refs)
- [ ] ETag enabled
- [ ] Handles missing graph with empty set + meta message

**Estimated Effort:** 4 hours

---

### T-122 (FE) Graph tab UI (MVP viewer)
**Status:** 🔄 Partial  
**Priority:** P0  
**Dependencies:** T-121  
**Acceptance criteria:**
- [ ] Renders graph snapshot (basic force-directed or list view acceptable)
- [ ] Clicking node shows props + evidence links
- [ ] Degrades gracefully when graph missing

**Estimated Effort:** 12 hours  
**Notes:** Placeholder exists, needs graph visualization library

---

### T-130 (SEC) Public rate limiting + WAF rules (baseline)
**Status:** ⏳ Pending  
**Priority:** P1  
**Dependencies:** T-020  
**Acceptance criteria:**
- [ ] Rate limits enforced at edge or API
- [ ] Documented thresholds
- [ ] Abuse patterns blocked (basic rules)

**Estimated Effort:** 6 hours

---

### T-131 (SEC/BE) Audit logging (private)
**Status:** ⏳ Pending  
**Priority:** P0  
**Dependencies:** T-090  
**Acceptance criteria:**
- [ ] Every policy change, approval, evidence upload logged with userId + timestamp
- [ ] Logs queryable by workspace admin

**Estimated Effort:** 8 hours

---

### T-132 (DEVOPS) Backups + retention policy for DB + blobs
**Status:** ⏳ Pending  
**Priority:** P1  
**Dependencies:** T-010, T-103  
**Acceptance criteria:**
- [ ] Automated DB backups enabled
- [ ] Blob lifecycle rules defined for exports (expire)
- [ ] Restore procedure documented

**Estimated Effort:** 4 hours

---

### T-133 (DEVOPS) Observability dashboard
**Status:** ⏳ Pending  
**Priority:** P1  
**Dependencies:** T-080  
**Acceptance criteria:**
- [ ] Shows pipeline run success rate, duration, failures by stage
- [ ] Shows API error rates and latency percentiles

**Estimated Effort:** 8 hours

---

### T-134 (UX/LEGAL) Fairness + right-to-respond page + contact channel
**Status:** ⏳ Pending  
**Priority:** P1  
**Dependencies:** T-047  
**Acceptance criteria:**
- [ ] Public page describes right-to-respond process
- [ ] Provider submission contact method available
- [ ] Dispute handling steps documented

**Estimated Effort:** 4 hours

---

## Optional "Nice-to-Have" Tickets (Post-MVP)

### T-200 (FE) Compare tray (rankings)
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Allow users to compare up to 3 servers side-by-side  
**Estimated Effort:** 12 hours

---

### T-201 (BE/FE) Provider portfolio endpoints + pages
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Full provider portfolio pages with server lists and trends  
**Estimated Effort:** 16 hours

---

### T-202 (PIPE) Doc hash diff + richer drift classification
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Enhanced drift detection with document hash comparison  
**Estimated Effort:** 12 hours

---

### T-203 (FE) Visual cards gallery + immutable asset URLs
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Visual card generation and storage for social media  
**Estimated Effort:** 16 hours

---

### T-204 (DEVOPS) Service Bus eventing for pipeline scaling
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Move from direct DB coordination to Service Bus messaging  
**Estimated Effort:** 20 hours

---

### T-205 (BE) Search via Azure AI Search (typeahead + facets)
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Replace Postgres full-text with Azure AI Search  
**Estimated Effort:** 16 hours

---

## MVP Acceptance Summary

MVP is considered done when:
- [ ] Public hub has Overview, Rankings, Server Detail (Overview/Evidence/Drift/Graph), Daily Brief, Methodology, Feeds
- [ ] Daily pipeline produces scores, drift, daily brief, and publishes with atomic swap
- [ ] Private registry supports: auth, workspace, inventory, policies, evidence pack upload, JSON export
- [ ] Every public score has visible explainability, evidence confidence, and last assessed timestamp

## Ticket Status Legend

- ✅ Completed
- 🔄 In Progress / Partial
- ⏳ Pending / Not Started
- 🚫 Blocked
- ❌ Cancelled

## Priority Legend

- P0: Critical (must have for MVP)
- P1: High (important for MVP)
- P2: Nice to have (post-MVP)
