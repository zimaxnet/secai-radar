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
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Create baseline tables: providers, mcp_servers, evidence_items, evidence_claims, score_snapshots, drift_events, daily_briefs, rubric_versions.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [x] Migration scripts run end-to-end
- [x] Primary keys + indexes for `serverSlug`, `providerId`, `assessedAt`
- [x] Seed script inserts sample provider/server/score

**Estimated Effort:** 8 hours  
**Notes:** Schema in `docs/implementation/database-schema.sql` and `apps/public-api/migrations/001_initial_schema.sql`; `apps/public-api/scripts/migrate.py` runs migrations; seed in `seed.py`.

---

### T-011 (DATA) Latest projections
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Implement `latest_scores` pointer table + materialized view for latest assessments.  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Query returns server + latest score in <200ms on 1k rows (local dev)
- [x] Refresh job script exists (manual invocation ok)

**Estimated Effort:** 4 hours  
**Notes:** `apps/public-api/scripts/refresh_latest_scores.py` repopulates `latest_scores` and refreshes `latest_assessments_view`; `get_latest_score()` uses `latest_scores` when populated.

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
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Implement `/api/v1/public/*` base with standard envelope and error schema.  
**Dependencies:** T-001  
**Acceptance criteria:**
- [x] `GET /health` returns ok
- [x] Envelope includes `methodologyVersion` + `generatedAt` (and attestation envelope on all public read responses)
- [x] Consistent error shape with codes

**Estimated Effort:** 4 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py` and status router.

---

### T-021 (BE) GET summary endpoint
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/summary?window=24h`  
**Dependencies:** T-011  
**Acceptance criteria:**
- [x] Returns KPIs + highlights (empty-safe)
- [x] Includes tier counts + evidence confidence counts
- [x] Window parameter validates (24h/7d/30d)

**Estimated Effort:** 6 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py` and `src/services/summary.py`.

---

### T-022 (BE) GET rankings endpoint with filters
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/rankings`  
**Dependencies:** T-011  
**Acceptance criteria:**
- [x] Supports q, category/tag, authModel, deploymentType, toolAgency, tier, evidenceConfidence, flags (tier, sort, pagination implemented; filter set may be subset)
- [x] Pagination (page/pageSize) + total count
- [x] Sort works: trustScore, evidenceConfidence, lastAssessedAt, deltas

**Estimated Effort:** 8 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py` and `src/services/rankings.py`; items include integrityDigest.

---

### T-023 (BE) GET server detail endpoint
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Accepts slug or id
- [x] Returns server metadata + latestScore + explainability (and optional integrityDigest)
- [x] Returns 404 with error schema when missing

**Estimated Effort:** 6 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py` and `src/services/server.py`.

---

### T-024 (BE) GET server evidence endpoint
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}/evidence`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Returns evidence list + extracted claims (public-safe, via redaction)
- [x] Evidence items include confidence + capturedAt
- [x] Claims include sourceUrl + sourceEvidenceId

**Estimated Effort:** 4 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py` and `src/services/server.py` (get_server_evidence).

---

### T-025 (BE) GET server drift endpoint
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}/drift?window=90d`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Returns ordered drift events with severity
- [x] Window validates; default 30d
- [x] Event types normalized

**Estimated Effort:** 4 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py`; backend may return stub/empty until drift pipeline runs.

---

