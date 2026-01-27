# Real MCP Rankings: Requirements and Implementation Status

## Executive Summary

This document outlines what must happen for SecAI Radar to display **real MCP server rankings** based on actual data from the Official MCP Registry and other sources, rather than seed/test data.

**Current Status:** Pipeline infrastructure is in place and running, but rankings show seed data with zero scores. Real MCP data flow needs verification and completion.

---

## Current State Analysis

### ✅ What's Working

1. **Pipeline Infrastructure**
   - GitHub Actions workflow runs successfully
   - All worker stages execute (Scout → Curator → Evidence Miner → Scorer → Drift → Brief → Publisher)
   - Pipeline run recording works
   - Status endpoint shows last successful run

2. **Database Schema**
   - All required tables exist (`raw_observations`, `mcp_servers`, `score_snapshots`, `latest_scores`, etc.)
   - `metadata_json` column added to `mcp_servers`
   - Migrations applied

3. **API Endpoints**
   - Rankings endpoint returns data (no 500 errors)
   - Status endpoint operational
   - Summary endpoint working

4. **Code Fixes**
   - Provider relationship mapping fixed
   - Scorer writes to staging (`WRITE_TO_STAGING=1`)
   - All worker dependencies resolved

### ⚠️ What's Not Working

1. **Rankings Show Seed Data**
   - Current rankings: 4 servers (Fetch, Slack, GitHub, Filesystem)
   - All have `trustScore: 0.0`, `tier: D`, `evidenceConfidence: 0`
   - These appear to be seed/test data, not real MCPs from registry

2. **Unknown Data Flow**
   - Unclear if Scout is fetching real servers from Official Registry
   - Unclear if real MCPs are being stored in database
   - Unclear if evidence extraction is working for real servers

---

## Requirements for Real MCP Rankings

### Phase 1: Data Ingestion (Scout)

**Requirement 1.1: Fetch Real MCP Servers**
- [ ] **Verify Scout fetches from Official Registry**
  - Check: `https://registry.modelcontextprotocol.io/v0.1/servers`
  - Expected: 100+ real MCP servers
  - Verify: `raw_observations` table has entries with `source_url` containing `registry.modelcontextprotocol.io`

**Requirement 1.2: Store Raw Observations**
- [ ] **Verify raw data is stored**
  - Check: `SELECT COUNT(*) FROM raw_observations WHERE source_url LIKE '%registry.modelcontextprotocol.io%';`
  - Expected: > 0 rows
  - Verify: Each observation has `_full_server_json` with complete server.json data

**Requirement 1.3: Handle Pagination**
- [ ] **Verify all pages are fetched**
  - Check: Scout logs show multiple pages being processed
  - Expected: All available servers from registry (100+)
  - Verify: No pagination errors in logs

**Current Implementation:**
- ✅ Scout has Official Registry adapter (`apps/workers/scout/src/sources/registry.py`)
- ✅ Pagination logic implemented
- ❓ **NEEDS VERIFICATION:** Is it actually fetching real data?

---

### Phase 2: Normalization (Curator)

**Requirement 2.1: Create Canonical Servers**
- [ ] **Verify real MCPs are normalized**
  - Check: `SELECT COUNT(*) FROM mcp_servers WHERE status = 'Active';`
  - Expected: > 0 (should match number of real servers fetched)
  - Verify: Server names match real MCPs (not "Unknown" or seed names)

**Requirement 2.2: Extract Metadata**
- [ ] **Verify metadata_json is populated**
  - Check: `SELECT server_name, metadata_json->>'source_provenance' FROM mcp_servers LIMIT 5;`
  - Expected: `source_provenance` = "Official Registry" for real MCPs
  - Verify: `metadata_json` contains `publisher`, `description`, `transport`, `package` fields

**Requirement 2.3: Create Providers**
- [ ] **Verify providers are created**
  - Check: `SELECT COUNT(*) FROM providers;`
  - Expected: > 0 providers
  - Verify: Provider names match real MCP publishers

**Requirement 2.4: Deduplication**
- [ ] **Verify no duplicates**
  - Check: `SELECT server_name, COUNT(*) FROM mcp_servers GROUP BY server_name HAVING COUNT(*) > 1;`
  - Expected: 0 rows (no duplicates)
  - Verify: Each real MCP appears once

