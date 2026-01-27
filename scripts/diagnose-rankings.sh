#!/bin/bash
# Diagnostic script to identify why rankings are empty
# Based on docs/DIAGNOSE-EMPTY-RANKINGS.md

set -e
cd "$(dirname "$0")/.."

if [ -z "${DATABASE_URL}" ]; then
  KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
  if command -v az &>/dev/null && az account show &>/dev/null 2>&1; then
    DATABASE_URL=$(az keyvault secret show --vault-name "$KV_NAME" --name database-url --query value -o tsv 2>/dev/null || true)
  fi
fi

if [ -z "${DATABASE_URL}" ]; then
  echo "DATABASE_URL is not set. Set it or use Azure CLI + Key Vault (secai-radar-kv / database-url)."
  exit 1
fi

export DATABASE_URL

VENV="${PWD}/apps/public-api/.venv"
if [ ! -d "$VENV" ]; then
  echo "Run ./scripts/run-migrations.sh first to create the venv."
  exit 1
fi

echo "=== SecAI Radar Rankings Diagnostic ==="
echo ""

# Extract connection details for psql
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p' || echo "5432")

# Use Python to query database (more reliable than parsing DATABASE_URL)
"$VENV/bin/python" << 'PYTHON_SCRIPT'
import os
import psycopg2
import json
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("1. RAW OBSERVATIONS (from Scout)")
    print("   " + "-" * 60)
    cur.execute("SELECT COUNT(*) FROM raw_observations")
    total_obs = cur.fetchone()[0]
    print(f"   Total raw observations: {total_obs}")
    
    if total_obs > 0:
        cur.execute("""
            SELECT COUNT(*), MAX(retrieved_at) 
            FROM raw_observations
        """)
        count, latest = cur.fetchone()
        print(f"   Latest observation: {latest}")
        cur.execute("""
            SELECT COUNT(DISTINCT source_url) 
            FROM raw_observations
        """)
        sources = cur.fetchone()[0]
        print(f"   Unique sources: {sources}")
    else:
        print("   ⚠️  NO RAW OBSERVATIONS - Scout may not be fetching data")
    print()
    
    print("2. MCP SERVERS (from Curator)")
    print("   " + "-" * 60)
    cur.execute("SELECT COUNT(*) FROM mcp_servers")
    total_servers = cur.fetchone()[0]
    print(f"   Total servers: {total_servers}")
    
    cur.execute("SELECT COUNT(*) FROM mcp_servers WHERE status = 'Active'")
    active_servers = cur.fetchone()[0]
    print(f"   Active servers: {active_servers}")
    
    if total_servers == 0:
        print("   ⚠️  NO SERVERS - Curator may not be processing raw_observations")
    print()
    
    print("3. PROVIDERS (from Curator)")
    print("   " + "-" * 60)
    cur.execute("SELECT COUNT(*) FROM providers")
    total_providers = cur.fetchone()[0]
    print(f"   Total providers: {total_providers}")
    
    if total_providers == 0:
        print("   ⚠️  NO PROVIDERS - Curator may not be creating providers")
    print()
    
    print("4. SCORE SNAPSHOTS (from Scorer)")
    print("   " + "-" * 60)
    cur.execute("SELECT COUNT(*) FROM score_snapshots")
    total_snapshots = cur.fetchone()[0]
    print(f"   Total score snapshots: {total_snapshots}")
    
    if total_snapshots > 0:
        cur.execute("""
            SELECT COUNT(*), MAX(assessed_at) 
            FROM score_snapshots
        """)
        count, latest = cur.fetchone()
        print(f"   Latest assessment: {latest}")
    else:
        print("   ⚠️  NO SCORE SNAPSHOTS - Scorer may not be running or may be failing")
    print()
    
    print("5. LATEST SCORES STAGING (from Scorer with WRITE_TO_STAGING=1)")
    print("   " + "-" * 60)
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'latest_scores_staging'
        )
    """)
    staging_exists = cur.fetchone()[0]
    
    if staging_exists:
        cur.execute("SELECT COUNT(*) FROM latest_scores_staging")
        staging_count = cur.fetchone()[0]
        print(f"   Staging table exists: Yes")
        print(f"   Servers in staging: {staging_count}")
        
        if staging_count > 0:
            cur.execute("""
                SELECT COUNT(*) FROM latest_scores_staging st
                LEFT JOIN score_snapshots ss ON st.score_id = ss.score_id
                WHERE ss.score_id IS NULL
            """)
            invalid_refs = cur.fetchone()[0]
            if invalid_refs > 0:
                print(f"   ⚠️  {invalid_refs} staging rows reference invalid score_snapshots")
            else:
                print("   ✓ All staging rows have valid score_snapshots")
        else:
            print("   ⚠️  STAGING IS EMPTY - Scorer may not be writing to staging")
    else:
        print("   ⚠️  STAGING TABLE DOES NOT EXIST - Migration may be missing")
    print()
    
    print("6. LATEST SCORES (stable - used by rankings)")
    print("   " + "-" * 60)
    cur.execute("SELECT COUNT(*) FROM latest_scores")
    stable_count = cur.fetchone()[0]
    print(f"   Servers in stable: {stable_count}")
    
    if stable_count == 0:
        print("   ⚠️  STABLE IS EMPTY - Publisher may not be flipping staging to stable")
        if staging_exists:
            cur.execute("SELECT COUNT(*) FROM latest_scores_staging")
            staging_count = cur.fetchone()[0]
            if staging_count > 0:
                print(f"   💡 FIX: Run Publisher to flip {staging_count} rows from staging to stable")
    else:
        cur.execute("""
            SELECT COUNT(*) FROM latest_scores ls
            LEFT JOIN score_snapshots ss ON ls.score_id = ss.score_id
            WHERE ss.score_id IS NULL
        """)
        invalid_refs = cur.fetchone()[0]
        if invalid_refs > 0:
            print(f"   ⚠️  {invalid_refs} stable rows reference invalid score_snapshots")
        else:
            print("   ✓ All stable rows have valid score_snapshots")
    print()
    
    print("7. RANKINGS QUERY TEST")
    print("   " + "-" * 60)
    cur.execute("""
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
             WHERE s.status = 'Active') as rankings_results
    """)
    row = cur.fetchone()
    active_servers, latest_scores_count, snapshots_count, providers_count, rankings_results = row
    
    print(f"   Active servers: {active_servers}")
    print(f"   Latest scores: {latest_scores_count}")
    print(f"   Score snapshots: {snapshots_count}")
    print(f"   Providers: {providers_count}")
    print(f"   Rankings query results: {rankings_results}")
    
    if rankings_results == 0:
        print("   ⚠️  RANKINGS QUERY RETURNS 0 RESULTS")
        print()
        print("   DIAGNOSIS:")
        if active_servers == 0:
            print("   - No active servers (Curator issue)")
        elif latest_scores_count == 0:
            print("   - No latest_scores (Publisher issue - staging not flipped)")
        elif snapshots_count == 0:
            print("   - No score_snapshots (Scorer issue)")
        elif providers_count == 0:
            print("   - No providers (Curator issue)")
        else:
            print("   - Join conditions not matching (data integrity issue)")
    else:
        print(f"   ✓ Rankings query would return {rankings_results} results")
    print()
    
    print("8. RECENT PIPELINE RUNS")
    print("   " + "-" * 60)
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'pipeline_runs'
        )
    """)
    runs_table_exists = cur.fetchone()[0]
    
    if runs_table_exists:
        cur.execute("""
            SELECT run_id, status, started_at, completed_at, 
                   CASE WHEN completed_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (completed_at - started_at))
                        ELSE NULL END as duration_seconds
            FROM pipeline_runs
            ORDER BY started_at DESC
            LIMIT 5
        """)
        runs = cur.fetchall()
        if runs:
            for run in runs:
                run_id, status, started_at, completed_at, duration = run
                print(f"   Run: {run_id[:16]}...")
                print(f"   Status: {status}")
                print(f"   Started: {started_at}")
                if completed_at:
                    print(f"   Completed: {completed_at} (duration: {duration:.1f}s)")
                else:
                    print(f"   Completed: Still running")
                print()
        else:
            print("   No pipeline runs recorded")
    else:
        print("   pipeline_runs table does not exist")
    print()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

PYTHON_SCRIPT

echo ""
echo "=== Diagnostic Complete ==="
echo ""
echo "Next steps:"
echo "1. If raw_observations is 0: Check Scout logs and registry adapter"
echo "2. If mcp_servers is 0: Run Curator manually: ./scripts/run-curator.sh"
echo "3. If score_snapshots is 0: Run Scorer manually: WRITE_TO_STAGING=1 ./scripts/run-scorer.sh"
echo "4. If latest_scores_staging has data but latest_scores is empty: Run Publisher: ./scripts/run-publisher.sh"
echo "5. If all tables have data but rankings is 0: Check join conditions and data integrity"