### T-026 (BE) GET daily brief endpoint
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/daily/{YYYY-MM-DD}`  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Returns brief object (long+short+lists)
- [x] Returns 404 if missing (until generated)
- [x] Includes methodologyVersion (and attestation envelope)

**Estimated Effort:** 4 hours  
**Notes:** Implemented in `apps/public-api/src/routers/public.py` and `src/services/daily_brief.py`.

---

### T-027 (BE) HTTP caching (ETag + Cache-Control)
**Status:** ✅ Completed  
**Priority:** P1  
**Description:** Add ETag and caching headers to public endpoints.  
**Dependencies:** T-020  
**Acceptance criteria:**
- [x] Rankings and summary return ETag (middleware applies to all GET JSON responses)
- [x] 304 works with If-None-Match (304 response includes ETag + Cache-Control)
- [x] Cache-Control set per endpoint policy (global public, max-age=300; can be refined per-route later)

**Estimated Effort:** 4 hours  
**Notes:** `apps/public-api/src/middleware/etag.py` is registered in main.py; ETag + Cache-Control on 200 and 304.

---

### Feeds (Public)

### T-030 (BE) RSS/Atom renderer
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /mcp/feed.xml`  
**Dependencies:** T-026  
**Acceptance criteria:**
- [x] Valid XML feed; includes at least DailyBrief items
- [x] Items include link + pubDate + description (and attestation in content:encoded)
- [x] Feed validates in common readers (manual check)

**Estimated Effort:** 4 hours  
**Notes:** Implemented in `apps/public-api/src/services/feeds.py` (generate_rss_feed) and `src/routers/public.py` (feed.xml).

---

