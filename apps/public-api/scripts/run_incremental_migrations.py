#!/usr/bin/env python3
"""
Run incremental migrations from apps/public-api/migrations/.
Each NNN_name.sql is run in sorted order. Use IF NOT EXISTS so they are idempotent.
Safe to run after the main schema or on an already-migrated DB.
"""

import os
import sys
import psycopg2
import subprocess
from pathlib import Path

_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

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
    print(f"⚠️  DATABASE_URL not set. Using default: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    print("   Set DATABASE_URL or use Azure CLI + Key Vault (secai-radar-kv / database-url)")


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
