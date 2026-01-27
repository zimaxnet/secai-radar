# SecAI Radar — MVP Implementation Plan

**Last updated:** 2026-01-23  
**Status legend:** Done | In progress | Not started

## Purpose and scope

This document is the **single source of truth** for MVP scope (Phases 0–4), definition of done, and "what's next." Use it to see current status at a glance.

- **Task-level checklists:** [build-order.md](build-order.md)
- **Pipeline and agents:** [automation-blueprint.md](../automation/automation-blueprint.md)
- **T-XXX backlog and acceptance criteria:** [mvp-build-tickets.md](../backlog/mvp-build-tickets.md)

---

## Phases and status

### Phase 0 – Foundation

| Area | Status | Summary |
|------|--------|---------|
| Monorepo structure, CI/CD, infra templates | **Done** | apps/public-api, public-web, registry-api, workers, packages; .github/workflows |
| Reference | — | build-order Phase 0; backlog T-001–T-004 |

### Phase 1 – Public MVP "Truth Hub"

| Area | Status | Summary |
|------|--------|---------|
| DB schema + migrations | **In progress** | Schema in [database-schema.sql](database-schema.sql) and apps/public-api/migrations/001_initial_schema.sql; migrate.py runs migrations |
| Public API (summary, rankings, server, evidence, drift, daily, feeds) | **Done** | [public.py](../../apps/public-api/src/routers/public.py), [feeds.py](../../apps/public-api/src/services/feeds.py) |
| Attestation/Verified (envelope, integrity digest, Gk-like feeds) | **Done** | [attestation.py](../../apps/public-api/src/constants/attestation.py), [VERIFIED-DEFINITION.md](../VERIFIED-DEFINITION.md) |
| Public web (MCP routes, methodology, daily, rankings, server detail, About, Submit) | **Done** | apps/public-web routes + api |
| Feeds (RSS + JSON) | **Done** | feed.xml, feed.json with provenance/integrity |
| Redaction | **Done** | [redaction.py](../../apps/public-api/src/middleware/redaction.py) |
| Staging swap / ETag | **Done** | T-051: latest_scores_staging, Scorer WRITE_TO_STAGING, Publisher validate+flip; etag in place |
| Rankings DB query + seed | **Done** | T-052, T-053, T-011 done — Path 1 complete; run `seed.py --refresh` after migrate. |
| Reference | — | build-order Phase 1; backlog T-010–T-031, T-040–T-048, T-050–T-053 |

### Phase 2 – Automation pipeline

| Area | Status | Summary |
|------|--------|---------|
| Workers (Scout, Curator, Evidence Miner, Scorer, Drift Sentinel, Sage Meridian, Publisher) | **In progress** | Scaffolds/READMEs and some code in scorer, scout, curator, graph-builder, publisher; no production runs |
| Scoring library | **In progress** | packages/scoring exists |
| Shared types | **Done** | packages/shared |
| Reference | — | build-order Phase 2; backlog T-060–T-062, T-070–T-076, T-080–T-081 |

### Phase 3 – Private Trust Registry

| Area | Status | Summary |
|------|--------|---------|
| Auth, RBAC, registry API, workspace, inventory, policies | **Done** | Migrations 004 (private registry), 005 (audit); [registry-api](../../apps/registry-api): auth (JWKS), RBAC, workspace repo, inventory/policies/evidence_packs/exports/audit_log repos; registry routes (servers, policies, approve/deny, evidence-packs, validate, exports/audit-pack); seed workspace + admin; web: RegistryLayout, RegistryInventory, RegistryPolicies, RegistryEvidence ([registry-api](../../apps/registry-api), [web/src/routes/registry](../../web/src/routes/registry)). Evidence list (GET /evidence-packs + UI) is optional follow-up. |
| Reference | — | build-order Phase 3; backlog T-090–T-113 |

### Phase 4 – Graph + hardening

| Area | Status | Summary |
|------|--------|---------|
| Graph builder / Graph API / hardening | **Done** | Migration 006 (server_graph_snapshots); graph-builder worker stores snapshots; public graph endpoint; ServerDetail graph tab; [rate_limit](../../apps/public-api/src/middleware/rate_limit.py) middleware; [BACKUPS-AND-RETENTION.md](BACKUPS-AND-RETENTION.md), [OBSERVABILITY-DASHBOARD.md](OBSERVABILITY-DASHBOARD.md); [Fairness.tsx](../../web/src/routes/mcp/Fairness.tsx) and `/mcp/fairness` route. |
| Reference | — | build-order Phase 4; backlog T-120–T-122, T-130–T-134 |