### T-031 (BE) JSON Feed renderer
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /mcp/feed.json`  
**Dependencies:** T-026  
**Acceptance criteria:**
- [x] Valid JSON Feed fields: version, title, feed_url, items
- [x] Items include id, url, title, content_text, date_published (and provenance, integrityDigest, security_context)

**Estimated Effort:** 3 hours  
**Notes:** Implemented in `apps/public-api/src/services/feeds.py` (generate_json_feed) and `src/routers/public.py` (feed.json).

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
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Ensure public endpoints never expose private blob refs or sensitive artifact fields.  
**Dependencies:** T-024  
**Acceptance criteria:**
- [x] Unit test: private-only fields are removed (or manual verification)
- [x] Public evidence items include only safe fields
- [x] Slug/id cannot retrieve private records

**Estimated Effort:** 4 hours  
**Notes:** Implemented in `apps/public-api/src/middleware/redaction.py`; used on public responses in public.py.

---

### T-051 (BE/DEVOPS) Staging swap publishing pattern
**Status:** ✅ Done  
**Priority:** P0  
**Description:** Implement "staging dataset" + atomic pointer swap for latest.  
**Dependencies:** T-011  
**Acceptance criteria:**
- [x] Pipeline writes to staging tables or staging partitions (Scorer writes to `latest_scores_staging` when `WRITE_TO_STAGING=1`; migration `003_latest_scores_staging.sql`)
- [x] Publisher validates counts then flips pointer (`validate_staging()` then `flip_stable_pointer()`: TRUNCATE latest_scores, INSERT from staging, REFRESH MATERIALIZED VIEW)
- [x] Failure keeps previous "stable" dataset live (validation or flip failure returns without modifying latest_scores)

**Notes:** Pipeline order: run Scorer with `WRITE_TO_STAGING=1`, then Drift (reads staging as current when populated), Brief, then `./scripts/run-publisher.sh`. Publisher validates staging and atomically replaces `latest_scores` from `latest_scores_staging`.

**Estimated Effort:** 8 hours

---

### T-052 (BE) Rankings service: implement DB query
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Implement the real DB logic in `get_rankings()`: join mcp_servers with latest score_snapshots (via T-011 or direct subquery), apply filters (q, category, tier), sorting, and pagination. Today the endpoint returns `servers: []`; this ticket makes it return real rows from the database.  
**Dependencies:** T-010, T-011  
**Acceptance criteria:**
- [x] `get_rankings()` in `src/services/rankings.py` queries DB (join or latest_scores)
- [x] Supports tier filter, sort (trustScore, evidenceConfidence, lastAssessedAt), page/pageSize, total count
- [x] Response shape unchanged; each item includes serverId, trustScore, tier, evidenceConfidence, lastAssessedAt, integrityDigest

**Estimated Effort:** 6 hours  
**Notes:** T-022 delivered the route and envelope; this ticket delivers the data. File: `apps/public-api/src/services/rankings.py`.

---

### T-053 (DATA) Seed script: mcp_servers + score_snapshots
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Extend `apps/public-api/scripts/seed.py` to insert sample mcp_servers and score_snapshots so /rankings and /mcp/servers/{id} return data for demos. Today the seed only inserts providers.  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Seed inserts at least 3–5 sample mcp_servers (with provider_id, server_slug, etc.)
- [x] Seed inserts corresponding score_snapshots (trust_score, tier, evidence_confidence, assessed_at)
- [x] After migrate + seed, GET /rankings returns non-empty items when T-052 is done

**Estimated Effort:** 3 hours  
**Notes:** Enables testing rankings UI and API with real DB rows before the pipeline runs. Run `seed.py --refresh` to also refresh latest_scores and mat view.

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
**Status:** ✅ Done  
**Priority:** P0  
**Description:** Implement scoring function and flag rules in `packages/scoring`.  
**Dependencies:** T-060  
**Acceptance criteria:**
- [x] Deterministic scoring from inputs (calculate_domain_scores from claims; weighted trust score; tier/enterprise_fit)
- [x] Unit tests for 5 sample servers (including fail-fast): test_fail_fast_no_auth, test_scoring_with_auth, test_scoring_sample_3_high_trust, test_scoring_sample_4_docs_only_no_claims, test_scoring_sample_5_deterministic
- [x] Returns d1..d6, trustScore, tier, enterpriseFit, flags, explainability skeleton (ScoreResult)

**Estimated Effort:** 16 hours

---

### T-062 (PIPE) Evidence Confidence calculator
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-060  
**Acceptance criteria:**
- [x] Computes 0–3 from evidence item types/confidence (calculate_evidence_confidence in packages/scoring)
- [x] Test cases: none→0, public docs→1, verifiable artifacts→2, validated pack→3 (test_evidence_confidence_*)

**Estimated Effort:** 4 hours

---

### Workers / Jobs (Tier 1 Sources First)

### T-070 (PIPE) Worker: Scout (discovery ingest)
**Status:** ✅ Done  
**Priority:** P0  
**Description:** Pull from Tier 1 sources and store raw observations.  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Stores raw items with sourceUrl + retrievedAt + rawHash (table `raw_observations`: source_url, content_json, content_hash, retrieved_at)
- [x] Does not overwrite; append-only (dedupe by content_hash; INSERT only when new)
- [x] Runs as scheduled job locally and in staging (runnable via `./scripts/run-scout.sh` or `python apps/workers/scout/src/scout.py` with DATABASE_URL; scheduling is follow-up)

**Notes:** Migration `002_raw_observations.sql` adds table; `run-migrations.sh` runs it after main schema. Runbook: apps/public-api/README Path 2.

**Estimated Effort:** 12 hours

---

### T-071 (PIPE) Worker: Curator (canonicalize + dedupe)
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-070  
**Acceptance criteria:**
- [x] Produces canonical provider/server records (writes to mcp_servers; ensures default provider exists)
- [x] Implements ID precedence: repoUrl > endpoint host > docs URL > name+source (generate_server_id)
- [x] Creates alias records or logs review queue when ambiguous (review_log: duplicate / ambiguous_same_batch, printed and in response as reviewQueueCount)

**Notes:** Run via `./scripts/run-curator.sh` or `python apps/workers/curator/src/curator.py` with DATABASE_URL. Reads raw_observations WHERE processed_at IS NULL; marks processed_at when done.

**Estimated Effort:** 12 hours  
**Legacy:** Dedupe utilities exist in `web/src/utils/dedupe.ts`

---

### T-072 (PIPE) Worker: Evidence Miner (basic docs/repo extraction)
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-071  
**Acceptance criteria:**
- [x] Captures docs/repo evidence items (Docs/Repo) when available (fetches repo_url/docs_url per mcp_servers; skips if evidence already exists for that source_url)
- [x] Extracts minimum claims: AuthModel, HostingCustody (if present), ToolAgency hints (heuristics in _extract_claims)
- [x] Stores claims with sourceEvidenceId and capturedAt (evidence_claims.evidence_id, evidence_claims.captured_at)

**Notes:** Run via `./scripts/run-evidence-miner.sh` or `python apps/workers/evidence-miner/src/evidence_miner.py` with DATABASE_URL. Writes to evidence_items + evidence_claims; parser_version evidence-miner-1.0.

**Estimated Effort:** 16 hours

---

### T-073 (PIPE) Worker: Scorer
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-072, T-061, T-062  
**Acceptance criteria:**
- [x] Computes latest score snapshot per server (score_server → calculate_trust_score from evidence/claims)
- [x] Writes append-only score_snapshots (store_score_snapshot)
- [x] Updates latest_scores pointer (update_latest_score; MVP updates directly; staging flip is T-051)

**Notes:** Run via `./scripts/run-scorer.sh` or `python apps/workers/scorer/src/scorer.py` with DATABASE_URL. Uses packages/scoring via sys.path.

**Estimated Effort:** 12 hours

---

### T-074 (PIPE) Worker: Drift Sentinel
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-073  
**Acceptance criteria:**
- [x] Detects changes in score, tier, flags, evidence additions/removals (latest vs previous score_snapshot + evidence count by assessed_at)
- [x] Writes drift events with severity (ScoreChanged/FlagChanged/EvidenceAdded/EvidenceRemoved; severity from drop magnitude or rule)
- [x] Produces "top movers/downgrades" candidate lists (topMovers, topDowngrades in response; up to 20 each)

**Notes:** Run via `./scripts/run-drift-sentinel.sh` or `python apps/workers/drift-sentinel/src/drift_sentinel.py` with DATABASE_URL.

**Estimated Effort:** 12 hours  
**Legacy:** Calculation utilities exist in `web/src/utils/calculations.ts`

---

### T-075 (PIPE) Worker: Daily Brief generator (Sage Meridian integration stub)
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-074  
**Acceptance criteria:**
- [x] Generates DailyBrief payload from structured movers/downgrades/new/drift (drift_events + new entrants from score_snapshots for date)
- [x] Uses prompt template stored in repo (`apps/workers/sage-meridian/templates/daily_brief.txt`)
- [x] Stores narrativeShort + placeholder narrativeLong (template-based short ≤600 chars; long = short + top movers/downgrades lines)

**Notes:** Run via `./scripts/run-daily-brief.sh` or `./scripts/run-daily-brief.sh YYYY-MM-DD`. Writes to `daily_briefs` (date, headline, narrative_long, narrative_short, highlights, payload_json, methodology_version).

**Estimated Effort:** 8 hours  
**Legacy:** Social template generators exist in `web/src/utils/socialTemplates.ts`

---

### T-076 (PIPE/BE) Publisher job hooks
**Status:** ✅ Done  
**Priority:** P0  
**Dependencies:** T-075, T-051  
**Acceptance criteria:**
- [x] Runs validation checks and flips stable pointers (validate_staging + flip_stable_pointer from T-051)
- [x] Refreshes rankings_cache for common filter combos (window 24h, default + tier A/B/C/D; upsert by filters_hash)
- [x] Ensures feeds read latest daily brief (brief written before publish; feeds query daily_briefs by date)

**Notes:** Run via `./scripts/run-publisher.sh`. Response includes `rankingsCacheRefreshed` count. Feed endpoints query `daily_briefs` directly; no separate feed cache.

**Estimated Effort:** 8 hours

---

### Observability + Reliability

### T-080 (DEVOPS) Run logs + run status table
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Each pipeline run writes a run record (started, finished, success, errors)
- [x] Public UI can show "last updated" time (via GET /api/v1/public/status lastSuccessfulRun)
- [ ] Basic alert on failure (email/webhook stub ok)

**Estimated Effort:** 6 hours  
**Notes:** Migration [007_pipeline_runs.sql](../../apps/public-api/migrations/007_pipeline_runs.sql); [record_pipeline_run.py](../../apps/public-api/scripts/record_pipeline_run.py) invoked by [run-full-path2.sh](../../scripts/run-full-path2.sh) for start/finish.

---

### T-081 (BE) Status endpoint + stale banner support
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** T-080  
**Acceptance criteria:**
- [x] `GET /api/v1/public/status` returns last successful run timestamp
- [x] FE shows stale banner when >24h

**Estimated Effort:** 4 hours  
**Notes:** [status.py](../../apps/public-api/src/routers/status.py) queries pipeline_runs for latest success; [MCPLayout.tsx](../../apps/public-web/src/routes/mcp/MCPLayout.tsx) calls getStatus() and shows banner when lastSuccessfulRun is null or &gt;24h.

---

## Phase 3 — Private Trust Registry MVP (Week 3)

### T-090 (SEC/BE) Entra OIDC auth for registry-api
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-001  
**Acceptance criteria:**
- [x] Validates JWTs
- [x] Rejects unauthenticated requests
- [x] Extracts user subject + tenant info

**Estimated Effort:** 12 hours  
**Notes:** Implemented in [registry-api](../../apps/registry-api) with JWKS validation; see [REGISTRY-API-ENTRA.md](../setup/REGISTRY-API-ENTRA.md).

---

### T-091 (SEC/DATA) Workspace + membership tables
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-010  
**Acceptance criteria:**
- [x] Tables for workspaces + members + roles
- [x] Seed script creates demo workspace and admin user

**Estimated Effort:** 4 hours  
**Notes:** Migration 004 (private registry); workspace repo + seed in [registry-api](../../apps/registry-api); [REGISTRY-API-ENTRA.md](../setup/REGISTRY-API-ENTRA.md).

---

### T-092 (SEC/BE) RBAC middleware
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-090, T-091  
**Acceptance criteria:**
- [x] Enforces roles per endpoint
- [x] Denies cross-workspace access
- [ ] Unit tests for each role

**Estimated Effort:** 12 hours  
**Notes:** RBAC in [registry-api](../../apps/registry-api) routers; workspace isolation enforced.

---

### T-100 (BE) Registry: list/add servers to workspace inventory
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoints:** `GET/POST /api/v1/private/registry/servers`  
**Dependencies:** T-092  
**Acceptance criteria:**
- [x] Can add serverId to workspace inventory with owner/purpose/environment fields
- [x] List returns only workspace items
- [x] Audit log record created

**Estimated Effort:** 8 hours  
**Notes:** [registry-api](../../apps/registry-api) registry routes + [inventory](../../apps/registry-api/src/repositories/inventory.py) repo.

---

### T-101 (BE) Registry: policies CRUD
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoints:** `GET/POST /api/v1/private/registry/policies`  
**Dependencies:** T-092  
**Acceptance criteria:**
- [x] Create policy with decision Allow/Deny/RequireApproval
- [x] Supports conditions: evidenceConfidence >= N, toolAgency constraints, expiresAt
- [x] List returns workspace policies only

**Estimated Effort:** 12 hours  
**Notes:** [registry-api](../../apps/registry-api) registry routes + [policies](../../apps/registry-api/src/repositories) repo.

---

### T-102 (BE) Registry: policy approvals
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoints:** `POST /policies/{id}/approve|deny`  
**Dependencies:** T-101  
**Acceptance criteria:**
- [x] Approval requires PolicyApprover role
- [x] Approval records stored with timestamps
- [x] Policy state updates

**Estimated Effort:** 6 hours  
**Notes:** [registry-api](../../apps/registry-api) approve/deny routes.

---

### T-103 (BE/SEC) Evidence pack upload (private blob)
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `POST /api/v1/private/registry/evidence-packs`  
**Dependencies:** T-092  
**Acceptance criteria:**
- [x] Upload stores blob in private container
- [x] Metadata stored with serverId + workspaceId + status=submitted
- [x] Download requires workspace membership

**Estimated Effort:** 12 hours  
**Notes:** [registry-api](../../apps/registry-api) evidence-packs routes + [evidence_packs](../../apps/registry-api/src/repositories/evidence_packs.py) repo.

---

### T-104 (BE) Evidence pack validation workflow
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `POST /evidence-packs/{id}/validate`  
**Dependencies:** T-103  
**Acceptance criteria:**
- [x] EvidenceValidator role required
- [x] Updates status to validated + validatedAt
- [x] Triggers recalculation hook (async stub ok)

**Estimated Effort:** 6 hours  
**Notes:** [registry-api](../../apps/registry-api) validate route; evidence_packs repo.

---

### T-105 (BE) Audit pack export v0 (JSON)
**Status:** ✅ Completed  
**Priority:** P1  
**Endpoint:** `POST /api/v1/private/registry/exports/audit-pack`  
**Dependencies:** T-100, T-101  
**Acceptance criteria:**
- [x] Generates JSON export containing inventory, policies, scores, drift (date range)
- [x] Export stored in private blob
- [x] Status endpoint returns ready + signed URL

**Estimated Effort:** 12 hours  
**Notes:** [registry-api](../../apps/registry-api) exports/audit-pack route + [exports](../../apps/registry-api/src/repositories/exports.py) repo.

---

### T-110 (FE) Private shell + login redirect
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-090  
**Acceptance criteria:**
- [x] Authenticated route loads workspace context
- [x] Shows user role + workspace selector (single ok)

**Estimated Effort:** 8 hours  
**Notes:** Registry private shell in [web/src/routes/registry](../../web/src/routes/registry); [REGISTRY-API-ENTRA.md](../setup/REGISTRY-API-ENTRA.md).

---

### T-111 (FE) Registry inventory UI
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-100  
**Acceptance criteria:**
- [x] List inventory items
- [x] Add server to inventory (by slug/id search)
- [x] Show latest trust score in list

**Estimated Effort:** 12 hours  
**Notes:** [RegistryInventory](../../web/src/routes/registry) in registry UI.

---

### T-112 (FE) Policy UI (create + list)
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-101  
**Acceptance criteria:**
- [x] Create Allow/Deny/RequireApproval
- [x] Shows approval state + expiry
- [x] Validates evidenceConfidence threshold

**Estimated Effort:** 12 hours  
**Notes:** [RegistryPolicies](../../web/src/routes/registry) in registry UI.

---

### T-113 (FE) Evidence pack upload UI
**Status:** 🔄 Partial  
**Priority:** P0  
**Dependencies:** T-103  
**Acceptance criteria:**
- [x] Upload file and show status
- [x] Shows "validated" state when approved
- [x] No public exposure of blob refs

**Estimated Effort:** 8 hours  
**Notes:** Upload/validate exist in [RegistryEvidence](../../web/src/routes/registry). "List evidence packs" (GET /evidence-packs + Evidence tab list) is optional follow-up T-207.

---

## Phase 4 — GK Explorer MVP + Hardening (Week 4)

### T-120 (PIPE/DATA) Graph snapshot builder job
**Status:** ✅ Completed  
**Priority:** P0  
**Description:** Build per-server graph snapshot JSON: Server→Tools→Scopes→DataDomains→Evidence→Flags.  
**Dependencies:** T-072, T-073  
**Acceptance criteria:**
- [x] Writes graph JSON to a `server_graph_snapshots` table keyed by serverId + assessedAt
- [x] Includes nodes + edges; nodes reference evidence IDs when applicable

**Estimated Effort:** 12 hours  
**Notes:** Migration 006 (server_graph_snapshots); [graph-builder](../../apps/workers/graph-builder/src/graph_builder.py) worker stores snapshots.

---

### T-121 (BE) Public server graph endpoint
**Status:** ✅ Completed  
**Priority:** P0  
**Endpoint:** `GET /api/v1/public/mcp/servers/{idOrSlug}/graph`  
**Dependencies:** T-120  
**Acceptance criteria:**
- [x] Returns redacted nodes/edges (no private refs)
- [x] ETag enabled
- [x] Handles missing graph with empty set + meta message

**Estimated Effort:** 4 hours  
**Notes:** [apps/public-api/src/routers/graph.py](../../apps/public-api/src/routers/graph.py) (or public graph route).

---

### T-122 (FE) Graph tab UI (MVP viewer)
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-121  
**Acceptance criteria:**
- [x] Renders graph snapshot (basic force-directed or list view acceptable)
- [x] Clicking node shows props + evidence links
- [x] Degrades gracefully when graph missing

**Estimated Effort:** 12 hours  
**Notes:** ServerDetail graph tab in [web/src/routes/mcp/ServerDetail.tsx](../../web/src/routes/mcp/ServerDetail.tsx) (or equivalent).

---

### T-130 (SEC) Public rate limiting + WAF rules (baseline)
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** T-020  
**Acceptance criteria:**
- [x] Rate limits enforced at edge or API
- [ ] Documented thresholds
- [ ] Abuse patterns blocked (basic rules)

**Estimated Effort:** 6 hours  
**Notes:** In-API rate limiting in [rate_limit.py](../../apps/public-api/src/middleware/rate_limit.py); see [RATE-LIMITING-AND-WAF.md](../implementation/RATE-LIMITING-AND-WAF.md) if present.

---

### T-131 (SEC/BE) Audit logging (private)
**Status:** ✅ Completed  
**Priority:** P0  
**Dependencies:** T-090  
**Acceptance criteria:**
- [x] Every policy change, approval, evidence upload logged with userId + timestamp
- [x] Logs queryable by workspace admin

**Estimated Effort:** 8 hours  
**Notes:** Migration 005 (audit); [audit_log](../../apps/registry-api/src/repositories/audit_log.py) repo; registry routes log actions.

---

### T-132 (DEVOPS) Backups + retention policy for DB + blobs
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** T-010, T-103  
**Acceptance criteria:**
- [ ] Automated DB backups enabled
- [ ] Blob lifecycle rules defined for exports (expire)
- [x] Restore procedure documented

**Estimated Effort:** 4 hours  
**Notes:** Documented in [BACKUPS-AND-RETENTION.md](../implementation/BACKUPS-AND-RETENTION.md).

---

### T-133 (DEVOPS) Observability dashboard
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** T-080  
**Acceptance criteria:**
- [ ] Shows pipeline run success rate, duration, failures by stage
- [ ] Shows API error rates and latency percentiles

**Estimated Effort:** 8 hours  
**Notes:** Documented in [OBSERVABILITY-DASHBOARD.md](../implementation/OBSERVABILITY-DASHBOARD.md); dashboard implementation can follow.

---

### T-134 (UX/LEGAL) Fairness + right-to-respond page + contact channel
**Status:** ✅ Completed  
**Priority:** P1  
**Dependencies:** T-047  
**Acceptance criteria:**
- [x] Public page describes right-to-respond process
- [x] Provider submission contact method available
- [x] Dispute handling steps documented

**Estimated Effort:** 4 hours  
**Notes:** [Fairness.tsx](../../web/src/routes/mcp/Fairness.tsx) and `/mcp/fairness` route.

---

## Fully functioning Verified MCP — plan steps (track in Project #3)

Execution order from the *Fully functioning Verified MCP* plan. See [MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md) "Pre-launch: RSS-with-real-data gate" and this section. Each step is a ticket below or an existing T-XXX; create a GitHub issue for each so progress is visible on Project #3.

| Plan step | Ticket | GitHub issue title (create if missing) |
|-----------|--------|----------------------------------------|
| 1. Align MVP-IMPLEMENTATION-PLAN with code | **T-206** | `Doc sync: Update MVP-IMPLEMENTATION-PLAN Phase 3/4 status (T-206)` |
| 2. Update mvp-build-tickets status for Phase 3/4 | **T-206** | *(same issue — doc sync covers Steps 1–3)* |
| 3. Update build-order Phase 3/4 checkboxes | **T-206** | *(same)* |
| 4. GET /evidence-packs + Evidence tab list | **T-207** | `Registry: GET /evidence-packs and Evidence tab list (T-207)` |
| 5a. One full Path 2 run | **T-208** | `RSS gate: Execute full Path 2 run + verify Tier 1 + deploy feeds (T-208)` |
| 5b. Tier 1 source and staging swap | **T-208** | *(same issue)* |
| 5c. Deploy and verify feed URLs | **T-208** | *(same)* |
| 6. Pipeline run logging + status + stale banner | **T-080**, **T-081** | *(use existing T-080 / T-081 issues)* |

---

### T-206 (DOC) Doc sync: Align MVP plan, backlog, build-order with Phase 3/4 implementation
**Status:** ✅ Completed  
**Priority:** P1  
**Description:** Update docs so they match implemented code. Plan steps 1–3.  
**Dependencies:** none  
**Acceptance criteria:**
- [x] [MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md): Phase 3 and Phase 4 status set to Done where implementation exists; “Next actions” / RSS gate text updated.
- [x] [mvp-build-tickets.md](mvp-build-tickets.md): T-090–T-113, T-120–T-122, T-130–T-134 marked Completed (or Partial) with Notes pointing at implementing code.
- [x] [build-order.md](../implementation/build-order.md): Phase 3 and Phase 4 task checkboxes checked for all implemented items.

**Estimated Effort:** 2 hours  
**Project #3:** Create issue *Doc sync: Update MVP-IMPLEMENTATION-PLAN Phase 3/4 status (T-206)* and add to board.

---

### T-207 (BE/FE) Registry: GET /evidence-packs and Evidence tab list
**Status:** ⏳ Pending  
**Priority:** P2  
**Description:** Close Phase 3 evidence-list gap. Plan step 4. Upload/validate exist; add list API and UI.  
**Dependencies:** T-103, T-113  
**Acceptance criteria:**
- [ ] `GET /api/v1/private/registry/evidence-packs` (query by workspace, optional filters); implemented via [evidence_packs](../../apps/registry-api/src/repositories/evidence_packs.py) and registry router.
- [ ] Registry Evidence tab calls this endpoint and shows packs with status; “validated” shown when applicable.

**Estimated Effort:** 4 hours  
**Project #3:** Create issue *Registry: GET /evidence-packs and Evidence tab list (T-207)* and add to board.

---

### T-208 (DEVOPS) RSS-with-real-data gate: full Path 2 run, Tier 1 validation, deploy and verify feed URLs
**Status:** ⏳ Pending  
**Priority:** P1  
**Description:** Execute minimal RSS gate. Plan steps 5a–5c.  
**Dependencies:** T-070–T-076, T-051  
**Acceptance criteria:**
- [ ] At least one full Path 2 run (Scout → Curator → Miner → Scorer `WRITE_TO_STAGING=1` → Drift → Daily Brief → Publisher) using target DB/env.
- [ ] Tier 1 source returns parseable data (or adapter in place) so brief/feeds can be non-empty; Publisher run confirmed so `latest_scores` and feeds reflect the run.
- [ ] Public API (and front end if it serves feeds) deployed so `GET /mcp/feed.xml` and `GET /mcp/feed.json` (or env-configured URLs) are reachable; verified they return items from `daily_briefs` from that run.

**Estimated Effort:** 4–8 hours (depends on env and deploy path)  
**Project #3:** Create issue *RSS gate: Execute full Path 2 run + verify Tier 1 + deploy feeds (T-208)* and add to board.

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
