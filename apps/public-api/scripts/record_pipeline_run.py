#!/usr/bin/env python3
"""
Record pipeline run start/finish for T-080. Used by run-full-path2.sh.
  --start          Insert a new run, print run_id to stdout.
  --finish ID      Set completed_at and status=success for run_id.
  --finish ID --failed   Set status=failed.
"""

import argparse
import os
import sys
import uuid
import json
import psycopg2
import subprocess
from pathlib import Path
from datetime import date

# same resolve as run_incremental_migrations
_SCRIPT_DIR = Path(__file__).resolve().parent
_MIGRATIONS_DIR = _SCRIPT_DIR.parent / "migrations"

# Get DATABASE_URL from environment or Azure Key Vault (same pattern as other scripts)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Try Azure Key Vault
    KV_NAME = os.getenv("KEY_VAULT_NAME", "secai-radar-kv")
    try:
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", KV_NAME, "--name", "database-url", "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            DATABASE_URL = result.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

if not DATABASE_URL:
    DATABASE_URL = "postgresql://secairadar:password@localhost:5432/secairadar"


def _ensure_table(conn):
    """Idempotently ensure pipeline_runs exists (in case migration not run)."""
    sql = (_MIGRATIONS_DIR / "007_pipeline_runs.sql").read_text()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def start_run(trigger: str = "manual") -> str:
    run_id = str(uuid.uuid4()).replace("-", "")[:32]
    conn = psycopg2.connect(DATABASE_URL)
    try:
        _ensure_table(conn)
        with conn.cursor() as cur:
            # Check if trigger column exists (migration 007 has it, but older schemas may not)
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'pipeline_runs' AND column_name = 'trigger'
            """)
            has_trigger = cur.fetchone() is not None
            
            # Check schema columns to determine which INSERT to use
            cur.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'pipeline_runs'
            """)
            columns = {row[0] for row in cur.fetchall()}
            
            has_date = 'date' in columns
            has_trigger = 'trigger' in columns
            has_stages_json = 'stages_json' in columns
            has_deliverables_json = 'deliverables_json' in columns
            
            today = date.today()
            empty_json = json.dumps([])
            empty_deliverables = json.dumps({})
            
            # Build INSERT based on available columns
            if has_date and has_stages_json and has_deliverables_json:
                # Full schema (from database-schema.sql)
                if has_trigger:
                    cur.execute(
                        """
                        INSERT INTO pipeline_runs (run_id, date, trigger, status, started_at, stages_json, deliverables_json)
                        VALUES (%s, %s, %s, 'Running', NOW(), %s, %s)
                        """,
                        (run_id, today, trigger, empty_json, empty_deliverables),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO pipeline_runs (run_id, date, status, started_at, stages_json, deliverables_json)
                        VALUES (%s, %s, 'Running', NOW(), %s, %s)
                        """,
                        (run_id, today, empty_json, empty_deliverables),
                    )
            elif has_trigger:
                # Migration 007 schema
                cur.execute(
                    """
                    INSERT INTO pipeline_runs (run_id, trigger, status, started_at)
                    VALUES (%s, %s, 'running', NOW())
                    """,
                    (run_id, trigger),
                )
            else:
                # Minimal schema
                cur.execute(
                    """
                    INSERT INTO pipeline_runs (run_id, status, started_at)
                    VALUES (%s, 'running', NOW())
                    """,
                    (run_id,),
                )
        conn.commit()
        return run_id
    finally:
        conn.close()


def finish_run(run_id: str, status: str = "success") -> None:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        # Map 'success' to appropriate status based on schema
        # Check which status values the schema supports
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type FROM information_schema.columns 
                WHERE table_name = 'pipeline_runs' AND column_name = 'status'
            """)
            status_col = cur.fetchone()
            
            # Check for CHECK constraint to determine valid values
            cur.execute("""
                SELECT check_clause FROM information_schema.check_constraints
                WHERE constraint_name LIKE '%pipeline_runs%status%'
                LIMIT 1
            """)
            check_constraint = cur.fetchone()
            
            if check_constraint and 'Completed' in str(check_constraint[0]):
                # Full schema uses 'Completed', 'Failed', 'Running', 'Partial'
                mapped_status = "Completed" if status == "success" else ("Failed" if status == "failed" else status)
            else:
                # Migration 007 schema uses 'success', 'failed', 'running'
                mapped_status = status
            
            cur.execute(
                """
                UPDATE pipeline_runs
                SET completed_at = NOW(), status = %s
                WHERE run_id = %s
                """,
                (mapped_status, run_id),
            )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", action="store_true", help="Start a new run; print run_id")
    ap.add_argument("--finish", metavar="RUN_ID", help="Mark run finished (success)")
    ap.add_argument("--failed", action="store_true", help="Use with --finish to set status=failed")
    ap.add_argument("--trigger", default="manual", help="Trigger name for --start")
    args = ap.parse_args()

    if args.start:
        run_id = start_run(trigger=args.trigger)
        print(run_id)
        return
    if args.finish:
        status = "failed" if args.failed else "success"
        finish_run(args.finish, status=status)
        return
    ap.error("Use --start or --finish RUN_ID")


if __name__ == "__main__":
    main()
    sys.exit(0)
