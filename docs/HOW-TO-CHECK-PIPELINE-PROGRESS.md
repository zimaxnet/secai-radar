# How to Check Pipeline Progress on the Server

## Quick Answer

**The pipeline can run in 3 ways:**
1. **GitHub Actions** (scheduled daily at 02:30 UTC) - Check: https://github.com/zimaxnet/secai-radar/actions
2. **Azure Container Apps Jobs** (if deployed) - Check via Azure Portal/CLI
3. **Manual execution** (local/server) - Check via API endpoints or database

## Method 1: Status API Endpoint (Easiest)

**URL:** `https://secairadar.cloud/api/v1/public/status`

**What it shows:**
- `lastSuccessfulRun`: Timestamp of last completed run (or `null` if never)
- `currentRun`: Active pipeline run with status, stages, errors (or `null` if none running)
- `status`: Always "operational"

**Example response:**
```json
{
  "status": "operational",
  "lastSuccessfulRun": "2026-01-27T03:39:26.718222+00:00",
  "currentRun": {
    "runId": "3181791539614d8390d1584750b8480c",
    "status": "Running",
    "startedAt": "2026-01-27T04:02:23.947307+00:00",
    "stages": [],
    "errors": []
  },
  "timestamp": "2026-01-27T04:15:00.000000+00:00"
}
```

**If `lastSuccessfulRun` is `null`:**
- Pipeline has never completed successfully
- Run the pipeline manually: `./scripts/run-full-path2.sh`

## Method 2: Pipeline Runs API Endpoint

**URL:** `https://secairadar.cloud/api/v1/public/pipeline/runs?limit=5`

**What it shows:**
- Recent pipeline runs with full details
- Filter by status: `?status=Running` or `?status=Completed`

**Example:**
```bash
# Get recent runs
curl https://secairadar.cloud/api/v1/public/pipeline/runs?limit=5

# Get only running pipelines
curl https://secairadar.cloud/api/v1/public/pipeline/runs?status=Running

# Get specific run
curl https://secairadar.cloud/api/v1/public/pipeline/runs/{run_id}
```

## Method 3: GitHub Actions (If Using GitHub Workflow)

**URL:** https://github.com/zimaxnet/secai-radar/actions

**What to check:**
1. Look for "Daily Pipeline" workflow
2. Click on the latest run
3. See individual job status:
   - ✅ Scout - Discovery
   - ✅ Curator - Canonicalization
   - ✅ Evidence Miner
   - ✅ Scorer
   - ✅ Drift Sentinel
   - ✅ Sage Meridian
   - ✅ Publisher

**Manual trigger:**
- Actions → Daily Pipeline → "Run workflow" button

## Method 4: Direct Database Query

**If you have database access:**

```sql
-- Current running pipeline
SELECT run_id, status, started_at, stages_json, errors_json
FROM pipeline_runs
WHERE status IN ('Running', 'running')
ORDER BY started_at DESC
LIMIT 1;

-- Last successful run
SELECT run_id, completed_at, status
FROM pipeline_runs
WHERE status IN ('Completed', 'success')
ORDER BY completed_at DESC
LIMIT 1;

-- Recent runs summary
SELECT run_id, status, started_at, completed_at,
       CASE 
         WHEN completed_at IS NOT NULL 
         THEN EXTRACT(EPOCH FROM (completed_at - started_at))
         ELSE NULL
       END as duration_seconds
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 10;
```

## Method 5: Azure Container Apps (If Deployed)

**Check job executions:**
```bash
# List all jobs
az containerapp job list --resource-group secai-radar-rg

# Check Scout job executions
az containerapp job execution list \
  --name secai-radar-prod-scout \
  --resource-group secai-radar-rg \
  --query "[].{name:name, status:properties.status, startTime:properties.startTime}" \
  -o table

# View logs for latest execution
az containerapp job logs show \
  --name secai-radar-prod-scout \
  --resource-group secai-radar-rg \
  --follow
```

## Understanding Pipeline Status

### Status Values

- **`Running`** or **`running`**: Pipeline is currently executing
- **`Completed`** or **`success`**: Pipeline finished successfully
- **`Failed`** or **`failed`**: Pipeline encountered errors
- **`Partial`**: Some stages completed, others failed

### Pipeline Stages

The pipeline runs these stages in order:

1. **Scout** - Fetches servers from Official Registry (takes ~30-60 seconds for 100 servers)
2. **Curator** - Normalizes and deduplicates (takes ~5-10 seconds)
3. **Evidence Miner** - Extracts claims and popularity (takes ~1-2 minutes)
4. **Scorer** - Calculates trust scores (takes ~10-30 seconds)
5. **Drift Sentinel** - Detects changes (takes ~5 seconds)
6. **Daily Brief** - Generates narrative (takes ~5 seconds)
7. **Publisher** - Updates rankings and feeds (takes ~5 seconds)

**Total expected time:** 5-10 minutes for 100 servers

## Troubleshooting "Last pipeline run: never"

### Cause 1: Pipeline Never Ran

**Solution:** Run manually:
```bash
cd secai-radar
./scripts/run-full-path2.sh
```

### Cause 2: Pipeline Runs But Status Not Recorded

**Check:**
1. Is `pipeline_runs` table created? Run migration `007_pipeline_runs.sql`
2. Does `record_pipeline_run.py` have DATABASE_URL? It should auto-detect from Key Vault
3. Check script logs for errors

**Solution:** Fix DATABASE_URL and re-run

### Cause 3: Status Endpoint Query Issue

**Check:** Status endpoint looks for `status IN ('Completed', 'success')`

**Solution:** Verify your `pipeline_runs.status` values match

## Real-Time Monitoring

**For real-time progress, check:**

1. **GitHub Actions logs** (if using GitHub workflow) - Shows live output
2. **Database `pipeline_runs.stages_json`** - Should be populated as stages complete
3. **Database tables:**
   - `raw_observations` - Should grow during Scout
   - `mcp_servers` - Should grow during Curator
   - `evidence_items` - Should grow during Evidence Miner
   - `score_snapshots` - Should grow during Scorer

## Quick Status Check Script

```bash
#!/bin/bash
# Quick pipeline status check

echo "=== Status Endpoint ==="
curl -s https://secairadar.cloud/api/v1/public/status | jq

echo -e "\n=== Recent Runs ==="
curl -s https://secairadar.cloud/api/v1/public/pipeline/runs?limit=3 | jq '.runs[] | {runId, status, startedAt, completedAt}'

echo -e "\n=== Currently Running ==="
curl -s https://secairadar.cloud/api/v1/public/pipeline/runs?status=Running | jq '.runs[] | {runId, status, startedAt}'
```

Save as `check-pipeline-status.sh` and run: `bash check-pipeline-status.sh`
