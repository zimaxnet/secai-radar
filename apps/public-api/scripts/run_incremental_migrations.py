#!/usr/bin/env python3
"""
Run incremental migrations from apps/public-api/migrations/.
Each NNN_name.sql is run in sorted order. Use IF NOT EXISTS so they are idempotent.
Safe to run after the main schema or on an already-migrated DB.
"""

import os
import sys
import psycopg2
from pathlib import Path

_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def main() -> None:
    if not _MIGRATIONS_DIR.exists():
        print(f"No migrations dir: {_MIGRATIONS_DIR}")
        return

    # Run NNN_name.sql in order; skip 001 (placeholder) and comments-only files
    files = sorted(
        f for f in _MIGRATIONS_DIR.glob("*.sql")
        if f.name != "001_initial_schema.sql"  # placeholder, would yield empty query
    )
    if not files:
        print("No migration files found.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    try:
        for sql_file in files:
            with conn.cursor() as cur:
                with open(sql_file, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
            conn.commit()
            print(f"✅ Migrated: {sql_file.name}")
        print("✅ Incremental migrations complete")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
