# Real MCPs in Rankings — Challenges, Accomplishments, and Research

**Purpose:** Support research and implementation work to populate SecAI Radar rankings with **real** MCP servers (not just seed data). This document records what we have accomplished, what’s blocking us, and what’s needed to reach the goal.

**Last updated:** 2026-01-26  
**Source inventory:** Based on ctxeco ingestion router research (see `mcp_endpoint_sources_report.md`)

---

## 1. Goal

**Objective:** Rankings (and RSS/JSON feeds, server detail pages, daily brief, drift) should be populated from **live discovery** of MCP servers, not only from seed data or manually inserted rows.

**Success looks like:** Running the Path 2 pipeline (Scout → Curator → … → Publisher) yields **new** raw observations from a Tier 1 source, which Curator turns into canonical `mcp_servers`, then Evidence Miner / Scorer / Drift / Publisher use that data so rankings and feeds reflect real, discovered MCPs.

---

## 2. What We Have Accomplished

### 2.1 End-to-end pipeline and automation

- **Path 2 script:** `scripts/run-full-path2.sh` runs, in order:
  - Scout → Curator → Evidence Miner → Scorer (`WRITE_TO_STAGING=1`) → Drift Sentinel → Daily Brief → Publisher.
- **Pipeline run tracking (T-080):** Start/finish recorded in `pipeline_runs`; failed runs marked on script exit.
- **Status and staleness (T-081):** Public API exposes `lastSuccessfulRun`; public web shows a stale-data banner when the last successful run is older than 24 hours or missing.

### 2.2 Data flow and schema

- **Scout** writes to `raw_observations` (observation_id, source_url, content_json, content_hash, retrieved_at, processed_at).
- **Curator** reads unprocessed `raw_observations`, parses `content_json`, deduplicates using canonical server IDs (repo_url → endpoint host → docs URL → name+source), and writes to `mcp_servers`.
- **Evidence Miner, Scorer, Drift, Daily Brief, Publisher** consume `mcp_servers` and related tables; rankings and feeds are driven by this data.
- **Seed data:** `seed.py --refresh` and existing DB rows currently supply the servers visible in rankings when Scout brings in no new observations.

### 2.3 Scout’s Tier 1 configuration

- **Code:** `apps/workers/scout/src/scout.py`
- **Tier 1 sources:** `TIER1_SOURCES = ["https://modelcontextprotocol.io/servers"]`
- **Fetch behavior:** `fetch_source()` performs a GET, treats response as JSON when `Content-Type` is `application/json`, and accepts:
  - a **top-level array** of items, or
  - an **object** with a `"servers"` or `"items"` key whose value is the list.
- Each element of that list is stored as one raw observation (one JSON object per row in `raw_observations`).

### 2.4 Curator’s expected raw-observation shape

Curator’s `dedupe_servers()` (and thus the rest of the pipeline) expects each raw observation to support these fields, with the given fallbacks:

| Conceptual field | Keys used in raw observation   | Purpose |
|------------------|--------------------------------|---------|
| Repository URL   | `repo_url` or `repository`     | Canonical ID precedence; stored on `mcp_servers` |
| Endpoint / URL   | `endpoint` or `url`            | Canonical ID fallback; not yet stored on canonical record |
| Documentation    | `docs_url` or `documentation`  | Canonical ID fallback; stored on `mcp_servers` |
| Name             | `name` or `server_name`        | Display name; default `"Unknown"` |
| Source           | `source_url`                   | Set by Curator from `raw_observations.source_url` (not from JSON) |

So for every **item** in the list returned by the Tier 1 source, we need at least **name**-like data; **repo_url** and/or **endpoint** and/or **docs_url** improve deduplication and usefulness.

### 2.5 Verified MCP and docs alignment

- MVP plan (Phases 3–4), build-order, and backlog tickets are aligned with “Fully functioning Verified MCP” and the RSS-with-real-data gate.
- Pre-launch gate explicitly calls out: *Tier 1 source returns parseable data (e.g. `https://modelcontextprotocol.io/servers` or adapter in place).*

### 2.6 Discovered MCP endpoint sources (from ctxeco research)

We have an inventory of **known, working sources** from previous ctxeco ingestion router work. These are ready to implement:

#### Tier 0: Official MCP Registry (Primary source)

