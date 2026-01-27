# Daily Pipeline Readiness Checklist

## Pre-Flight Checks

### ✅ Database
- [x] Migrations applied (including 008_metadata_json.sql)
- [x] `pipeline_runs` table exists
- [x] `latest_scores_staging` table exists
- [x] `mcp_servers` table has `metadata_json` column

### ✅ GitHub Secrets
- [x] `DATABASE_URL` secret is set in GitHub repository secrets
- [ ] Verify: Go to Settings → Secrets and variables → Actions

### ✅ Workflow Configuration
- [x] `WRITE_TO_STAGING=1` set for scorer job
- [x] Pipeline run recording configured (record-start, record-success, record-failure)
- [x] All worker jobs have correct dependencies
- [x] Timeout set for scout job (10 minutes)

### ✅ Code Fixes
- [x] Provider relationship fixed (direct class reference)
- [x] `metadata_json` column added to MCPServer model
- [x] Scorer Optional import fixed
- [x] Sage-meridian filename fixed (daily_brief.py)
- [x] Container App revision suffix fix (unique timestamps)

### ⚠️ Container Deployment
- [ ] Public API container needs redeploy with latest model changes
- [ ] Check: `deploy-staging.yml` workflow should trigger on push to main
- [ ] Or manually trigger: Actions → Deploy to Staging → Run workflow

## Current Status

**Last Successful Run:** `2026-01-27T05:52:12` (from status endpoint)

**Current Run:** 
- Run ID: `cb9fc7faec04447197368408ea8b8a98`
- Status: Running
- Started: `2026-01-27T05:45:35` (over 12 hours ago - may be stuck)

## Ready to Run?

### If Current Run is Stuck:
1. Check GitHub Actions for the running workflow
2. If it's been running > 1 hour, it may be stuck
3. Cancel the stuck run
4. Then trigger a new run

### To Run Pipeline:
1. Go to: https://github.com/zimaxnet/secai-radar/actions
2. Click "Daily Pipeline" workflow
3. Click "Run workflow" → "Run workflow"

### Expected Duration:
- Scout: ~2-5 minutes (fetching 100 servers)
- Curator: ~30 seconds
- Evidence Miner: ~2-3 minutes (extracting claims + GitHub API)
- Scorer: ~30 seconds
- Drift Sentinel: ~10 seconds
- Sage Meridian: ~10 seconds
- Publisher: ~10 seconds
- **Total: ~5-10 minutes**

## Post-Run Verification

After pipeline completes, check:

1. **Status Endpoint:**
   ```bash
   curl https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status
   ```
   Should show `lastSuccessfulRun` with recent timestamp

2. **Rankings Endpoint:**
   ```bash
   curl https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/mcp/rankings?page=1&pageSize=5
   ```
   Should return JSON with servers array

3. **Database Check:**
   ```sql
   SELECT COUNT(*) FROM mcp_servers WHERE status = 'Active';
   SELECT COUNT(*) FROM latest_scores;
   SELECT COUNT(*) FROM score_snapshots;
   ```

## Known Issues Fixed

- ✅ SQLAlchemy Provider relationship mapping
- ✅ MCPServer metadata_json column missing
- ✅ Scorer dependency resolution
- ✅ Container App revision suffix conflicts
- ✅ Pipeline run recording

## Blockers

- ⚠️ **Container needs redeploy** - Public API model changes not yet deployed
- ⚠️ **Current run may be stuck** - Check GitHub Actions status
