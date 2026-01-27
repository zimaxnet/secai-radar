# Troubleshooting: Pipeline Runs Successfully But No Rankings

## Problem

The daily pipeline (`./scripts/run-full-path2.sh`) runs successfully, but rankings are empty when accessing `/api/v1/public/mcp/rankings` or the rankings page.

## Root Cause Analysis

Rankings require data to flow through the entire pipeline:

1. **Scout** → `raw_observations` table
2. **Curator** → `mcp_servers` and `providers` tables
3. **Evidence Miner** → `evidence_items` and `evidence_claims` tables
4. **Scorer** → `score_snapshots` and `latest_scores_staging` tables
5. **Publisher** → Flips `latest_scores_staging` → `latest_scores` (stable)

The rankings query joins:
- `mcp_servers` (status = 'Active')
- `latest_scores` (points to latest score per server)
- `score_snapshots` (actual score data)
- `providers` (provider information)

**If any of these tables are empty or the joins fail, rankings will be empty.**

## Most Common Issue: Publisher Not Flipping Staging

The most common cause is that **Publisher isn't flipping staging to stable**. Here's why:

1. Scorer writes to `latest_scores_staging` (when `WRITE_TO_STAGING=1`)
2. Publisher validates staging and flips it to `latest_scores`
3. If validation fails, Publisher keeps the old stable dataset (which may be empty)

### Why Validation Might Fail

Publisher validation checks:
- Staging is not empty
- All active servers have entries in staging
- All staging rows reference valid `score_snapshots`

Common validation failures:
- **"Staging is empty"** → Scorer didn't write to staging (check `WRITE_TO_STAGING=1`)
- **"X active servers missing in staging"** → Scorer didn't score all active servers
- **"X staging rows reference invalid score_snapshots"** → Data integrity issue

## Diagnostic Steps

### Step 1: Run Diagnostic Script

```bash
./scripts/diagnose-rankings.sh
```

This script checks:
- Raw observations count
- MCP servers count
- Providers count
- Score snapshots count
- Staging table status
- Stable table status
- Rankings query test
- Recent pipeline runs

### Step 2: Check Specific Tables

If you have database access, run these queries:

```sql
-- Check raw observations
SELECT COUNT(*) FROM raw_observations;

-- Check active servers
SELECT COUNT(*) FROM mcp_servers WHERE status = 'Active';

-- Check score snapshots
SELECT COUNT(*) FROM score_snapshots;

-- Check staging
SELECT COUNT(*) FROM latest_scores_staging;

-- Check stable
SELECT COUNT(*) FROM latest_scores;

-- Test rankings query
SELECT COUNT(*) 
FROM mcp_servers s
JOIN latest_scores ls ON s.server_id = ls.server_id
JOIN score_snapshots ss ON ls.score_id = ss.score_id
JOIN providers p ON s.provider_id = p.provider_id
WHERE s.status = 'Active';
```

### Step 3: Check Publisher Logs

Run Publisher manually to see validation errors:

```bash
./scripts/run-publisher.sh
```

Look for error messages like:
- "Staging validation failed: ..."
- "Failed to flip stable pointer"
- "X active servers missing in staging"

## Solutions

### Solution 1: Re-run Publisher (Most Common Fix)

If staging has data but stable is empty:

```bash
./scripts/run-publisher.sh
```

This will:
1. Validate staging
2. Flip staging to stable (if validation passes)
3. Refresh rankings cache

### Solution 2: Manual Flip (If Validation Fails Unnecessarily)

If staging has valid data but validation is failing due to edge cases:

```bash
./scripts/manual-flip-staging.sh
```

**WARNING:** This bypasses validation. Only use if you're certain staging data is correct.

### Solution 3: Re-run Scorer

If staging is empty or incomplete:

```bash
WRITE_TO_STAGING=1 ./scripts/run-scorer.sh
```

Then run Publisher:

```bash
./scripts/run-publisher.sh
```

### Solution 4: Re-run Full Pipeline

If data is missing at earlier stages:

```bash
./scripts/run-full-path2.sh
```

This runs:
1. Scout (fetch servers)
2. Curator (normalize and deduplicate)
3. Evidence Miner (extract claims)
4. Scorer (calculate scores with `WRITE_TO_STAGING=1`)
5. Drift Sentinel (detect changes)
6. Daily Brief (generate narrative)
7. Publisher (flip staging and refresh cache)

### Solution 5: Check Scout Data Source

If `raw_observations` is empty, Scout isn't fetching data. Check:

1. **Registry adapter is working:**
   ```bash
   ./scripts/run-scout.sh
   ```
   Look for: "Fetched X servers from Official Registry"

2. **Registry API is accessible:**
   - Test: `curl https://registry.modelcontextprotocol.io/v0.1/servers?limit=5`
   - Should return JSON with server list

3. **Check Scout logs** for errors fetching from registry

## Prevention

### Ensure Pipeline Completes All Stages

The pipeline script (`run-full-path2.sh`) should complete all stages. Check:

1. **Pipeline run tracking:**
   ```bash
   # Check recent runs
   curl https://secairadar.cloud/api/v1/public/pipeline/runs?limit=5
   ```

2. **Status endpoint:**
   ```bash
   curl https://secairadar.cloud/api/v1/public/status
   ```
   Look for `lastSuccessfulRun` timestamp

### Monitor Publisher Validation

Publisher now logs validation errors to stderr. Check logs after each pipeline run to catch validation failures early.

### Verify Rankings After Pipeline

After pipeline completes, verify rankings are populated:

```bash
curl https://secairadar.cloud/api/v1/public/mcp/rankings?pageSize=5
```

Should return non-empty `servers` array.

## Quick Reference

| Issue | Symptom | Fix |
|-------|---------|-----|
| No raw observations | `raw_observations` table empty | Run Scout: `./scripts/run-scout.sh` |
| No servers | `mcp_servers` table empty | Run Curator: `./scripts/run-curator.sh` |
| No scores | `score_snapshots` table empty | Run Scorer: `WRITE_TO_STAGING=1 ./scripts/run-scorer.sh` |
| Staging not flipped | `latest_scores_staging` has data, `latest_scores` empty | Run Publisher: `./scripts/run-publisher.sh` |
| Validation failing | Publisher errors about missing servers/invalid refs | Check Scorer output, re-run Scorer, or use manual flip |

## Related Documentation

- `docs/DIAGNOSE-EMPTY-RANKINGS.md` - Detailed diagnostic queries
- `docs/REAL-MCP-RESEARCH.md` - Information about data sources and adapters
- `docs/HOW-TO-CHECK-PIPELINE-PROGRESS.md` - How to monitor pipeline status
