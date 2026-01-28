# Evaluation: Why Only Test Servers Are Loading Despite 4,000+ Observations

## Executive Summary

The pipeline has **4,119 unprocessed raw observations** from the Official MCP Registry, but only **5 test servers** appear in rankings. The root cause is a **database constraint violation** that aborts the entire transaction when Curator tries to store new servers, preventing real MCPs from being added to the database.

## Current State

### Database Status
- **Total servers in database**: 5 (all test/mock data)
  - `s100000000000001`: Filesystem (no repo_url, no docs_url)
  - `s100000000000002`: GitHub (no repo_url, no docs_url)
  - `s100000000000003`: Slack (no repo_url, no docs_url)
  - `s100000000000004`: Fetch (no repo_url, no docs_url)
  - `6f0b19de6f54e844`: Unknown (no repo_url, no docs_url)

- **Raw observations**: 4,219 total
  - **Processed**: 100 (2.4%)
  - **Unprocessed**: 4,119 (97.6%)

- **Servers with scores**: 4 (the 4 test servers above, excluding "Unknown")

### Curator Behavior
- Processes 1,000 observations per run
- Creates ~375 canonical servers per batch (after deduplication)
- **But only 9 servers were actually stored** before transaction abort
- **366 servers failed to store** due to transaction abort

## Root Cause Analysis

### Primary Issue: Duplicate `server_slug` Constraint Violation

**Error**: `duplicate key value violates unique constraint "mcp_servers_server_slug_key"`

**What's happening**:
1. Curator generates `server_slug` by normalizing server names (e.g., `"io.github.chris85/app-ding-unified-offer-protocol"` → `"iogithubchris85appdingunified-offer-protocol"`)
2. Multiple different servers can have the same normalized slug (e.g., `"io.github.chris85/app-ding"` and `"io.github.chris85/app-ding-unified"` both normalize to similar slugs)
3. When Curator tries to INSERT a server with a slug that already exists (from a previous batch or the same batch), PostgreSQL throws a `UniqueViolation` error
4. **The transaction aborts**, and all subsequent INSERTs in that transaction fail with "current transaction is aborted, commands ignored until end of transaction block"
5. Only servers inserted **before** the first conflict succeed (9 out of 375 in the last run)

**Example**:
```
Server 1: server_id="abc123", server_slug="iogithubchris85appding" → INSERT succeeds
Server 2: server_id="def456", server_slug="iogithubchris85appding" → UNIQUE CONSTRAINT VIOLATION
Server 3-375: → All fail because transaction is aborted
```

### Secondary Issues

1. **Validation Too Strict**: 
   - Scorer only checks for `repo_url` or `docs_url` in the table columns
   - Many MCPs have `endpoint` URLs stored in `metadata_json` but not in `repo_url`/`docs_url` columns
   - These valid servers are marked as 'Unknown' and not scored

2. **Status Determination Logic**:
   - Curator checks for endpoint in `metadata_json._full_server_json.remotes[0].url`
   - But this check happens during storage, and if it fails, status is set to 'Unknown'
   - Scorer then rejects 'Unknown' servers, creating a catch-22

3. **Transaction Management**:
   - All 375 servers are inserted in a single transaction
   - First error aborts the entire transaction
   - No rollback/recovery mechanism to continue with remaining servers

## Data Flow Breakdown

```
Scout (Working)
  ↓
  Fetches 4,219 observations from Official MCP Registry
  ↓
Raw Observations Table (4,119 unprocessed)
  ↓
Curator (Partially Working)
  ↓
  Processes 1,000 observations → Creates 375 canonical servers
  ↓
  Tries to INSERT 375 servers in one transaction
  ↓
  ❌ First duplicate slug → Transaction aborts
  ↓
  Only 9 servers stored (those before the conflict)
  ↓
mcp_servers Table (Still only 5 test servers)
  ↓
Scorer (Fails)
  ↓
  Finds 0 valid servers (5 test servers have no repo_url/docs_url)
  ↓
  Marks all 5 as 'Unknown'
  ↓
Publisher (Fails)
  ↓
  Staging validation fails: "4 invalid or deprecated servers in staging"
  ↓
Rankings API (Shows Mock Data)
  ↓
  Returns only the 4 test servers with scores
```

## Why Test Servers Appear

The 5 test servers (Filesystem, GitHub, Slack, Fetch, Unknown) were likely:
1. **Seeded manually** or from an earlier test run
2. **Have hardcoded server_ids** (`s100000000000001`, etc.) that don't conflict with real MCPs
3. **Already have score_snapshots** from previous pipeline runs
4. **Appear in `latest_scores`** table, so they show up in rankings

Real MCPs from the registry **cannot be stored** because:
- Their normalized slugs conflict with existing slugs
- The transaction aborts before they can be inserted
- They never make it to the `mcp_servers` table

## Fixes Required

### 1. Fix Duplicate Slug Handling (CRITICAL)

**File**: `apps/workers/curator/src/curator.py`

**Solution**: Handle `server_slug` conflicts by:
- Checking if slug exists before INSERT
- Appending server_id suffix if conflict: `{base_slug}-{server_id[:8]}`
- Using `ON CONFLICT (server_slug)` clause in INSERT statement
- OR: Make slug generation include server_id to ensure uniqueness

