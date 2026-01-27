"""
Rankings service - business logic for rankings endpoint
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, case, desc, cast, Integer
from typing import Dict, Any, List, Optional
import json
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
        .filter(MCPServer.status == 'Active')  # Only show active servers in rankings
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
    
    # Multi-factor sorting:
    # 1. Primary: trust_score (or user-specified sort)
    # 2. Secondary: evidence_confidence
    # 3. Tertiary: source_provenance (Official Registry first)
    # 4. Quaternary: assessed_at (recency)
    
    # Determine primary sort column
    primary_sort = {
        "trustScore": ScoreSnapshot.trust_score,
        "evidenceConfidence": ScoreSnapshot.evidence_confidence,
        "lastAssessedAt": ScoreSnapshot.assessed_at,
    }.get(sort, ScoreSnapshot.trust_score)
    
    # Create provenance priority for tertiary sort
    # Official Registry = 1 (highest), MCPAnvil = 2, Other = 3
    provenance_priority = case(
        (
            MCPServer.metadata_json['source_provenance'].astext == 'Official Registry',
            1
        ),
        (
            MCPServer.metadata_json['source_provenance'].astext == 'MCPAnvil',
            2
        ),
        else_=3
    )
    
    # Extract popularity signals for quaternary sort (GitHub stars)
    # Handle missing popularity_signals gracefully with default 0
    # Use safe JSONB path extraction with null handling
    popularity_stars = case(
        (
            MCPServer.metadata_json['popularity_signals']['github']['stars'].astext.isnot(None),
            cast(MCPServer.metadata_json['popularity_signals']['github']['stars'].astext, Integer)
        ),
        else_=0
    )
    
    # Apply multi-factor ordering
    rows = (
        base.order_by(
            primary_sort.desc().nulls_last(),  # Primary sort
            ScoreSnapshot.evidence_confidence.desc().nulls_last(),  # Secondary
            provenance_priority.asc().nulls_last(),  # Tertiary (lower number = higher priority)
            popularity_stars.desc().nulls_last(),  # Quaternary (popularity: stars)
            ScoreSnapshot.assessed_at.desc().nulls_last()  # Quinary (recency)
        )
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
