"""
Scorer Worker - Trust Score calculation
Computes scores using packages/scoring library
"""

import os
import sys
import psycopg2
from datetime import datetime
from typing import Dict, Any, List
import json

# Add scoring package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../packages/scoring/src'))

from scoring import calculate_trust_score, calculate_evidence_confidence
from scoring.models import EvidenceItem, ExtractedClaim, EvidenceType, ClaimType

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)

METHODOLOGY_VERSION = "v1.0"


def get_server_evidence(db, server_id: str) -> tuple[List[EvidenceItem], List[ExtractedClaim]]:
    """Get evidence items and claims for a server"""
    evidence_items = []
    claims = []
    
    with db.cursor() as cur:
        # Get evidence items
        cur.execute("""
            SELECT evidence_id, type, url, confidence, source_url, captured_at
            FROM evidence_items
            WHERE server_id = %s
        """, (server_id,))
        
        for row in cur.fetchall():
            evidence_items.append(EvidenceItem(
                evidence_id=row[0],
                type=EvidenceType(row[1]),
                url=row[2],
                confidence=row[3],
                source_url=row[4],
                claims=[]  # Will be populated separately
            ))
        
        # Get claims
        evidence_ids = [item.evidence_id for item in evidence_items]
        if evidence_ids:
            cur.execute("""
                SELECT claim_id, evidence_id, claim_type, value_json, confidence, source_url
                FROM evidence_claims
                WHERE evidence_id = ANY(%s)
            """, (evidence_ids,))
            
            for row in cur.fetchall():
                claims.append(ExtractedClaim(
                    claim_id=row[0],
                    evidence_id=row[1],
                    claim_type=ClaimType(row[2]),
                    value=row[3],
                    confidence=row[4],
                    source_url=row[5],
                    source_evidence_id=row[1]
                ))
    
    # Attach claims to evidence items
    for item in evidence_items:
        item.claims = [c for c in claims if c.evidence_id == item.evidence_id]
    
    return evidence_items, claims


def store_score_snapshot(db, server_id: str, score_result) -> str:
    """Store score snapshot"""
    score_id = hashlib.sha256(
        f"{server_id}|{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO score_snapshots (
                score_id, server_id, methodology_version, assessed_at,
                d1, d2, d3, d4, d5, d6,
                trust_score, tier, enterprise_fit, evidence_confidence,
                fail_fast_flags, risk_flags, explainability_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            score_id,
            server_id,
            METHODOLOGY_VERSION,
            datetime.utcnow(),
            float(score_result.domain_scores.d1),
            float(score_result.domain_scores.d2),
            float(score_result.domain_scores.d3),
            float(score_result.domain_scores.d4),
            float(score_result.domain_scores.d5),
            float(score_result.domain_scores.d6),
            float(score_result.trust_score.trust_score),
            score_result.trust_score.tier.value,
            score_result.trust_score.enterprise_fit.value,
            score_result.trust_score.evidence_confidence.value,
            json.dumps([f.dict() for f in score_result.fail_fast_flags]),
            json.dumps([f.dict() for f in score_result.risk_flags]),
            json.dumps(score_result.explainability)
        ))
        db.commit()
    
    return score_id


def update_latest_score(db, server_id: str, score_id: str):
    """Update latest_scores pointer"""
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO latest_scores (server_id, score_id, updated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (server_id)
            DO UPDATE SET score_id = EXCLUDED.score_id, updated_at = EXCLUDED.updated_at
        """, (server_id, score_id, datetime.utcnow()))
        db.commit()


def score_server(db, server_id: str) -> Dict[str, Any]:
    """Score a single server"""
    try:
        # Get evidence
        evidence_items, claims = get_server_evidence(db, server_id)
        
        # Calculate score
        score_result = calculate_trust_score(evidence_items, claims, METHODOLOGY_VERSION)
        
        # Store snapshot
        score_id = store_score_snapshot(db, server_id, score_result)
        
        # Update latest pointer (staging - will be flipped by publisher)
        # For MVP, update directly
        update_latest_score(db, server_id, score_id)
        
        return {
            "success": True,
            "server_id": server_id,
            "score_id": score_id,
            "trust_score": float(score_result.trust_score.trust_score),
            "tier": score_result.trust_score.tier.value
        }
    except Exception as e:
        return {
            "success": False,
            "server_id": server_id,
            "error": str(e)
        }


def run_scorer():
    """
    Main scorer function - score all active servers
    """
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        # Get active servers
        with conn.cursor() as cur:
            cur.execute("""
                SELECT server_id FROM mcp_servers
                WHERE status = 'Active'
            """)
            server_ids = [row[0] for row in cur.fetchall()]
        
        results = []
        for server_id in server_ids:
            result = score_server(conn, server_id)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "serversScored": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "completedAt": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Scorer error: {e}")
        return {
            "success": False,
            "error": str(e),
            "completedAt": datetime.utcnow().isoformat()
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = run_scorer()
    print(json.dumps(result, indent=2))
