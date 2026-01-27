# Pipeline Monitoring and Progress Checking

## Overview

The SecAI Radar pipeline runs daily to discover, analyze, and rank MCP servers. This document explains how to check if the pipeline is running and monitor its progress.

## Pipeline Execution Methods

### 1. GitHub Actions (Current)

**Location:** `.github/workflows/daily-pipeline.yml`

**Schedule:** Daily at 02:30 UTC (can be manually triggered)

**How to check:**
- Go to: https://github.com/zimaxnet/secai-radar/actions
- Look for "Daily Pipeline" workflow runs
- Click on a run to see individual job status (Scout, Curator, Evidence Miner, etc.)

**Manual trigger:**
- Go to Actions → Daily Pipeline → "Run workflow"

### 2. Azure Container Apps Jobs (Planned)

**Location:** `infra/mcp-infrastructure.bicep` (lines 279-318)

**Status:** Infrastructure code exists but may not be deployed yet

**If deployed, check via Azure CLI:**
```bash
# List Container Apps Jobs
az containerapp job list --resource-group secai-radar-rg

# Check job execution history
az containerapp job execution list \
  --name secai-radar-prod-scout \
  --resource-group secai-radar-rg

# View job logs
az containerapp job logs show \
  --name secai-radar-prod-scout \
  --resource-group secai-radar-rg \
  --follow
```

### 3. Manual Local Execution

**Script:** `./scripts/run-full-path2.sh`

**Runs from:** Your local machine or a server with database access

**Records to:** `pipeline_runs` table in database

## Checking Pipeline Progress

### Method 1: Status Endpoint (Current Run + Last Success)

**Endpoint:** `GET /api/v1/public/status`

**Response:**
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

**Usage:**
```bash
curl https://secairadar.cloud/api/v1/public/status
```

### Method 2: Pipeline Runs Endpoint (History)

**Endpoint:** `GET /api/v1/public/pipeline/runs?limit=10&status=Running`

**Response:**
```json
{
  "runs": [
    {
      "runId": "3181791539614d8390d1584750b8480c",
      "date": "2026-01-26",
      "status": "Running",
      "startedAt": "2026-01-27T04:02:23.947307+00:00",
      "completedAt": null,
      "stages": [],
      "deliverables": {},
      "errors": []
    }
  ],
  "count": 1
}
```

**Usage:**
```bash
# Get recent runs
curl https://secairadar.cloud/api/v1/public/pipeline/runs?limit=5

# Get only running pipelines
curl https://secairadar.cloud/api/v1/public/pipeline/runs?status=Running

# Get specific run details
curl https://secairadar.cloud/api/v1/public/pipeline/runs/{run_id}
```

### Method 3: Direct Database Query

**Table:** `pipeline_runs`

**Query:**
```sql
-- Current running pipeline
SELECT run_id, status, started_at, stages_json, errors_json
FROM pipeline_runs
WHERE status IN ('Running', 'running')
ORDER BY started_at DESC
LIMIT 1;

-- Recent runs
SELECT run_id, status, started_at, completed_at
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 10;

-- Last successful run
SELECT completed_at
FROM pipeline_runs
WHERE status IN ('Completed', 'success')
ORDER BY completed_at DESC
LIMIT 1;
```

## Pipeline Stages

The pipeline runs in this order:

1. **Scout** (T-070) - Fetches from Official Registry
2. **Curator** (T-071) - Normalizes and deduplicates
3. **Evidence Miner** (T-072) - Extracts claims and popularity signals
4. **Scorer** (T-073) - Calculates trust scores
5. **Drift Sentinel** (T-074) - Detects changes
6. **Daily Brief** (T-075) - Generates narrative
7. **Publisher** (T-076) - Updates rankings and feeds

**Expected duration:** ~5-10 minutes for 100 servers

## Troubleshooting

### "Data may be outdated. Last pipeline run: never."

**Causes:**
1. Pipeline has never run successfully
2. `pipeline_runs` table is empty
3. Status endpoint query is failing

**Solutions:**
1. Check if pipeline_runs table exists: Run migration `007_pipeline_runs.sql`
2. Manually trigger a run: `./scripts/run-full-path2.sh`
3. Check GitHub Actions: https://github.com/zimaxnet/secai-radar/actions
4. Verify DATABASE_URL is set correctly

### Pipeline Stuck in "Running" Status

**Check:**
1. Query `pipeline_runs` for runs with `status = 'Running'` and `started_at` > 1 hour ago
2. Check GitHub Actions logs for the specific job
3. Check database for evidence of progress (new raw_observations, mcp_servers, etc.)

**Fix:**
- Manually mark as failed: Update `pipeline_runs` SET `status = 'Failed'` WHERE `run_id = '...'`
- Or let it complete naturally

### No Data in Rankings

**Check:**
1. Verify Scout stored observations: `SELECT COUNT(*) FROM raw_observations`
2. Verify Curator created servers: `SELECT COUNT(*) FROM mcp_servers`
3. Verify Scorer created scores: `SELECT COUNT(*) FROM score_snapshots`
4. Check Publisher logs for staging validation errors

## Monitoring Best Practices

1. **Set up alerts** for:
   - No successful run in 25+ hours
   - Pipeline failures
   - Stuck runs (>1 hour in Running status)

2. **Regular checks:**
   - Daily: Verify lastSuccessfulRun is within 24h
   - Weekly: Review pipeline_runs for error patterns
   - Monthly: Check GitHub Actions workflow success rate

3. **Logs:**
   - GitHub Actions: Full logs for each job
   - Database: `pipeline_runs.errors_json` contains error details
   - Application Insights: If configured, check for exceptions

## Quick Status Check

```bash
# Check status endpoint
curl https://secairadar.cloud/api/v1/public/status | jq

# Check recent runs
curl https://secairadar.cloud/api/v1/public/pipeline/runs?limit=3 | jq

# Check if pipeline is currently running
curl https://secairadar.cloud/api/v1/public/pipeline/runs?status=Running | jq
```