- **API Base:** `https://registry.modelcontextprotocol.io/v0.1/`
- **Endpoints:**
  - List/search: `GET /servers?search=<term>&limit=<n>&cursor=<token>`
  - Latest version: `GET /servers/{serverName}/versions/latest`
  - Specific version: `GET /servers/{serverName}/versions/{serverVersion}`
- **Data format:** Returns `server.json` objects with:
  - `remotes[]` array: `{transport, url}` for remote endpoints
  - `packages[]` array: `{registry/type, identifier, version, run command/args/env}` for local servers
  - Standard fields: `name`, `publisher`, `description`, `repo_url`, `docs_url`, etc.
- **Status:** **v0.1 API freeze** — stable, programmatic, canonical source.

#### Tier 1: High-value public directories (JSON APIs)

1. **MCPAnvil** (`https://mcpanvil.com/api/v1/`)
   - All servers: `GET /all.json`
   - Index: `GET /index.json`
   - Categories: `GET /categories/{name}.json`
   - Single record: `GET /mcp/{id}.json`

2. **Glama MCP Directory**
   - Per-server: `/api/mcp/v1/servers/{owner}/{repo}`
   - Also provides an MCP server package for agent-based discovery

3. **PulseMCP Sub-Registry**
   - Implements Generic MCP Registry API spec
   - Partner-gated (contact required)

#### Tier 2–5: Additional sources (for future enrichment)

- Tier 2: Scraper-friendly directories (mcp.so, mcpservers.org, mcptop.art, unlockmcp.com, smithery.ai, mcpbundles.com)
- Tier 3: Package registries (npm, PyPI, NuGet, Docker Hub/GHCR, GitHub Releases)
- Tier 4: Source code search (GitHub/GitLab for `server.json`, `manifest.json`, MCP config blocks)
- Tier 5: Vendor docs and platform catalogs (OpenAI Agents SDK examples, enterprise catalogs)

**Reference:** Full details in `mcp_endpoint_sources_report.md` (ctxeco ingestion router research).

---

## 3. Challenges (Blockers for Real MCPs)

### 3.1 Tier 1 URL does not supply usable JSON

- **Configured URL:** `https://modelcontextprotocol.io/servers`
- **Observed behavior:** A request to this URL does **not** reliably return JSON in the shape Scout expects (top-level array or `{ "servers" | "items": […] }`). It may return HTML, a different JSON schema, or be unreachable in some environments.
- **Result:** Scout’s `fetch_source()` returns an empty list; **0 new observations** are stored; Curator has nothing new to process; rankings stay on seed + existing DB rows only.

### 3.2 ~~No confirmed “official” machine-readable registry~~ ✅ RESOLVED

- ✅ **Official MCP Registry API exists:** `https://registry.modelcontextprotocol.io/v0.1/servers` (v0.1 API freeze)
- ✅ **Additional Tier 1 sources identified:** MCPAnvil, Glama, PulseMCP (see §2.6)
- **Remaining work:** Implement adapter/normalizer to map Official Registry `server.json` response to Curator’s expected fields (see §4.1.1).

### 3.3 Schema and field mapping needs implementation

- We have **known sources** (Official Registry, MCPAnvil, etc.) but need to **implement** the field mapping from their schemas to Curator’s contract.
- **Official Registry mapping needed:**
  - `server.json` fields → Curator keys (`repo_url`/`repository`, `endpoint`/`url`, `docs_url`/`documentation`, `name`/`server_name`)
  - Handle `remotes[]` array (extract `url` as `endpoint`/`url`)
  - Handle `packages[]` array (extract repo/identifier info)
- **MCPAnvil/Glama mapping:** Schema inspection needed to define exact mapping.

### 3.4 Single code path in Scout

- Scout currently has **one** ingest path: fetch URL → parse as JSON → extract list → store each element as `content_json`.
- There is **no adapter** that:
  - consumes HTML, or
  - consumes a different JSON shape, or
  - calls the GitHub API and normalizes the response into our list-of-objects format.
- So we are blocked until we either get a Tier 1 URL that already matches our contract or add an adapter that produces it.

---

## 4. What We Need to Reach Real MCPs

### 4.1 Functional Tier 1 input (Implementation options)

We have **known sources** (see §2.6). Choose one or more to implement:

#### 4.1.1 Official MCP Registry (Recommended — Tier 0)