---

## Definition of Done (MVP launch)

| Criterion | Status |
|-----------|--------|
| **Public:** /mcp overview + rankings + server pages + daily brief | **Done** |
| **Public:** RSS + JSON feed live | **Done** |
| **Public:** Each server has Trust Score + Evidence Confidence + last assessed | **Done** |
| **Public:** Drift timeline shows at least score/evidence/flag changes | **Done** |
| **Automation:** Daily run completes end-to-end with stable publish | **Not done** |
| **Automation:** Daily brief text generated and stored | **In progress** (stub/brief exists) |
| **Automation:** Outbox drafts created | **Not done** |
| **Private:** Basic workspace + inventory + policy skeleton | **Not done** |

---

## Clear path forward

The following sequences are **execution-order** paths. Dependencies are respected; where multiple tickets can run in parallel, that is noted. Every step is a concrete backlog ticket (or a one-line prerequisite).

### Path 1: Ranked MCP servers (visible in UI) — **Done**

**Goal:** /mcp/rankings and server detail show real rows with Trust Score, tier, evidence confidence.

| Order | Ticket | What it does |
|-------|--------|--------------|
| 1 | **T-011** ✅ | Latest projections — refresh_latest_scores.py + get_latest_score() uses latest_scores. |
| 2 | **T-053** ✅ | Seed script: mcp_servers + score_snapshots — seed.py inserts 4 servers + scores; `--refresh` runs refresh_latest_scores. |
| 3 | **T-052** ✅ | Rankings service: get_rankings() joins mcp_servers + latest_scores + score_snapshots + providers; filters, sort, pagination. |

**Prerequisites (already done):** T-010 (schema + migrations), T-022 (rankings route/envelope). Run migrations and seed before or with step 2.

**Outcome:** Run `migrate.py` then `seed.py --refresh`; rankings API and /mcp/rankings show seeded data. No pipeline yet.

---

### Path 2: Daily pipeline (real discovery and scoring)

**Goal:** Scout → Curator → Evidence Miner → Scorer run so rankings are filled from real MCP sources.

| Order | Ticket | What it does |
|-------|--------|--------------|
| 1 | **T-070** | Scout — discover servers from Tier 1 sources, store raw observations. *(Done: raw_observations table, runnable scout, `./scripts/run-scout.sh`; runbook in apps/public-api/README Path 2.)* |
| 2 | **T-071** | Curator — canonicalize and dedupe into provider/server records. *(Done: ID precedence, review queue log, `./scripts/run-curator.sh`.)* |
| 3 | **T-072** | Evidence Miner — extract claims from docs/repos. *(Done: Docs/Repo items, AuthModel/HostingCustody/ToolCapabilities, `./scripts/run-evidence-miner.sh`.)* |
| 4 | **T-061**, **T-062** | Scoring library + Evidence Confidence. *(Done: deterministic d1–d6 from claims, 0–3 confidence, 9 tests in packages/scoring.)* |
| 5 | **T-073** | Scorer — compute scores, write score_snapshots. *(Done: `./scripts/run-scorer.sh`, score_snapshots + latest_scores.)* |
| 6 | **T-074** | Drift Sentinel — diff and classify changes. *(Done: `./scripts/run-drift-sentinel.sh`, drift_events + topMovers/topDowngrades.)* |
| 7 | **T-075** | Daily Brief generator (Sage Meridian stub). *(Done: `./scripts/run-daily-brief.sh`, template, narrativeShort/Long, daily_briefs.)* |
| 8 | **T-051** | Staging swap — atomic flip so pipeline writes don’t corrupt live data. |
| 9 | **T-076** | Publisher — validation + flip + cache refresh. *(Done: run-publisher.sh, rankings_cache 24h + tier A/B/C/D; feeds use daily_briefs.)* |

**Outcome:** One full run updates servers and scores; rankings reflect pipeline output.

---

### Path 3: Deploy and wire (staging end-to-end)

**Goal:** Public hub and API live in staging, SWA talks to API.

| Order | Step | What to do |
|-------|------|------------|
| 1 | Migrations | Run `apps/public-api/scripts/migrate.py` (set `DATABASE_URL`). |
| 2 | Seed | Run `apps/public-api/scripts/seed.py` (after T-053: servers + scores). |
| 3 | Deploy API | Use deploy-staging workflow (or manual) to deploy public-api Container App. |
| 4 | Wire SWA | Set `VITE_API_BASE` or SWA linked backends; see docs/SWA-STANDARD-AND-CONTAINERS.md. |
| 5 | Smoke test | Load /mcp, /mcp/rankings, a server detail, feed.json. |