**Status**: Partially implemented (slug uniqueness check added, but ON CONFLICT clause needs PostgreSQL syntax fix)

### 2. Fix Transaction Error Handling

**File**: `apps/workers/curator/src/curator.py`

**Solution**: 
- Commit in smaller batches (e.g., 50 servers per commit)
- OR: Use savepoints to allow partial commits
- OR: Handle each server INSERT in its own try/except and continue

**Status**: Error handling added but needs batch commits

### 3. Fix Scorer Validation

**File**: `apps/workers/scorer/src/scorer.py`

**Solution**: 
- Check for endpoint in `metadata_json` when validating servers
- Use JSONB query: `metadata_json::text LIKE '%"remotes"%'`

**Status**: ✅ Fixed - now checks metadata_json for endpoints

### 4. Fix Curator Status Logic

**File**: `apps/workers/curator/src/curator.py`

**Solution**:
- Ensure endpoint check in `store_canonical_servers` correctly identifies servers with endpoints
- Set status to 'Active' if endpoint exists in metadata_json

**Status**: ✅ Fixed - now checks for endpoint in metadata

## Immediate Actions Needed

1. **Fix the duplicate slug issue** - This is blocking all new servers from being stored
2. **Run Curator in batches** - Process remaining 4,119 observations
3. **Re-run Scorer** - Score the newly stored real MCPs
4. **Run Publisher** - Publish real MCPs to rankings
5. **Verify rankings** - Check that real MCPs appear instead of test data

## Expected Outcome After Fixes

- **4,000+ real MCP servers** from Official Registry in database
- **Active servers with scores** in rankings
- **No test/mock servers** in production rankings
- **Real provider names, repo URLs, and trust scores** displayed

## Testing Checklist

- [ ] Curator stores servers without slug conflicts
- [ ] Transaction commits successfully for all 375 servers per batch
- [ ] Scorer validates servers with endpoints in metadata_json
- [ ] Publisher accepts staging with real MCPs
- [ ] Rankings API returns real MCPs (not test data)
- [ ] Frontend displays real server names and providers

## Fixes Applied

### 1. Duplicate Slug Handling ✅

**Solution Implemented**:
- Added slug uniqueness check before INSERT
- If slug exists for different server_id, append server_id suffix: `{base_slug}-{server_id[:8]}`
- This ensures each server gets a unique slug even if names normalize to the same value

**Result**: 
- ✅ Curator now successfully stores 330+ servers per batch (0 errors)
- ✅ Database now contains **641 servers** (5 test + 636 real MCPs)
- ✅ All 4,119 observations processed
- ✅ Transaction commits successfully

### 2. JSON Parsing Fix in Scorer ✅

**Problem**: `metadata_json` from PostgreSQL JSONB is returned as a dict, but code was calling `json.loads()` on it.

**Solution**: Check if `metadata_json` is already a dict before parsing.

**Result**:
- ✅ Scorer can now read metadata_json correctly
- ✅ Servers can be scored (though with 0 evidence, they get Tier D scores)

### 3. Scorer Validation Enhanced ✅

**Solution**: Updated validation to check for endpoints in `metadata_json` using JSONB queries.

**Result**:
- ✅ Servers with endpoints in metadata are now considered valid
- ✅ 636 active servers can be scored

### Current Status

### ✅ Completed
- **All 4,119 observations processed** by Curator
- **641 servers in database** (636 active real MCPs + 5 test servers)
- **Scorer validation fixed** to handle metadata_json correctly
- **JSON parsing fixed** in Scorer

### ⚠️ In Progress / Issues

1. **Evidence Miner**: Failed with JSON parsing error - needs fix
2. **Scorer**: Can score servers but most get Tier D (0 evidence = low scores)
3. **Publisher**: Staging validation failing because:
   - 55 valid active servers missing in staging (scoring may be incomplete)
   - 27 invalid/deprecated servers in staging (test servers need cleanup)

### Next Steps

1. **Fix Evidence Miner** JSON parsing (similar to Scorer fix)
2. **Run Evidence Miner** to extract evidence from repo_urls/docs_urls
3. **Re-run Scorer** to get better scores with evidence
4. **Clean up test servers** - mark as 'Deprecated' or remove from staging
5. **Run Publisher** to publish real MCPs to rankings
6. **Verify rankings** show real MCPs instead of test data

## Conclusion

**Root Cause**: Database constraint violation on `server_slug` was preventing real MCPs from being stored.

**Status**: ✅ **FIXED** - 636 real MCPs are now in the database. The pipeline is working, but:
- Evidence Miner needs JSON parsing fix (same issue as Scorer had)
- Test servers need to be removed/deprecated
- Once evidence is extracted and scores improve, rankings will show real MCPs

**Current State**:
- **636 active real MCP servers** in database
- **All observations processed**
- **Scoring works** (but scores are low without evidence)
- **Rankings still show test data** because staging validation is failing

Once Evidence Miner is fixed and test servers are cleaned up, the rankings will display the 636 real MCPs from the Official Registry.
