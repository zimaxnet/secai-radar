#!/usr/bin/env python3
"""
Refresh latest_scores pointer table and latest_assessments_view.
Run after seeding or when score_snapshots change (e.g. after pipeline runs).
Uses DATABASE_URL like migrate.py/seed.py.
"""

import os
import sys
import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def refresh_latest_scores(conn) -> None:
    """Repopulate latest_scores from score_snapshots (one row per server, latest assessed_at)."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE latest_scores")
        cur.execute("""
            INSERT INTO latest_scores (server_id, score_id, updated_at)
            SELECT server_id, score_id, NOW()
            FROM (
                SELECT DISTINCT ON (server_id) server_id, score_id, assessed_at
                FROM score_snapshots
                ORDER BY server_id, assessed_at DESC
            ) sub
        """)
        conn.commit()
        n = cur.rowcount
    print(f"  Repopulated latest_scores ({n} rows)")


def refresh_materialized_view(conn) -> None:
    """Refresh latest_assessments_view."""
    with conn.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW latest_assessments_view")
        conn.commit()
    print("  Refreshed materialized view latest_assessments_view")


def main() -> int:
    try:
        conn = psycopg2.connect(DATABASE_URL)
        try:
            print("Refreshing latest projections...")
            refresh_latest_scores(conn)
            refresh_materialized_view(conn)
            print("✅ Done")
            return 0
        finally:
            conn.close()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
