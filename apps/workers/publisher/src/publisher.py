"""
Publisher Worker - Atomic publish with staging swap (T-051, T-076).
Validates, flips stable pointers, refreshes rankings_cache, ensures feeds see latest brief.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def _staging_exists(db) -> bool:
    with db.cursor() as cur:
        cur.execute("""
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'latest_scores_staging'
        """)
        return cur.fetchone() is not None


def validate_dataset(db) -> tuple[bool, List[str]]:
    """Validate stable latest_scores (used when no staging). Returns (is_valid, errors)."""
    errors = []
    with db.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM mcp_servers s
            LEFT JOIN latest_scores ls ON s.server_id = ls.server_id
            WHERE s.status = 'Active' AND ls.server_id IS NULL
        """)
        if cur.fetchone()[0] > 0:
            errors.append("Active servers missing in latest_scores")
        cur.execute("""
            SELECT COUNT(*) FROM latest_scores ls
            LEFT JOIN score_snapshots ss ON ls.score_id = ss.score_id
            WHERE ss.score_id IS NULL
        """)
        if cur.fetchone()[0] > 0:
            errors.append("latest_scores reference invalid snapshots")
    return len(errors) == 0, errors


def validate_staging(db) -> tuple[bool, List[str]]:
    """
    Validate latest_scores_staging before flipping (T-051).
    Failure keeps previous stable dataset live.
    Returns (is_valid, error_messages).
    """
    errors = []
    if not _staging_exists(db):
        return False, ["latest_scores_staging table does not exist"]
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM latest_scores_staging")
        if cur.fetchone()[0] == 0:
            errors.append("Staging is empty")
        cur.execute("""
            SELECT COUNT(*) FROM mcp_servers s
            LEFT JOIN latest_scores_staging st ON s.server_id = st.server_id
            WHERE s.status = 'Active' AND st.server_id IS NULL
        """)
        missing = cur.fetchone()[0]
        if missing > 0:
            errors.append(f"{missing} active servers missing in staging")
        cur.execute("""
            SELECT COUNT(*) FROM latest_scores_staging st
            LEFT JOIN score_snapshots ss ON st.score_id = ss.score_id
            WHERE ss.score_id IS NULL
        """)
        invalid = cur.fetchone()[0]
        if invalid > 0:
            errors.append(f"{invalid} staging rows reference invalid score_snapshots")
    return len(errors) == 0, errors


def flip_stable_pointer(db) -> bool:
    """
    Atomically replace latest_scores with latest_scores_staging (T-051).
    Call after validate_staging(). On failure, stable dataset is unchanged.
    """
    if not _staging_exists(db):
        return False
    try:
        with db.cursor() as cur:
            cur.execute("TRUNCATE latest_scores")
            cur.execute("""
                INSERT INTO latest_scores (server_id, score_id, updated_at)
                SELECT server_id, score_id, updated_at FROM latest_scores_staging
            """)
            cur.execute("REFRESH MATERIALIZED VIEW latest_assessments_view")
            db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error flipping stable pointer: {e}")
        return False


def _rankings_cache_exists(db) -> bool:
    with db.cursor() as cur:
        cur.execute("""
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'rankings_cache'
        """)
        return cur.fetchone() is not None


