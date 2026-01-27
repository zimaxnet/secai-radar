"""
Rankings service - business logic for rankings endpoint
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Dict, Any, List, Optional
from src.models.server import MCPServer
from src.models.score_snapshot import ScoreSnapshot
from src.models.latest_score import LatestScore
from src.models.provider import Provider


def get_rankings(
    db: Session,
    q: Optional[str] = None,
    category: Optional[str] = None,
    tier: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort: str = "trustScore"
) -> Dict[str, Any]:
    """
    Get rankings with filters, pagination, and sorting.
    Uses latest_scores + score_snapshots for latest score per server.
    """
    base = (
        db.query(MCPServer, ScoreSnapshot, Provider)
        .select_from(MCPServer)
        .join(LatestScore, MCPServer.server_id == LatestScore.server_id)
        .join(ScoreSnapshot, LatestScore.score_id == ScoreSnapshot.score_id)
        .join(Provider, MCPServer.provider_id == Provider.provider_id)
    )
    if tier:
        base = base.filter(ScoreSnapshot.tier == tier)
    if category:
        base = base.filter(MCPServer.category_primary == category)
    if q and q.strip():
        pat = f"%{q.strip()}%"
        base = base.filter(
            or_(
                MCPServer.server_name.ilike(pat),
                MCPServer.server_slug.ilike(pat),
            )
        )
    total = base.count()
    sort_col = {
        "trustScore": ScoreSnapshot.trust_score,
        "evidenceConfidence": ScoreSnapshot.evidence_confidence,
        "lastAssessedAt": ScoreSnapshot.assessed_at,
    }.get(sort, ScoreSnapshot.trust_score)
    rows = (
        base.order_by(sort_col.desc().nulls_last())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    servers: List[Dict[str, Any]] = []
    for server, score, provider in rows:
        servers.append({
            "serverId": server.server_id,
            "serverSlug": server.server_slug,
            "serverName": server.server_name,
            "providerId": server.provider_id,
            "providerName": provider.provider_name,
            "categoryPrimary": server.category_primary,
            "trustScore": float(score.trust_score),
            "tier": score.tier,
            "evidenceConfidence": int(score.evidence_confidence),
            "lastAssessedAt": score.assessed_at.isoformat() if score.assessed_at else None,
            "evidenceIds": [],  # optional; populated elsewhere if needed
        })
    return {
        "servers": servers,
        "total": total,
        "page": page,
        "pageSize": page_size,
    }