---

### Path 4: Private registry (later)

**Goal:** Auth, workspace, inventory, policies, evidence upload.

Order: **T-090** (Entra OIDC) → **T-091** (workspace/membership) → **T-092** (RBAC) → **T-100**–**T-105** (inventory, policies, evidence, approvals, export) → **T-110**–**T-113** (registry UI). Details and acceptance criteria are in [mvp-build-tickets.md](../backlog/mvp-build-tickets.md).

---

### How to use these paths

- **“Get ranked servers now”:** Do Path 1 (T-011 → T-053 → T-052), then Path 3 steps 1–2 and 5.
- **“Full daily refresh”:** Do Path 2 after Path 1; schedule T-070–T-076 + T-051 + T-076 as a daily job.
- **“Ship staging”:** Do Path 3 in order.

All tickets above exist in [mvp-build-tickets.md](../backlog/mvp-build-tickets.md) with dependencies and acceptance criteria. No gaps: Path 1 addresses the rankings-query and seed gaps explicitly (T-052, T-053).

---

### Pre-launch: RSS-with-real-data gate

Phase 3 and Phase 4 implementation is in place. Remaining work for “fully functioning Verified MCP” is: doc sync (done via this plan), optional evidence list (GET /evidence-packs + Evidence tab), then **RSS gate** (one full Path 2 run, Tier 1 source + staging swap, deploy and verify feed URLs) and optional **T-080/T-081** (pipeline run logging, status endpoint, stale banner).

RSS and JSON feeds read from `daily_briefs` only. “Real data” means feed items produced by the pipeline (Daily Brief after Drift), not manual or empty rows.

**Minimal gate (technical):**
- [ ] At least one full Path 2 run: Scout → Curator → Miner → Scorer (`WRITE_TO_STAGING=1`) → Drift → Daily Brief → Publisher.
- [ ] Tier 1 source returns parseable data (e.g. `https://modelcontextprotocol.io/servers` or adapter in place).
- [ ] Staging swap run so `latest_scores` and feeds reflect the run.
- [ ] Feed endpoints reachable: `/mcp/feed.xml`, `/mcp/feed.json` (or env-configured URLs).

**Recommended before broad promotion:**
- [ ] T-080 + T-081: run log per pipeline run; `GET /api/v1/public/status` with last successful run; frontend stale banner when >24h.
- [ ] Feed URLs in [feeds.py](../../apps/public-api/src/services/feeds.py) match the promoted environment (or are configurable).
- [ ] Deploy and wiring so feed URLs are live and status reflects freshness.

Phase 3 and Phase 4 are not prerequisites for RSS content; the gate is pipeline + deploy + optional freshness/trust items.

---

## Next actions

1. **Path 1 done.** Run locally: `migrate.py` → `seed.py --refresh` → start API; see [apps/public-api/README.md](../../apps/public-api/README.md) runbook.
2. **Phase 1 remaining:** T-027 (ETag wired to public routes), T-051 (staging swap), then test end-to-end: seed → API → UI → feeds.
3. **Path 2 (daily pipeline):** T-070–T-076 ✅ complete. Full pipeline: Scout → Curator → Miner → Scorer (WRITE_TO_STAGING=1) → Drift → Brief → Publisher (validate, flip, refresh rankings_cache).
4. **Path 3 (deploy):** Migrations + seed on staging DB, deploy public-api, wire SWA, smoke-test.
5. **Phase 3/4:** Implementation in place (auth, RBAC, workspace, inventory, policies, approvals, evidence upload/validate, audit export, registry UI, graph snapshot/API/tab, rate limiting, backups/observability docs, fairness page). Optional: GET /evidence-packs + Evidence tab list. Then: RSS-with-real-data gate (one full Path 2 run, staging swap, deploy/verify feeds); recommended T-080/T-081 before broad promotion.

---

## References

- [build-order.md](build-order.md) — Phase 0–4 task checkboxes
- [automation-blueprint.md](../automation/automation-blueprint.md) — Daily pipeline runbook, agents, guardrails
- [mvp-build-tickets.md](../backlog/mvp-build-tickets.md) — T-XXX backlog with acceptance criteria
- [GITHUB-PROJECT-SETUP.md](../GITHUB-PROJECT-SETUP.md) — Project #3 setup
- [REFACTORING-PROGRESS.md](../../REFACTORING-PROGRESS.md) — Refactoring and implementation status