**Implementation approach:**
- **Option A (Simple):** Use list endpoint `GET https://registry.modelcontextprotocol.io/v0.1/servers` (with pagination via `cursor` if needed).
- **Option B (Complete):** Fetch each server’s latest version to get full `server.json` with `remotes[]` and `packages[]`.

**Field mapping (server.json → Curator):**
- `name` → `name` / `server_name`
- `repo_url` (or `repository` from metadata) → `repo_url` / `repository`
- `remotes[].url` (first remote) → `endpoint` / `url`
- `docs_url` (or `documentation`) → `docs_url` / `documentation`
- `publisher` → store as `publisher` (may need new field or metadata)

**Adapter needed:** Normalize `server.json` response into list of objects with Curator keys. Handle pagination if using list endpoint.

#### 4.1.2 MCPAnvil (Tier 1 — Simple JSON API)

**Implementation:**
- Use `GET https://mcpanvil.com/api/v1/all.json` (or `/index.json` for lightweight).
- **Schema inspection needed:** Fetch a sample response to map fields to Curator contract.

**Likely mapping:**
- MCPAnvil fields → `name`, `repo_url`, `endpoint`, `docs_url` (exact keys TBD after inspection).

#### 4.1.3 Multi-source adapter pattern

- Implement **source-specific adapters** in Scout (e.g. `scout/sources/registry.py`, `scout/sources/mcpanvil.py`).
- Each adapter:
  - Fetches from its source URL/API
  - Normalizes response into list of objects with Curator keys
  - Returns list to Scout’s `store_raw_observation()` loop
- Scout calls adapters based on `TIER1_SOURCES` configuration.

### 4.2 Documented schema and mapping

- For whichever source we use:
  - Document the **real** response schema (or page structure, if HTML).
  - Define the **field mapping** from source fields to `repo_url` / `repository` / `endpoint` / `url` / `docs_url` / `documentation` / `name` / `server_name`.
- This can live in this doc or in `apps/workers/scout/README.md` (or a small `TIER1-SOURCES.md`).

### 4.3 Validation that the pipeline fills rankings

- After Tier 1 (or adapter) is in place:
  - Run `./scripts/run-full-path2.sh`.
  - Confirm Scout stores **> 0** new raw observations when the source has new/changed data.
  - Confirm Curator creates/updates canonical `mcp_servers`.
  - Confirm rankings and feeds (`/mcp/feed.xml`, `/mcp/feed.json`) reflect those servers.

---

## 5. Research Tasks (For Someone Doing the Research)

Use the list below to drive discovery and design.

### 5.1 ✅ Official Registry API — Schema inspection and mapping

- [x] **Source identified:** `https://registry.modelcontextprotocol.io/v0.1/servers` (v0.1 API)
- [ ] **Fetch sample response:**
  - Test `GET /servers?limit=5` (or similar) to see list response shape.
  - Test `GET /servers/{serverName}/versions/latest` for full `server.json` structure.
- [ ] **Document schema:**
  - List endpoint: top-level shape, pagination (`cursor`), item structure.
  - `server.json`: all fields, `remotes[]` structure, `packages[]` structure.
- [ ] **Define field mapping:** Create mapping table (Official Registry field → Curator key) based on §4.1.1.

### 5.2 MCPAnvil API — Schema inspection

- [ ] **Fetch sample:** `GET https://mcpanvil.com/api/v1/all.json` (or `/index.json`)
- [ ] **Document schema:** Top-level shape, item structure, available fields.
- [ ] **Define field mapping:** MCPAnvil field → Curator key (see §2.4).

### 5.3 Glama and PulseMCP — Schema inspection (optional)

- [ ] **Glama:** Test `/api/mcp/v1/servers/{owner}/{repo}` endpoint structure.
- [ ] **PulseMCP:** If access available, document API shape and mapping.

### 5.4 Implement Official Registry adapter (Priority 1)

- [ ] **Choose implementation approach:** Option A (list endpoint) or Option B (per-server latest version) from §4.1.1.
- [ ] **Create adapter module:** `apps/workers/scout/src/sources/registry.py` (or similar).
  - Function: `fetch_registry_servers()` → returns list of normalized objects.
  - Handles pagination if using list endpoint.
  - Maps `server.json` fields to Curator keys (see §4.1.1 mapping).
