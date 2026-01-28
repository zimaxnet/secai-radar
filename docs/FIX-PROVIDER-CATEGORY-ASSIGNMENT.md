# Plan: Fix Provider Assignment and Category Extraction

## Current Issues

1. **636 servers have `provider_id='0000000000000000'` (Unknown)** - Curator only creates providers from `publisher` field, but most MCPs don't have this
2. **All 636 servers have `category_primary=NULL`** - Curator doesn't extract or assign categories
3. **Trust scores are 0** - Expected until Evidence Miner completes
4. **Daily brief not populated** - Need to verify summary service queries correctly

## Implementation Tasks

1. Enhance provider extraction to use repo_url
2. Add category extraction from server name/description
3. Update Curator to set category_primary
4. Create backfill script for existing servers
5. Verify daily brief integration
