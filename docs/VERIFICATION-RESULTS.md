# Verification Results: Real MCP Rankings Status

**Date:** 2026-01-27  
**Pipeline Run:** Latest successful at 18:08:11

## Key Findings

### ✅ What's Working

1. **Scout is Fetching Real Data**
   - **4,215 raw observations** from Official Registry
   - All observations have correct structure with `_full_server_json`
   - Observations include normalized fields: `name`, `repo_url`, `description`, `package`

2. **Scoring is Working**
   - **44 total score snapshots** exist
   - **4 servers have non-zero scores** (91.00, 85.50, 72.00, 58.00)
   - Tiers distributed: A:2, B:1, C:1, D:40
   - Evidence confidence: 0:40, 1:1, 2:2, 3:1

3. **API Endpoints Working**
   - Rankings endpoint returns data (no 500 errors)
   - Status endpoint shows last successful run

### ❌ Critical Issues

1. **Curator Not Processing Observations**
   - **4,115 unprocessed observations** (`processed_at IS NULL`)
   - Curator only created **1 server from registry** (named "Unknown")
   - Curator processes 1000 at a time, but only 1 server created suggests:
     - Deduplication too aggressive (marking all as duplicates)
     - Or error during processing causing early exit
     - Or name extraction failing

2. **Rankings Show Seed Data Only**
   - 4 servers in rankings: Filesystem, GitHub, Slack, Fetch
   - All have `source: None` (not from Official Registry)
   - All show `trustScore: 0.0` in rankings (but scores exist in snapshots!)

3. **Score Mismatch**
   - Seed servers HAVE good scores (91, 85.5, 72, 58)
   - But `latest_scores` points to zero-score snapshots
   - This suggests `latest_scores` wasn't updated correctly

## Root Cause Analysis

### Primary Issue: Curator Deduplication

**Problem:** Curator is checking if `server_id` already exists in `mcp_servers` before creating new records. If the ID generation is creating the same ID for different servers, they'll all be marked as duplicates.

**Verification Needed:**
```sql
-- Check if server_id generation is creating duplicates
SELECT server_id, COUNT(*) as count
FROM mcp_servers
GROUP BY server_id
HAVING COUNT(*) > 1;
```

**Likely Cause:** The `generate_server_id()` function might be:
- Using the same fallback (name+source) for many servers
- Or repo_url/endpoint extraction is failing, causing all to use name+source
- Or name extraction is failing, causing all to be "Unknown"

### Secondary Issue: latest_scores Points to Wrong Snapshots

**Problem:** The 4 seed servers have good scores in `score_snapshots`, but `latest_scores` points to zero-score snapshots.

**Fix:** Need to update `latest_scores` to point to the highest-scoring snapshots for each server.

## Immediate Actions Required

### 1. Fix Curator Name Extraction

**Issue:** Curator extracts name with:
```python
name = obs.get("name") or obs.get("server_name", "Unknown")
```

**Check:** Verify observations have `name` field (✅ confirmed they do)

**Possible Issue:** If name is empty string or None, it falls back to "Unknown"

**Fix:** Add better name extraction:
```python
# Try multiple sources for name
name = (obs.get("name") or 
        obs.get("server_name") or 
        obs.get("_full_server_json", {}).get("name") or 
        "Unknown")
```

### 2. Fix Curator Deduplication Logic

**Issue:** All servers might be getting the same `server_id` if:
- repo_url extraction fails
- endpoint extraction fails  
- docs_url extraction fails
- All fall back to `name+source`, and if name is "Unknown", all get same ID

**Fix:** 
- Add logging to see what server_id is generated for each observation
- Verify repo_url/endpoint extraction is working
- Ensure name extraction doesn't default to "Unknown"

### 3. Fix latest_scores to Use Best Scores

**Issue:** `latest_scores` points to zero-score snapshots instead of best scores.

**Fix:**
```sql
-- Update latest_scores to point to highest-scoring snapshots
UPDATE latest_scores ls
SET score_id = (
    SELECT score_id 
    FROM score_snapshots ss
    WHERE ss.server_id = ls.server_id
    ORDER BY ss.trust_score DESC, ss.assessed_at DESC
    LIMIT 1
);
```

## Next Steps

1. **Add logging to Curator** to see:
   - How many observations are processed
   - What server_ids are generated
   - Why servers are skipped (duplicate/ambiguous)
   - What names are extracted

2. **Fix name extraction** to use `_full_server_json.name` as fallback

3. **Fix latest_scores** to point to best scores

4. **Re-run pipeline** and verify:
   - More than 1 server created from registry
   - Server names are real (not "Unknown")
   - Rankings show real MCPs with non-zero scores