- [ ] **Update Scout:** Modify `scout.py` to call registry adapter when `TIER1_SOURCES` includes registry URL.
- [ ] **Test:** Run Scout standalone, verify raw observations stored with correct field mapping.

### 5.5 Implement MCPAnvil adapter (Priority 2 — optional)

- [ ] After schema inspection (§5.2), create `scout/sources/mcpanvil.py`.
- [ ] Map MCPAnvil fields to Curator keys.
- [ ] Add to `TIER1_SOURCES` and test.

### 5.6 Multi-source architecture (if implementing multiple sources)

- [ ] **Refactor Scout:** Support source-specific adapters (registry, mcpanvil, etc.).
- [ ] **Configuration:** `TIER1_SOURCES` can specify source type or auto-detect from URL pattern.
- [ ] **Error handling:** Per-source error isolation (one source fails, others continue).

---

## 6. Quick Reference

| Item | Location |
|------|----------|
| Tier 1 URL config | `apps/workers/scout/src/scout.py` → `TIER1_SOURCES` |
| Scout fetch + parse | `apps/workers/scout/src/scout.py` → `fetch_source()` |
| Curator field contract | `apps/workers/curator/src/curator.py` → `dedupe_servers()` (e.g. `repo_url`/`repository`, `endpoint`/`url`, `docs_url`/`documentation`, `name`/`server_name`) |
| Full Path 2 run | `./scripts/run-full-path2.sh` (from repo root) |
| Pre-launch gate (Tier 1) | `docs/implementation/MVP-IMPLEMENTATION-PLAN.md` — “Tier 1 source returns parseable data…” |
| Raw observations schema | `apps/public-api/migrations/002_raw_observations.sql` |

---

## 8. References and External Sources

### 8.1 Source inventory report

- **ctxeco ingestion router research:** `mcp_endpoint_sources_report.md` (January 26, 2026)
  - Comprehensive inventory of Tier 0–5 sources
  - Canonical data model recommendations
  - Collection pipeline blueprint
  - Operational and security notes

### 8.2 Official MCP Registry

- **Registry API:** `https://registry.modelcontextprotocol.io/`
- **API docs:** v0.1 endpoints (see §2.6)
- **Open-source repo:** `https://github.com/modelcontextprotocol/registry`
- **server.json schema:** `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`
- **GitHub Copilot integration docs:** `https://docs.github.com/en/copilot/using-github-copilot/extending-github-copilot-chat-with-mcp/configure-mcp-registry-access`

### 8.3 Tier 1 directory APIs

- **MCPAnvil:** `https://mcpanvil.com/` (see `/api/v1/*` feeds)
- **PulseMCP API:** `https://www.pulsemcp.com/api`
- **Glama MCP Directory:** Per-server endpoints under `/api/mcp/v1/servers/{owner}/{repo}`

### 8.4 Additional resources

- **OpenAI Agents SDK MCP guides:**
  - JavaScript: `https://openai.github.io/openai-agents-js/guides/mcp/`
  - Python: `https://openai.github.io/openai-agents-python/mcp/`
- **MCP Bundles (MCPB) spec:** `https://github.com/modelcontextprotocol/mcpb`

---

## 7. Summary

- **Done:** End-to-end pipeline, Scout/Curator data contract, Tier 1 placeholder URL, run script, status/staleness, seed + DB-backed rankings. **✅ Sources identified** (Official Registry, MCPAnvil, Glama, PulseMCP).
- **Blocker:** No adapter implemented yet to normalize Official Registry (or other Tier 1) responses into Curator’s expected field shape. Scout’s current `fetch_source()` expects a simple list/object, but Official Registry returns `server.json` objects with nested `remotes[]`/`packages[]`.
- **Goal:** Implement Official Registry adapter (Priority 1) that maps `server.json` → Curator fields, then optionally add MCPAnvil adapter. Re-run Path 2 pipeline to validate real MCPs flow into rankings and feeds.
- **Next steps:**
  1. **Schema inspection (§5.1):** Fetch sample Official Registry responses, document exact schema.
  2. **Field mapping (§4.1.1):** Define `server.json` → Curator key mapping (name, repo_url, endpoint from remotes[], docs_url).
  3. **Implementation (§5.4):** Create `scout/sources/registry.py` adapter, update Scout to use it, test with real API calls.
  4. **Validation (§4.3):** Run full Path 2, confirm > 0 new observations, verify rankings/feeds update.
