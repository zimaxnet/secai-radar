# Public API

FastAPI service for public read-only endpoints at secairadar.cloud/api/v1/public/*

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL

## Path 1 runbook (rankings with seeded data)

From repo root `secai-radar/`. **DB access:** see **WORKLOAD-FIXES.md** and **INTEGRATED-WORKSPACE-DATABASE.md** in the workspace root. The shared Azure DB uses Key Vault **secai-radar-kv** secret `database-url`; `run-migrations.sh` reads it when `DATABASE_URL` is unset and `az` is logged in. The shared Azure DB uses **secai-radar-kv** `database-url`; for local runs you can pull it or use the script below.

**Using the shared Azure DB (documented in WORKLOAD-FIXES / INTEGRATED-WORKSPACE-DATABASE):**

```bash
# 1. Apply schema — uses DATABASE_URL from env, or from Key Vault (secai-radar-kv / database-url) when az is logged in
./scripts/run-migrations.sh

# 2. Seed + refresh latest_scores (same DATABASE_URL)
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
python apps/public-api/scripts/seed.py --refresh

# 3. Start API (from apps/public-api, with PYTHONPATH=src and DATABASE_URL)
cd apps/public-api && PYTHONPATH=src uvicorn main:app --reload --port 8000

# 4. Smoke-test: GET /api/v1/public/mcp/rankings, /api/v1/public/mcp/servers/filesystem
```

**Local Postgres only (no Azure):** Step 0 — start a DB matching the default URL, then run steps 1–2 with that URL:

```bash
docker run -d --name secairadar-pg \
  -e POSTGRES_USER=secairadar -e POSTGRES_PASSWORD=password -e POSTGRES_DB=secairadar \
  -p 5432:5432 postgres:16-alpine
# Wait a few seconds, then:
python apps/public-api/scripts/migrate.py
python apps/public-api/scripts/seed.py --refresh
```

(Default `DATABASE_URL` is `postgresql://secairadar:password@localhost:5432/secairadar` when unset.)

Without `--refresh`, run `python apps/public-api/scripts/refresh_latest_scores.py` after seed so rankings and server latest-score use the pointer table.

## Path 2 runbook (daily pipeline — Scout)

From repo root `secai-radar/`. Same DB/Key Vault as Path 1.

**Prerequisite:** `raw_observations` table exists. `./scripts/run-migrations.sh` applies it via `002_raw_observations.sql` (after the main schema). For an already-migrated DB, run only incremental migrations:

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
python apps/public-api/scripts/run_incremental_migrations.py
```

**Run Scout (T-070 discovery ingest):**

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
# Scout needs requests; use API venv or install in scout env
apps/public-api/.venv/bin/pip install -q requests
apps/public-api/.venv/bin/python apps/workers/scout/src/scout.py
```

Or run `./scripts/run-scout.sh` from repo root. Scout writes to `raw_observations` (source_url, content_json, content_hash, retrieved_at); append-only, deduped by content_hash.

**Run Curator (T-071) after Scout** — canonicalize and dedupe into provider/server records:

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
./scripts/run-curator.sh
# or: apps/public-api/.venv/bin/python apps/workers/curator/src/curator.py
```

Curator reads `raw_observations` where `processed_at IS NULL`, produces canonical `mcp_servers` rows (ID precedence: repoUrl &gt; endpoint host &gt; docs URL &gt; name+source), ensures default provider exists, then sets `processed_at`.

**Run Evidence Miner (T-072)** after Curator — docs/repo extraction and minimal claims:

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
./scripts/run-evidence-miner.sh
```

Miner reads `mcp_servers` with `repo_url` or `docs_url`, fetches each URL once per server (skips if evidence exists for that source_url), writes `evidence_items` (Docs/Repo) and `evidence_claims` (AuthModel, HostingCustody, ToolCapabilities) with sourceEvidenceId = evidence_id and capturedAt.

**Run Scorer (T-073)** after Evidence Miner — compute scores and update pointers:

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
./scripts/run-scorer.sh
```

Scorer uses `packages/scoring` (T-061/T-062): reads `evidence_items` and `evidence_claims` per server, computes domain scores d1–d6, trust score, tier, enterprise fit, evidence confidence, flags; writes append-only `score_snapshots` and updates `latest_scores`.

**Run Drift Sentinel (T-074)** after Scorer — detect changes and emit events:

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
./scripts/run-drift-sentinel.sh
```

Compares latest vs previous `score_snapshots` per server; writes `drift_events` (ScoreChanged, FlagChanged, EvidenceAdded, EvidenceRemoved) with severity; returns `topMovers` and `topDowngrades` candidate lists.

**Run Daily Brief (T-075)** after Drift Sentinel — generate and store brief for a date:

```bash
export DATABASE_URL="${DATABASE_URL:-$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv 2>/dev/null)}"
./scripts/run-daily-brief.sh           # today
./scripts/run-daily-brief.sh 2026-01-27   # specific date
```

Reads `drift_events` and first-score `score_snapshots` for that date; builds movers/downgrades/newEntrants/notableDrift; fills template; stores in `daily_briefs`. Next: Publisher.

**Staging swap (T-051)** — Pipeline writes to staging; publisher flips:

- Run Scorer with **`WRITE_TO_STAGING=1`** so it writes to `latest_scores_staging` instead of `latest_scores`.
- Drift Sentinel uses staging as "current" when it has rows.
- After Brief, run **Publisher** to validate and flip: `./scripts/run-publisher.sh`. Validates `latest_scores_staging` then atomically replaces `latest_scores` and refreshes `latest_assessments_view`. On validation or flip failure, stable data is unchanged.

**Full pipeline (staging mode):**
```bash
export DATABASE_URL="..."
WRITE_TO_STAGING=1 ./scripts/run-scorer.sh
./scripts/run-drift-sentinel.sh
./scripts/run-daily-brief.sh
./scripts/run-publisher.sh
```

**One-command Path 2 (RSS-with-real-data gate, plan step 5a/5b):** From repo root, run `./scripts/run-full-path2.sh`. This runs Scout → Curator → Evidence Miner → Scorer (`WRITE_TO_STAGING=1`) → Drift → Daily Brief → Publisher. Tier 1 source is configured in `apps/workers/scout/src/scout.py` (`TIER1_SOURCES`; default `https://modelcontextprotocol.io/servers`). After the run, deploy the public API and verify `GET /mcp/feed.xml` and `GET /mcp/feed.json` (plan step 5c).

**Publisher (T-076)** validates staging, flips `latest_scores`, refreshes **rankings_cache** (window 24h, default + tier A/B/C/D), and returns `rankingsCacheRefreshed`. Feeds read `daily_briefs` by date, so the latest brief is used after the run.

## Development
```bash
uvicorn main:app --reload --port 8000
```

## Endpoints
- `GET /api/v1/public/health` - Health check
- `GET /api/v1/public/mcp/summary` - Overview KPIs
- `GET /api/v1/public/mcp/rankings` - Rankings with filters
- `GET /api/v1/public/mcp/servers/{idOrSlug}` - Server detail
- `GET /api/v1/public/mcp/servers/{idOrSlug}/evidence` - Evidence list
- `GET /api/v1/public/mcp/servers/{idOrSlug}/drift` - Drift timeline
- `GET /api/v1/public/mcp/daily/{date}` - Daily brief
- `GET /mcp/feed.xml` - RSS feed
- `GET /mcp/feed.json` - JSON Feed
