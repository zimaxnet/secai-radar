"""
Publisher Worker - Atomic publish with staging swap
"""

import os
import psycopg2
from datetime import datetime
from typing import Dict, Any, List
import json

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def validate_dataset(db) -> tuple[bool, List[str]]:
    """
    Validate dataset completeness before publishing
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    with db.cursor() as cur:
        # Check that all active servers have latest scores
        cur.execute("""
            SELECT COUNT(*) 
            FROM mcp_servers s
            LEFT JOIN latest_scores ls ON s.server_id = ls.server_id
            WHERE s.status = 'Active' AND ls.server_id IS NULL
        """)
        missing_scores = cur.fetchone()[0]
        if missing_scores > 0:
            errors.append(f"{missing_scores} active servers missing latest scores")
        
        # Check that latest scores reference valid score_snapshots
        cur.execute("""
            SELECT COUNT(*) 
            FROM latest_scores ls
            LEFT JOIN score_snapshots ss ON ls.score_id = ss.score_id
            WHERE ss.score_id IS NULL
        """)
        invalid_refs = cur.fetchone()[0]
        if invalid_refs > 0:
            errors.append(f"{invalid_refs} latest_scores reference invalid snapshots")
        
        # Check for null scores
        cur.execute("""
            SELECT COUNT(*) 
            FROM score_snapshots
            WHERE trust_score IS NULL OR tier IS NULL
        """)
        null_scores = cur.fetchone()[0]
        if null_scores > 0:
            errors.append(f"{null_scores} score snapshots have null values")
    
    return len(errors) == 0, errors


def flip_stable_pointer(db) -> bool:
    """
    Atomically flip the stable pointer to staging dataset
    
    This uses a transaction to ensure atomicity
    """
    try:
        with db.cursor() as cur:
            # In a real implementation, this would:
            # 1. Write new data to staging tables/partitions
            # 2. Validate counts
            # 3. Atomically update latest_scores pointers
            # 4. Refresh materialized views
            
            # For MVP, we'll update latest_scores based on most recent score_snapshots
            cur.execute("""
                INSERT INTO latest_scores (server_id, score_id, updated_at)
                SELECT 
                    server_id,
                    score_id,
                    NOW()
                FROM (
                    SELECT DISTINCT ON (server_id)
                        server_id,
                        score_id,
                        assessed_at
                    FROM score_snapshots
                    ORDER BY server_id, assessed_at DESC
                ) latest
                ON CONFLICT (server_id) 
                DO UPDATE SET 
                    score_id = EXCLUDED.score_id,
                    updated_at = EXCLUDED.updated_at
            """)
            
            # Refresh materialized view
            cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_assessments_view")
            
            db.commit()
            return True
    except Exception as e:
        db.rollback()
        print(f"Error flipping stable pointer: {e}")
        return False


def refresh_rankings_cache(db):
    """Refresh rankings cache for common filter combinations"""
    # TODO: Implement rankings cache refresh
    # For MVP, this is a placeholder
    pass


def publish() -> Dict[str, Any]:
    """
    Main publish function - validates and publishes dataset
    """
    conn = psycopg2.connect(DATABASE_URL)
    try:
        # Validate dataset
        is_valid, errors = validate_dataset(conn)
        
        if not is_valid:
            return {
                "success": False,
                "errors": errors,
                "message": "Dataset validation failed - keeping previous stable dataset"
            }
        
        # Flip stable pointer
        if not flip_stable_pointer(conn):
            return {
                "success": False,
                "errors": ["Failed to flip stable pointer"],
                "message": "Pointer flip failed - keeping previous stable dataset"
            }
        
        # Refresh cache
        refresh_rankings_cache(conn)
        
        return {
            "success": True,
            "publishedAt": datetime.utcnow().isoformat(),
            "message": "Dataset published successfully"
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = publish()
    print(json.dumps(result, indent=2))
