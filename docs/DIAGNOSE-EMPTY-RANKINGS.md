# Diagnosing Empty Rankings

If the site shows no MCPs, check these tables in order:

## Required Data Flow

1. **raw_observations** (from Scout)
   ```sql
   SELECT COUNT(*) FROM raw_observations;
   ```

2. **mcp_servers** (from Curator)
   ```sql
   SELECT COUNT(*) FROM mcp_servers WHERE status = 'Active';
   ```

3. **providers** (from Curator)
   ```sql
   SELECT COUNT(*) FROM providers;
   ```

4. **score_snapshots** (from Scorer)
   ```sql
   SELECT COUNT(*) FROM score_snapshots;
   ```

5. **latest_scores** or **latest_scores_staging** (from Scorer)
   ```sql
   SELECT COUNT(*) FROM latest_scores;
   SELECT COUNT(*) FROM latest_scores_staging;
   ```

## Rankings Query Requirements

The rankings endpoint requires ALL of these joins to succeed:
- `mcp_servers` JOIN `latest_scores` 
- `latest_scores` JOIN `score_snapshots`
- `mcp_servers` JOIN `providers`

If any table is empty or the joins fail, no results will be returned.

## Quick Diagnostic Query

```sql
-- Check if rankings query would return results
SELECT 
    (SELECT COUNT(*) FROM mcp_servers WHERE status = 'Active') as active_servers,
    (SELECT COUNT(*) FROM latest_scores) as latest_scores_count,
    (SELECT COUNT(*) FROM score_snapshots) as score_snapshots_count,
    (SELECT COUNT(*) FROM providers) as providers_count,
    (SELECT COUNT(*) 
     FROM mcp_servers s
     JOIN latest_scores ls ON s.server_id = ls.server_id
     JOIN score_snapshots ss ON ls.score_id = ss.score_id
     JOIN providers p ON s.provider_id = p.provider_id
     WHERE s.status = 'Active') as rankings_results;
```

## Common Issues

1. **Scorer didn't set WRITE_TO_STAGING=1**
   - Fix: Set `WRITE_TO_STAGING=1` in workflow (✅ done)

2. **Publisher didn't flip staging to stable**
   - Check: `latest_scores_staging` has data but `latest_scores` is empty
   - Fix: Re-run publisher or manually flip

3. **No servers created**
   - Check: `mcp_servers` table is empty
   - Fix: Re-run Curator

4. **No scores created**
   - Check: `score_snapshots` table is empty
   - Fix: Re-run Scorer with `WRITE_TO_STAGING=1`

5. **Providers missing**
   - Check: `providers` table is empty
   - Fix: Re-run Curator (it should create providers)

## Manual Fix: Flip Staging to Stable

If `latest_scores_staging` has data but `latest_scores` is empty:

```sql
TRUNCATE latest_scores;
INSERT INTO latest_scores (server_id, score_id, updated_at)
SELECT server_id, score_id, updated_at FROM latest_scores_staging;
REFRESH MATERIALIZED VIEW latest_assessments_view;
```
