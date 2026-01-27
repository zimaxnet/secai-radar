# Real MCP Rankings Implementation - Complete

## Changes Implemented

### 1. Curator Fixes ✅

**File:** `apps/workers/curator/src/curator.py`

**Changes:**
- ✅ Added `extract_from_full_server_json()` helper function to extract fields from nested `_full_server_json`
- ✅ Improved name extraction: Now checks `_full_server_json.name` as fallback, handles empty strings properly
- ✅ Improved field extraction: Extracts `repo_url` from `_full_server_json.repository.url`, `endpoint` from `_full_server_json.remotes[0].url`
- ✅ Added provider creation: Extracts publisher from observations and creates proper provider records using `get_or_create_provider()`
- ✅ Added detailed logging: Logs processing progress, server_id generation, skip reasons, and server creation

**Impact:** Curator should now create multiple real MCP servers instead of just 1 "Unknown" server.

### 2. Scorer Fixes ✅

**File:** `apps/workers/scorer/src/scorer.py`

**Changes:**
- ✅ Updated `score_server()` to use best-scoring snapshot for stable `latest_scores` (not just latest)
- ✅ Added post-scoring update in `run_scorer()` to ensure `latest_scores_staging` points to best scores after all servers are scored
- ✅ Added progress logging every 10 servers

**Impact:** Rankings will show the best scores for each server, not zero scores from failed evidence extraction runs.

### 3. Evidence Miner Logging ✅

**File:** `apps/workers/evidence-miner/src/evidence_miner.py`

**Changes:**
- ✅ Added logging for registry server count
- ✅ Added logging for evidence extraction success/failure per server
- ✅ Better error messages

**Impact:** Better visibility into evidence extraction process.

### 4. Database Migration ✅

**File:** `apps/public-api/migrations/009_fix_latest_scores.sql`

**Changes:**
- ✅ SQL migration to update existing `latest_scores` to point to highest-scoring snapshots
- ✅ Also updates `latest_scores_staging` if it exists
- ✅ Migration applied to database

**Impact:** Existing rankings now show best scores instead of zero scores.

## Next Steps: Verification

### 1. Re-run Pipeline

The pipeline needs to be re-run to:
- Process the 4,115 unprocessed observations with the fixed Curator
- Create real MCP servers with proper names and providers
- Extract evidence from server.json
- Calculate scores for real servers

**To run:**
1. Go to: https://github.com/zimaxnet/secai-radar/actions
2. Click "Daily Pipeline" → "Run workflow" → "Run workflow"

### 2. Verify Results

After pipeline completes, check:

**Database:**
```sql
-- Should show > 1 server from Official Registry
SELECT COUNT(*) FROM mcp_servers 
WHERE metadata_json->>'source_provenance' = 'Official Registry';

-- Should show real server names (not "Unknown")
SELECT server_name, metadata_json->>'source_provenance' as source
FROM mcp_servers
WHERE metadata_json->>'source_provenance' = 'Official Registry'
LIMIT 10;

-- Should show evidence claims
SELECT COUNT(*) FROM evidence_claims;

-- Should show non-zero scores in rankings
SELECT s.server_name, ss.trust_score, ss.tier, ss.evidence_confidence
FROM mcp_servers s
JOIN latest_scores ls ON s.server_id = ls.server_id
JOIN score_snapshots ss ON ls.score_id = ss.score_id
WHERE ss.trust_score > 0
ORDER BY ss.trust_score DESC
LIMIT 10;
```

**API:**
```bash
# Should return real MCPs with non-zero scores
curl https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/mcp/rankings?page=1&pageSize=10
```

**Website:**
- Visit: https://secairadar.cloud/mcp
- Should show real MCP servers with trust scores > 0.0
- Server names should match real MCPs from Official Registry

## Expected Results

**After successful pipeline run:**
- ✅ 10+ real MCP servers from Official Registry in `mcp_servers` table
- ✅ Server names match real MCPs (e.g., "filesystem", "github", "slack", "fetch" - but from registry, not seed)
- ✅ At least 5 servers have `trustScore > 0.0` in rankings
- ✅ At least 2 servers have `evidenceConfidence >= 1`
- ✅ `source_provenance` = "Official Registry" for real MCPs
- ✅ Providers created from publisher information

## Troubleshooting

If rankings still show zero scores or seed data:

1. **Check Curator logs** - Should show "Created X canonical servers from Y observations"
2. **Check Evidence Miner logs** - Should show "Extracted evidence from server.json for X servers"
3. **Check Scorer logs** - Should show "Scored X/Y servers" and "Updated X staging entries"
4. **Check database** - Run verification queries above
5. **Check Publisher** - Should show "Staging validation passed" and "Dataset published successfully"

## Files Changed

- `apps/workers/curator/src/curator.py` - Name/field extraction, provider creation, logging
- `apps/workers/scorer/src/scorer.py` - Best score selection, logging
- `apps/workers/evidence-miner/src/evidence_miner.py` - Logging
- `apps/public-api/migrations/009_fix_latest_scores.sql` - Database migration
- `docs/PIPELINE-READINESS-CHECK.md` - Readiness checklist