**Current Implementation:**
- ✅ Curator normalizes server.json format
- ✅ Extracts metadata into `metadata_json`
- ✅ Creates providers
- ❓ **NEEDS VERIFICATION:** Are real MCPs being created, or only seed data?

---

### Phase 3: Evidence Extraction (Evidence Miner)

**Requirement 3.1: Extract Claims from server.json**
- [ ] **Verify claims extracted from Official Registry data**
  - Check: `SELECT COUNT(*) FROM evidence_claims WHERE claim_type IN ('Auth', 'Hosting', 'ToolAgency');`
  - Expected: > 0 claims
  - Verify: Claims reference real MCP server_ids

**Requirement 3.2: Fetch GitHub Popularity Signals**
- [ ] **Verify GitHub stars/forks are fetched**
  - Check: `SELECT server_name, metadata_json->'popularity_signals'->'github' FROM mcp_servers WHERE metadata_json->'popularity_signals' IS NOT NULL LIMIT 5;`
  - Expected: GitHub data with `stars`, `forks`, `watchers`
  - Verify: Data is recent (< 24 hours old)

**Requirement 3.3: Extract from Documentation**
- [ ] **Verify docs are scraped (if docs_url exists)**
  - Check: Evidence Miner logs show docs being fetched
  - Expected: Claims extracted from README/docs
  - Verify: `evidence_items` table has entries with `source_type = 'documentation'`

**Current Implementation:**
- ✅ Evidence Miner extracts from `_full_server_json`
- ✅ Fetches GitHub popularity signals
- ✅ Extracts claims from docs/repos
- ❓ **NEEDS VERIFICATION:** Is evidence being extracted for real MCPs?

---

### Phase 4: Scoring (Scorer)

**Requirement 4.1: Calculate Trust Scores**
- [ ] **Verify scores are calculated**
  - Check: `SELECT COUNT(*) FROM score_snapshots WHERE trust_score > 0;`
  - Expected: > 0 scores > 0.0
  - Verify: Scores are based on evidence (not all zeros)

**Requirement 4.2: Calculate Evidence Confidence**
- [ ] **Verify confidence levels**
  - Check: `SELECT evidence_confidence, COUNT(*) FROM score_snapshots GROUP BY evidence_confidence;`
  - Expected: Distribution across 0-3 (not all zeros)
  - Verify: Official Registry sources get +1 confidence boost

**Requirement 4.3: Determine Tiers**
- [ ] **Verify tier assignment**
  - Check: `SELECT tier, COUNT(*) FROM score_snapshots GROUP BY tier;`
  - Expected: Distribution across A/B/C/D (not all D)
  - Verify: Tiers match trust scores (A = highest, D = lowest)

**Requirement 4.4: Write to Staging**
- [ ] **Verify staging table is populated**
  - Check: `SELECT COUNT(*) FROM latest_scores_staging;`
  - Expected: Matches number of active servers
  - Verify: All active servers have scores in staging

**Current Implementation:**
- ✅ Scorer calculates trust scores using `packages/scoring`
- ✅ Writes to `latest_scores_staging` when `WRITE_TO_STAGING=1`
- ✅ Uses `ServerMetadata` for context
- ❓ **NEEDS VERIFICATION:** Are scores being calculated correctly? Why are all scores 0.0?

---

### Phase 5: Publishing (Publisher)

**Requirement 5.1: Validate Staging**
- [ ] **Verify staging validation passes**
  - Check: Publisher logs show "Staging validation passed"
  - Expected: No validation errors
  - Verify: All active servers have scores in staging

**Requirement 5.2: Flip Staging to Stable**
- [ ] **Verify latest_scores is populated**
  - Check: `SELECT COUNT(*) FROM latest_scores;`
  - Expected: Matches number of active servers
  - Verify: `latest_scores` has data after publisher runs

**Requirement 5.3: Refresh Rankings Cache**
- [ ] **Verify cache is updated**
  - Check: `SELECT COUNT(*) FROM rankings_cache;`
  - Expected: > 0 cache entries
  - Verify: Cache has recent `generated_at` timestamps

**Current Implementation:**
- ✅ Publisher validates staging
- ✅ Flips staging → stable
- ✅ Refreshes rankings cache
- ❓ **NEEDS VERIFICATION:** Is staging being flipped correctly?

---

## Verification Checklist

### Step 1: Verify Real Data Ingestion

