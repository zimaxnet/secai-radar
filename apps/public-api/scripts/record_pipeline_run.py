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
import psycopg2
from pathlib import Path

# same resolve as run_incremental_migrations
_SCRIPT_DIR = Path(__file__).resolve().parent
_MIGRATIONS_DIR = _SCRIPT_DIR.parent / "migrations"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar",
)


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
            cur.execute(
                """
                INSERT INTO pipeline_runs (run_id, trigger, status, started_at)
                VALUES (%s, %s, 'running', NOW())
                """,
                (run_id, trigger),
            )
        conn.commit()
        return run_id
    finally:
        conn.close()


def finish_run(run_id: str, status: str = "success") -> None:
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pipeline_runs
                SET completed_at = NOW(), status = %s
                WHERE run_id = %s
                """,
                (status, run_id),
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
