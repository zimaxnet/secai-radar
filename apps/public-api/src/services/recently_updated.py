"""
Recently Updated service - business logic for recently-updated endpoint
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.server import MCPServer
from src.models.score_snapshot import ScoreSnapshot
from src.models.latest_score import LatestScore
from src.models.provider import Provider
from src.models.drift import DriftEvent


def get_recently_updated(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recently updated servers with their latest scores.
    Returns servers ordered by assessed_at DESC, with drift count for last 7 days.
    """
    # Query servers with latest scores, ordered by assessment time
    servers = (
        db.query(MCPServer, ScoreSnapshot, Provider)
        .select_from(MCPServer)
        .join(LatestScore, MCPServer.server_id == LatestScore.server_id)
        .join(ScoreSnapshot, LatestScore.score_id == ScoreSnapshot.score_id)
        .join(Provider, MCPServer.provider_id == Provider.provider_id)
        .filter(MCPServer.status == 'Active')
        .order_by(ScoreSnapshot.assessed_at.desc())
        .limit(limit)
        .all()
    )
    
    # Get server IDs for drift count query
    server_ids = [server.server_id for server, _, _ in servers]
    
    # Calculate drift count for last 7 days for each server
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    drift_counts = (
        db.query(
            DriftEvent.server_id,
            func.count(DriftEvent.drift_id).label('drift_count')
        )
        .filter(
            and_(
                DriftEvent.server_id.in_(server_ids),
                DriftEvent.detected_at >= seven_days_ago
            )
        )
        .group_by(DriftEvent.server_id)
        .all()
    )
    
    # Create drift count map
    drift_map = {server_id: count for server_id, count in drift_counts}
    
    # Calculate score deltas (24h) for each server
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    score_deltas = {}
    
    # Build a map of current scores from the already-fetched data
    current_scores_map = {server.server_id: float(score.trust_score) for server, score, _ in servers}
    
    # Get previous scores (most recent before 24h ago) for each server
    # For small limits (10-50), per-server queries are acceptable
    previous_scores_map = {}
    for server_id in server_ids:
        prev_score = (
            db.query(ScoreSnapshot.trust_score)
            .filter(ScoreSnapshot.server_id == server_id)
            .filter(ScoreSnapshot.assessed_at < one_day_ago)
            .order_by(ScoreSnapshot.assessed_at.desc())
            .first()
        )
        if prev_score:
            previous_scores_map[server_id] = float(prev_score[0])
    
    # Calculate deltas
    for server_id, current_score in current_scores_map.items():
        previous_score = previous_scores_map.get(server_id, current_score)
        score_deltas[server_id] = current_score - previous_score
    
    # Format results
    results: List[Dict[str, Any]] = []
    for server, score, provider in servers:
        # Get fail-fast and risk flags
        fail_fast_flags = score.fail_fast_flags if score.fail_fast_flags else []
        risk_flags = score.risk_flags if score.risk_flags else []
        all_flags = [f"fail-fast:{flag}" for flag in fail_fast_flags] + risk_flags
        
        results.append({
            "serverId": server.server_id,
            "serverSlug": server.server_slug,
            "serverName": server.server_name,
            "providerId": provider.provider_id,
            "providerName": provider.provider_name,
            "providerSlug": provider.primary_domain.split('.')[0] if provider.primary_domain else "",
            "categoryPrimary": server.category_primary or "",
            "trustScore": float(score.trust_score),
            "tier": score.tier,
            "evidenceConfidence": int(score.evidence_confidence),
            "lastAssessedAt": score.assessed_at.isoformat() if score.assessed_at else None,
            "scoreDelta24h": score_deltas.get(server.server_id, 0.0),
            "driftEvents7d": drift_map.get(server.server_id, 0),
            "driftCount7d": drift_map.get(server.server_id, 0),  # Alias for frontend compatibility
            "flags": all_flags,
        })
    
    return results