```sql
-- Check if real MCPs are in raw_observations
SELECT COUNT(*) as total_observations,
       COUNT(DISTINCT CASE WHEN source_url LIKE '%registry.modelcontextprotocol.io%' THEN observation_id END) as registry_observations
FROM raw_observations;

-- Check if real MCPs are in mcp_servers
SELECT COUNT(*) as total_servers,
       COUNT(DISTINCT CASE WHEN metadata_json->>'source_provenance' = 'Official Registry' THEN server_id END) as registry_servers
FROM mcp_servers
WHERE status = 'Active';

-- List real MCP server names
SELECT server_name, metadata_json->>'source_provenance' as source, 
       metadata_json->>'publisher' as publisher
FROM mcp_servers
WHERE metadata_json->>'source_provenance' = 'Official Registry'
LIMIT 10;
```

**Expected Results:**
- `registry_observations` > 0
- `registry_servers` > 0
- Server names match real MCPs (e.g., "filesystem", "github", "slack", "fetch" are real, but verify they're from registry, not seed)

### Step 2: Verify Evidence Extraction

```sql
-- Check evidence claims
SELECT claim_type, COUNT(*) as count
FROM evidence_claims
GROUP BY claim_type
ORDER BY count DESC;

-- Check evidence items
SELECT source_type, COUNT(*) as count
FROM evidence_items
GROUP BY source_type;

-- Check GitHub popularity signals
SELECT server_name, 
       metadata_json->'popularity_signals'->'github'->>'stars' as stars,
       metadata_json->'popularity_signals'->'github'->>'forks' as forks
FROM mcp_servers
WHERE metadata_json->'popularity_signals'->'github' IS NOT NULL
LIMIT 10;
```

**Expected Results:**
- Evidence claims > 0
- Evidence items > 0
- GitHub stars/forks populated for servers with repo_url

### Step 3: Verify Scoring

```sql
-- Check score distribution
SELECT 
    COUNT(*) as total_scores,
    COUNT(CASE WHEN trust_score > 0 THEN 1 END) as non_zero_scores,
    AVG(trust_score) as avg_score,
    MIN(trust_score) as min_score,
    MAX(trust_score) as max_score
FROM score_snapshots;

-- Check tier distribution
SELECT tier, COUNT(*) as count
FROM score_snapshots
GROUP BY tier
ORDER BY tier;

-- Check evidence confidence distribution
SELECT evidence_confidence, COUNT(*) as count
FROM score_snapshots
GROUP BY evidence_confidence
ORDER BY evidence_confidence;
```

**Expected Results:**
- `non_zero_scores` > 0 (not all zeros)
- Tier distribution across A/B/C/D
- Evidence confidence > 0 for some servers

### Step 4: Verify Rankings Query

```sql
-- Test the actual rankings query
SELECT s.server_name, ss.trust_score, ss.tier, ss.evidence_confidence,
       p.provider_name, s.metadata_json->>'source_provenance' as source
FROM mcp_servers s
JOIN latest_scores ls ON s.server_id = ls.server_id
JOIN score_snapshots ss ON ls.score_id = ss.score_id
JOIN providers p ON s.provider_id = p.provider_id
WHERE s.status = 'Active'
ORDER BY ss.trust_score DESC NULLS LAST
LIMIT 10;
```

**Expected Results:**
- Returns 10+ servers
- Trust scores > 0.0 for some servers
- Source provenance = "Official Registry" for real MCPs
- Tiers distributed (not all D)

---

## Root Cause Analysis: Why Scores Are Zero

### Hypothesis 1: Seed Data Only
**Problem:** Rankings show seed data (Fetch, Slack, GitHub, Filesystem) which may have been inserted manually, not from the registry.

**Verification:**
```sql
-- Check if these are seed data or real registry data
SELECT server_name, 
       metadata_json->>'source_provenance' as source,
       first_seen_at,
       created_at
FROM mcp_servers
WHERE server_name IN ('Fetch', 'Slack', 'GitHub', 'Filesystem');
```

**Fix:** If seed data, ensure Scout fetches real MCPs and Curator creates new server records (not overwriting seed).

### Hypothesis 2: No Evidence Extracted
**Problem:** Evidence Miner isn't extracting claims, so Scorer has no evidence to score.

**Verification:**
```sql
-- Check evidence for these servers
SELECT s.server_name, COUNT(e.claim_id) as claim_count
FROM mcp_servers s
LEFT JOIN evidence_claims e ON s.server_id = e.server_id
WHERE s.server_name IN ('Fetch', 'Slack', 'GitHub', 'Filesystem')
GROUP BY s.server_name;
```

**Fix:** If claim_count = 0, check Evidence Miner logs for errors. Verify `_full_server_json` is being parsed correctly.

### Hypothesis 3: Scoring Logic Issue
**Problem:** Scorer is running but not calculating scores correctly (all zeros).

**Verification:**
```sql
-- Check if score_snapshots exist
SELECT COUNT(*) FROM score_snapshots;
SELECT server_id, trust_score, evidence_confidence, tier 
FROM score_snapshots 
LIMIT 5;
```

**Fix:** If scores exist but are all 0.0, check scoring calculator logic. Verify evidence is being passed to `calculate_trust_score()`.

### Hypothesis 4: Staging Not Flipped
**Problem:** Scores are in staging but not flipped to stable `latest_scores`.

**Verification:**
```sql
-- Check staging vs stable
SELECT 
    (SELECT COUNT(*) FROM latest_scores_staging) as staging_count,
    (SELECT COUNT(*) FROM latest_scores) as stable_count;
```

**Fix:** If staging has data but stable is empty, Publisher didn't flip. Check Publisher logs for validation errors.

---

## Action Plan: Get Real MCP Rankings

### Immediate Actions (Today)

1. **Verify Data Source**
   ```bash
   # Check Scout logs from last run
   # Verify it fetched from Official Registry
   # Check raw_observations table
   ```

2. **Check Database State**
   ```sql
   -- Run all verification queries above
   -- Identify where the data flow breaks
   ```

3. **Fix Root Cause**
   - If seed data: Ensure Scout fetches real MCPs
   - If no evidence: Fix Evidence Miner
   - If no scores: Fix Scorer
   - If staging not flipped: Fix Publisher

### Short-Term (This Week)

1. **Enhance Logging**
   - Add more detailed logging to each worker
   - Log counts at each stage (servers fetched, normalized, scored, etc.)

2. **Add Validation**
   - Add validation checks in each worker
   - Fail fast if expected data is missing

3. **Monitor Pipeline**
   - Set up alerts for zero scores
   - Track data flow metrics

### Long-Term (This Month)

1. **Multi-Source Support**
   - Add MCPAnvil adapter (currently placeholder)
   - Add Glama adapter
   - Add PulseMCP adapter

2. **Enhanced Evidence Extraction**
   - Improve claim extraction from server.json
   - Better GitHub API rate limiting
   - Cache GitHub data more effectively

3. **Scoring Improvements**
   - Refine trust score calculation
   - Add more evidence types
   - Improve tier assignment logic

---

## Success Criteria

### Minimum Viable (MVP)
- [ ] Rankings show 10+ real MCP servers from Official Registry
- [ ] At least 5 servers have `trustScore > 0.0`
- [ ] At least 2 servers have `evidenceConfidence >= 1`
- [ ] Tiers distributed (not all D)
- [ ] `source_provenance` = "Official Registry" for real MCPs

### Production Ready
- [ ] 50+ real MCP servers in rankings
- [ ] Trust scores range from 0.0 to 1.0 (not all zeros)
- [ ] Evidence confidence distributed (0-3)
- [ ] Tiers A/B/C/D all represented
- [ ] GitHub popularity signals populated
- [ ] Daily pipeline runs successfully
- [ ] Rankings update daily with new/changed MCPs

---

## Next Steps

1. **Run Verification Queries** (see above)
2. **Identify Root Cause** (which hypothesis is correct?)
3. **Fix the Issue** (based on root cause)
4. **Re-run Pipeline** (verify fix works)
5. **Monitor Rankings** (ensure real MCPs appear)

---

## References

- **Official Registry API:** https://registry.modelcontextprotocol.io/v0.1/servers
- **Database Schema:** `docs/implementation/database-schema.sql`
- **Pipeline Workflow:** `.github/workflows/daily-pipeline.yml`
- **Scout Registry Adapter:** `apps/workers/scout/src/sources/registry.py`
- **Scoring Logic:** `packages/scoring/src/scoring/calculator.py`
- **Real MCP Research:** `docs/REAL-MCP-RESEARCH.md`
