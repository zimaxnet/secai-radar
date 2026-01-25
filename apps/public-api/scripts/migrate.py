#!/usr/bin/env python3
"""
Database migration script
"""

import os
import sys
import psycopg2
from pathlib import Path

# Get database connection from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def run_migration(sql_file: Path):
    """Run a SQL migration file"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            with open(sql_file, 'r') as f:
                cur.execute(f.read())
            conn.commit()
        print(f"✅ Migrated: {sql_file.name}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error migrating {sql_file.name}: {e}")
        raise
    finally:
        conn.close()


def main():
    """Run all migrations"""
    schema_file = Path(__file__).parent.parent.parent / "docs" / "implementation" / "database-schema.sql"
    
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)
    
    print(f"Running migration from: {schema_file}")
    run_migration(schema_file)
    print("✅ Migration complete")


if __name__ == "__main__":
    main()