def _fetch_rankings_payload(cur, tier: Optional[str], page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """Build rankings-shaped payload via raw SQL (mirrors rankings.get_rankings)."""
    where = "AND ss.tier = %(tier)s" if tier else "AND 1=1"
    params = {"tier": tier, "limit": page_size, "offset": (page - 1) * page_size}
    cur.execute(
        f"""
        WITH ranked AS (
            SELECT s.server_id, s.server_slug, s.server_name, s.provider_id, p.provider_name,
                   s.category_primary, ss.trust_score, ss.tier, ss.evidence_confidence, ss.assessed_at
            FROM mcp_servers s
            JOIN latest_scores ls ON s.server_id = ls.server_id
            JOIN score_snapshots ss ON ls.score_id = ss.score_id
            JOIN providers p ON s.provider_id = p.provider_id
            WHERE s.status = 'Active' {where}
        )
        SELECT COUNT(*) OVER () AS total,
               server_id, server_slug, server_name, provider_id, provider_name,
               category_primary, trust_score, tier, evidence_confidence, assessed_at
        FROM ranked
        ORDER BY trust_score DESC NULLS LAST
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        params,
    )
    rows = cur.fetchall()
    total = int(rows[0][0]) if rows else 0
    servers = []
    for r in rows:
        servers.append({
            "serverId": r[1],
            "serverSlug": r[2],
            "serverName": r[3],
            "providerId": r[4],
            "providerName": r[5],
            "categoryPrimary": r[6],
            "trustScore": float(r[7]) if r[7] is not None else 0,
            "tier": r[8],
            "evidenceConfidence": int(r[9]) if r[9] is not None else 0,
            "lastAssessedAt": r[10].isoformat() if r[10] and hasattr(r[10], "isoformat") else None,
            "evidenceIds": [],
        })
    return {"servers": servers, "total": total, "page": page, "pageSize": page_size}


def refresh_rankings_cache(db) -> Tuple[int, List[str]]:
    """
    Refresh rankings_cache for common filter combos (T-076).
    Uses window '24h'; fills default + tier A/B/C/D. Returns (count_updated, errors).
    """
    if not _rankings_cache_exists(db):
        return 0, []
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=24)
    window = "24h"
    combos = [{"tier": None}, {"tier": "A"}, {"tier": "B"}, {"tier": "C"}, {"tier": "D"}]
    updated = 0
    errors = []
    with db.cursor() as cur:
        for combo in combos:
            try:
                payload = _fetch_rankings_payload(cur, combo.get("tier"))
                filters_hash = hashlib.sha256(
                    json.dumps({"tier": combo.get("tier"), "sort": "trustScore"}, sort_keys=True).encode()
                ).hexdigest()
                cur.execute(
                    """
                    INSERT INTO rankings_cache ("window", filters_hash, payload_json, generated_at, expires_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT ("window", filters_hash)
                    DO UPDATE SET payload_json = EXCLUDED.payload_json,
                                  generated_at = EXCLUDED.generated_at,
                                  expires_at = EXCLUDED.expires_at
                    """,
                    (window, filters_hash, json.dumps(payload), now, expires),
                )
                updated += 1
            except Exception as e:
                errors.append(f"rankings_cache {combo}: {e}")
    return updated, errors


def publish() -> Dict[str, Any]:
    """
    Validate and publish. Uses staging when latest_scores_staging exists and passes
    validate_staging(); otherwise no-op or validate stable only (T-051).
    """
    import sys
    conn = psycopg2.connect(DATABASE_URL)
    try:
        if _staging_exists(conn):
            print("Publisher: Staging table exists, validating...", file=sys.stderr)
            is_valid, errors = validate_staging(conn)
            if not is_valid:
                error_msg = f"Staging validation failed: {', '.join(errors)}"
                print(f"Publisher: {error_msg}", file=sys.stderr)
                return {
                    "success": False,
                    "errors": errors,
                    "message": "Staging validation failed - keeping previous stable dataset",
                }
            print("Publisher: Staging validation passed, flipping to stable...", file=sys.stderr)
            if not flip_stable_pointer(conn):
                error_msg = "Failed to flip stable pointer"
                print(f"Publisher: {error_msg}", file=sys.stderr)
                return {
                    "success": False,
                    "errors": ["Failed to flip stable pointer"],
                    "message": "Pointer flip failed - keeping previous stable dataset",
                }
            print("Publisher: Staging flipped to stable successfully", file=sys.stderr)
        else:
            print("Publisher: No staging table, validating stable dataset...", file=sys.stderr)
            is_valid, errors = validate_dataset(conn)
            if not is_valid:
                error_msg = f"Dataset validation failed: {', '.join(errors)}"
                print(f"Publisher: {error_msg}", file=sys.stderr)
                return {
                    "success": False,
                    "errors": errors,
                    "message": "Dataset validation failed",
                }
        print("Publisher: Refreshing rankings cache...", file=sys.stderr)
        cache_updated, cache_errors = refresh_rankings_cache(conn)
        if cache_updated:
            conn.commit()
            print(f"Publisher: Rankings cache refreshed ({cache_updated} entries)", file=sys.stderr)
        if cache_errors:
            print(f"Publisher: Rankings cache warnings: {cache_errors}", file=sys.stderr)
        out = {
            "success": True,
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "message": "Dataset published successfully",
            "rankingsCacheRefreshed": cache_updated,
        }
        if cache_errors:
            out["rankingsCacheWarnings"] = cache_errors
        return out
    finally:
        conn.close()


if __name__ == "__main__":
    result = publish()
    print(json.dumps(result, indent=2))
