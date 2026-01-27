# SecAI Radar Verified MCP - Backlog Management

This directory contains the MVP build tickets and backlog management documentation.

## Files

- `mvp-build-tickets.md` - Complete backlog of 60+ tickets organized by phase (canonical source)
- `ticket-template.md` - Template for creating new tickets
- `README.md` - This file

**Canonical path forward:** [MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md) — Path 1 (ranked servers), Path 2 (daily pipeline), Path 3 (deploy), Path 4 (private registry).

---

## Clear path forward (execution order)

These sequences have no gaps: every step is a ticket in `mvp-build-tickets.md` or a concrete prerequisite.

### Path to ranked MCP servers (first goal)

| # | Ticket | What it does |
|---|--------|--------------|
| 1 | **T-011** | Latest projections — fast “latest score per server” |
| 2 | **T-053** | Seed script: mcp_servers + score_snapshots — sample data for demos |
| 3 | **T-052** | Rankings service: implement DB query — `get_rankings()` returns real rows |

**Already done:** T-010 (schema), T-022 (rankings route). Run migrations + seed; then rankings UI shows data.

### Path to daily pipeline (real discovery and scoring)

| # | Ticket | What it does |
|---|--------|--------------|
| 1 | T-070 | Scout |
| 2 | T-071 | Curator |
| 3 | T-072 | Evidence Miner |
| 4 | T-061, T-062 | Scoring library + Evidence Confidence (parallel ok) |
| 5 | T-073 | Scorer |
| 6 | T-074 | Drift Sentinel |
| 7 | T-075 | Daily Brief (Sage Meridian stub) |
| 8 | T-051 | Staging swap |
| 9 | T-076 | Publisher |

### Path to private registry

T-090 → T-091 → T-092 → T-100–T-105 → T-110–T-113. See MVP-IMPLEMENTATION-PLAN Path 4 and `mvp-build-tickets.md`.

### Path to fully functioning Verified MCP (plan execution order)

| # | Ticket | What it does |
|---|--------|--------------|
| 1 | **T-206** | Doc sync: Align MVP-IMPLEMENTATION-PLAN, mvp-build-tickets, build-order with Phase 3/4 implementation |
| 2 | **T-207** | (Optional) Registry: GET /evidence-packs and Evidence tab list |
| 3 | **T-208** | RSS-with-real-data gate: full Path 2 run, Tier 1 validation, deploy and verify feed URLs |
| 4 | **T-080, T-081** | Pipeline run logging; status endpoint + stale banner |

**Make these trackable on the board:** run `./scripts/create-plan-step-issues.sh` from the repo root to create T-206, T-207, T-208 and add them to Project #3; ensure T-080 and T-081 are on the project. See [GITHUB-PROJECT-ISSUES-REVIEW.md](GITHUB-PROJECT-ISSUES-REVIEW.md) §0 and §7.

---

## Backlog Organization

### By Phase
- **Phase 0** (Day 1-2): Repo + CI Skeleton (4 tickets)
- **Phase 1** (Week 1): Public MVP "Truth Hub" (24 tickets — includes T-052, T-053)
- **Phase 2** (Week 2): Automation Pipeline MVP (12 tickets)
- **Phase 3** (Week 3): Private Trust Registry MVP (14 tickets)
- **Phase 4** (Week 4): GK Explorer MVP + Hardening (8 tickets)
- **Post-MVP**: Optional nice-to-have tickets (6 tickets)

### By Category
- **FE** (Frontend): 15 tickets
- **BE** (Backend/API): 20 tickets (includes T-052)
- **DATA** (Data/Database): 6 tickets (includes T-053)
- **PIPE** (Pipeline/Agents): 10 tickets
- **SEC** (Security): 5 tickets
- **DEVOPS** (CI/CD/Infra): 7 tickets
- **UX** (Copy/Docs): 2 tickets

---

## Ticket Tracking

### Current Status Summary

**Completed:** 21 tickets (T-004, T-010, T-020–T-026, T-030, T-031, T-040–T-048, T-050, T-060)  
**In Progress / Partial:** 4 tickets (T-027, T-044, T-045, and any in-progress)  
**Pending:** 40+ tickets (including T-011, T-052, T-053, all Phase 2–4)

### Key Completed Tickets
- T-004: Copy system package ✅
- T-010: Postgres schema + migrations ✅
- T-020: Public API skeleton + envelope ✅
- T-021–T-026: Summary, rankings, server, evidence, drift, daily brief ✅
- T-030–T-031: RSS + JSON feed ✅
- T-040–T-048: Public web routes and pages ✅
- T-050: Redaction middleware ✅
- T-060: Shared types + JSON schemas ✅

### New tickets (no gaps)

- **T-052** — Rankings service: implement DB query (makes /rankings return real rows)
- **T-053** — Seed script: mcp_servers + score_snapshots (sample data for demos)

---

## Critical Path (P0 by phase)

**Phase 0:** T-001 → T-002 → T-003 (monorepo, CI, deploy). T-004 done.  
**Phase 1:** T-010 done. Next: T-011, T-052, T-053 (path to ranked servers). Then T-020–T-031, T-040–T-048, T-050–T-051 — most done.  
**Phase 2:** T-060 done. T-061, T-062, T-070–T-076 (path to daily pipeline).  
**Phase 3:** T-090–T-092, T-100–T-105, T-110–T-113.  
**Phase 4:** T-120–T-122, T-131.

---

## Using This Backlog

1. **For “what’s next”:** Use the paths above and [MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md).
2. **For dependencies:** Each ticket lists `Dependencies:` in `mvp-build-tickets.md`.
3. **For planning:** Path to ranked servers = T-011 → T-053 → T-052; path to pipeline = T-070 → … → T-076.
4. **For estimation:** Use estimated effort in each ticket.
