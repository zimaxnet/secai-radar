# Pipeline Deduplication and Validation

## Overview

This document describes the validation and deduplication mechanisms implemented at each stage of the daily pipeline to ensure only real, valid, non-duplicate MCP servers appear in the rankings.

## Problem Statement

The pipeline was producing duplicates and non-real MCPs in the rankings because:
1. Curator was creating servers even with minimal data (just name + source)
2. No validation that servers are "real" MCPs with required identifiers
3. Deduplication only checked server_id, not content similarity
4. Invalid servers were marked as 'Active' by default
5. No cleanup step to identify and mark duplicates

## Solution: Multi-Stage Validation

### 1. Curator (T-071) - Initial Validation and Deduplication

**Location**: `apps/workers/curator/src/curator.py`

**Validations**:
- ✅ Server must have at least one of: `repo_url`, `endpoint`, or `docs_url`
- ✅ Server name must not be "Unknown" or empty
- ✅ Content-based deduplication using normalized URLs (not just server_id)
- ✅ Status set to 'Unknown' if missing required data, 'Active' otherwise

**Deduplication Logic**:
1. Check if server_id already exists in database → skip
2. Check if server_id already seen in current batch → skip
3. Check if normalized URLs (repo_url, endpoint, docs_url) match existing servers → skip
4. Track normalized URLs for content-based deduplication

**Code Changes**:
- Added `is_valid_mcp_server()` function to validate observations
- Enhanced `dedupe_servers()` to track normalized URLs and check content similarity
- Updated `store_canonical_servers()` to set status based on data completeness

### 2. Cleanup Duplicates Script - Post-Curator Cleanup

**Location**: `scripts/cleanup-duplicates.sh` and `apps/public-api/scripts/cleanup_duplicates.py`

**Purpose**: Identify and mark duplicate servers that may have been created before improved deduplication.

**Process**:
1. Find servers with same normalized `repo_url` or `docs_url`
2. Group duplicates together
3. Select "best" server from each group:
   - Has `repo_url`: +100 points
   - Has `docs_url`: +50 points
   - Status is 'Active': +10 points
   - Older `first_seen_at`: tiebreaker
4. Mark others as 'Deprecated'

**Usage**:
```bash
./scripts/cleanup-duplicates.sh
```

**When to Run**: After Curator, before Evidence Miner (included in `run-full-path2.sh`)

### 3. Scorer (T-073) - Pre-Scoring Validation

**Location**: `apps/workers/scorer/src/scorer.py`

**Validations**:
- ✅ Only scores servers with `repo_url` OR `docs_url`
- ✅ Skips servers with name "Unknown" or empty
- ✅ Automatically marks invalid 'Active' servers as 'Unknown' status

**Code Changes**:
- Enhanced query to filter invalid servers before scoring
- Added UPDATE to mark invalid servers as 'Unknown'

### 4. Publisher (T-076) - Pre-Publish Validation

**Location**: `apps/workers/publisher/src/publisher.py`

**Validations**:
- ✅ Staging must contain all valid Active servers
- ✅ No invalid servers (missing data, "Unknown" name) in staging
- ✅ No duplicate servers (same normalized URLs) in staging
- ✅ Rankings only include valid, non-duplicate servers

**Code Changes**:
- Enhanced `validate_staging()` to check for invalid and duplicate servers
- Updated `_fetch_rankings_payload()` to filter invalid servers from rankings

## Pipeline Flow with Validation

```
Scout
  ↓ (writes raw_observations)
Curator
  ↓ (validates + deduplicates → mcp_servers)
  - Validates: has repo_url/docs_url/endpoint, name != "Unknown"
  - Deduplicates: by server_id and normalized URLs
  - Sets status: 'Active' if valid, 'Unknown' if invalid
Cleanup Duplicates
  ↓ (marks duplicates as 'Deprecated')
  - Finds servers with same normalized URLs
  - Keeps best one, marks others as 'Deprecated'
Evidence Miner
  ↓ (extracts evidence)
Scorer
  ↓ (scores servers)
  - Only scores valid servers (has repo_url/docs_url, name != "Unknown")
  - Marks invalid 'Active' servers as 'Unknown'
Drift Sentinel
  ↓ (detects changes)
Daily Brief
  ↓ (generates brief)
Publisher
  ↓ (publishes to stable)
  - Validates staging: no invalid/duplicate servers
  - Only publishes valid, non-duplicate servers
  - Rankings only include valid servers
```

