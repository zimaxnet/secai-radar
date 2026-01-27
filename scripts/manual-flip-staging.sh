#!/bin/bash
# Manual script to flip staging to stable (use if Publisher validation fails but you want to force it)
# WARNING: This bypasses validation. Use only if you're sure staging data is correct.

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

echo "=== Manual Staging Flip (Bypasses Validation) ==="
echo ""
echo "WARNING: This will force-flip staging to stable without validation."
echo "Only use this if you're certain staging data is correct."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

"$VENV/bin/python" << 'PYTHON_SCRIPT'
import os
import psycopg2
import sys
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check if staging exists
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'latest_scores_staging'
        )
    """)
    staging_exists = cur.fetchone()[0]
    
    if not staging_exists:
        print("ERROR: latest_scores_staging table does not exist")
        sys.exit(1)
    
    # Check staging count
    cur.execute("SELECT COUNT(*) FROM latest_scores_staging")
    staging_count = cur.fetchone()[0]
    
    if staging_count == 0:
        print("ERROR: latest_scores_staging is empty")
        sys.exit(1)
    
    print(f"Found {staging_count} rows in staging")
    
    # Check for invalid references
    cur.execute("""
        SELECT COUNT(*) FROM latest_scores_staging st
        LEFT JOIN score_snapshots ss ON st.score_id = ss.score_id
        WHERE ss.score_id IS NULL
    """)
    invalid_refs = cur.fetchone()[0]
    
    if invalid_refs > 0:
        print(f"WARNING: {invalid_refs} staging rows reference invalid score_snapshots")
        print("These rows will be skipped during flip")
    
    # Perform the flip
    print("\nFlipping staging to stable...")
    cur.execute("TRUNCATE latest_scores")
    cur.execute("""
        INSERT INTO latest_scores (server_id, score_id, updated_at)
        SELECT server_id, score_id, updated_at 
        FROM latest_scores_staging
        WHERE score_id IN (SELECT score_id FROM score_snapshots)
    """)
    
    # Refresh materialized view
    print("Refreshing latest_assessments_view...")
    cur.execute("REFRESH MATERIALIZED VIEW latest_assessments_view")
    
    conn.commit()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM latest_scores")
    stable_count = cur.fetchone()[0]
    
    print(f"\n✓ Flip complete: {stable_count} rows in latest_scores")
    print(f"  (Skipped {invalid_refs} rows with invalid score_snapshots)")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

PYTHON_SCRIPT

echo ""
echo "=== Manual Flip Complete ==="
echo ""
echo "Next step: Run Publisher to refresh rankings cache:"
echo "  ./scripts/run-publisher.sh"