## Validation Rules Summary

### Server is Valid if:
- ✅ Has at least one of: `repo_url`, `endpoint`, or `docs_url`
- ✅ `server_name` is not NULL, not empty, and not "Unknown"
- ✅ Status is 'Active' (not 'Unknown' or 'Deprecated')

### Server is Duplicate if:
- ✅ Same normalized `repo_url` (after removing query params, fragments)
- ✅ Same normalized `docs_url` (after removing query params, fragments)
- ✅ Same normalized `endpoint` host (if available)

### Best Server Selection (for duplicates):
1. Has `repo_url` (highest priority)
2. Has `docs_url`
3. Status is 'Active'
4. Older `first_seen_at` (most established)

## Running Cleanup Manually

If you need to clean up existing duplicates:

```bash
# Set DATABASE_URL or use Azure Key Vault
export DATABASE_URL="postgresql://..."

# Run cleanup
./scripts/cleanup-duplicates.sh
```

## Monitoring

Check for invalid/duplicate servers:

```sql
-- Invalid servers (should be 0 after cleanup)
SELECT COUNT(*) FROM mcp_servers
WHERE status = 'Active'
AND (repo_url IS NULL AND docs_url IS NULL)
OR server_name IS NULL
OR server_name = ''
OR LOWER(TRIM(server_name)) = 'unknown';

-- Duplicate servers (should be 0 after cleanup)
WITH normalized_urls AS (
    SELECT 
        server_id,
        LOWER(TRIM(REGEXP_REPLACE(repo_url, '[?#].*', ''))) as normalized_repo,
        LOWER(TRIM(REGEXP_REPLACE(docs_url, '[?#].*', ''))) as normalized_docs
    FROM mcp_servers
    WHERE status = 'Active'
    AND (repo_url IS NOT NULL OR docs_url IS NOT NULL)
),
duplicates AS (
    SELECT normalized_repo, COUNT(*) as cnt
    FROM normalized_urls
    WHERE normalized_repo IS NOT NULL AND normalized_repo != ''
    GROUP BY normalized_repo
    HAVING COUNT(*) > 1
    UNION
    SELECT normalized_docs, COUNT(*) as cnt
    FROM normalized_urls
    WHERE normalized_docs IS NOT NULL AND normalized_docs != ''
    GROUP BY normalized_docs
    HAVING COUNT(*) > 1
)
SELECT COUNT(*) FROM duplicates;
```

## Testing

After running the pipeline, verify:

1. **No invalid servers in rankings**:
   ```bash
   curl https://api.secairadar.cloud/api/v1/public/mcp/rankings | jq '.data.servers[] | select(.serverName == "Unknown" or .serverName == "")'
   ```
   Should return empty array.

2. **No duplicates in rankings**:
   ```bash
   curl https://api.secairadar.cloud/api/v1/public/mcp/rankings | jq '.data.servers | group_by(.serverId) | map(select(length > 1))'
   ```
   Should return empty array.

3. **All ranked servers have required data**:
   ```bash
   curl https://api.secairadar.cloud/api/v1/public/mcp/rankings | jq '.data.servers[] | select(.serverId and .serverName and .serverName != "Unknown") | length'
   ```
   Should return count matching total servers.

## Future Improvements

- [ ] Add fuzzy name matching for deduplication (e.g., "mcp-server" vs "mcp_server")
- [ ] Add provider-based deduplication (same provider + similar name)
- [ ] Add manual review queue for ambiguous duplicates
- [ ] Add metrics/alerting for duplicate detection rate
- [ ] Add automated cleanup job that runs periodically
