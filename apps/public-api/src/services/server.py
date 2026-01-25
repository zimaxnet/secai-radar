"""
Server service - business logic for server endpoints
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from src.models.server import MCPServer
from src.models.score_snapshot import ScoreSnapshot
from src.models.evidence import EvidenceItem, ExtractedClaim
from src.models.drift import DriftEvent


def get_server_by_id_or_slug(db: Session, id_or_slug: str) -> Optional[MCPServer]:
    """Get server by ID or slug"""
    # Try ID first
    server = db.query(MCPServer).filter(MCPServer.server_id == id_or_slug).first()
    if server:
        return server
    
    # Try slug
    server = db.query(MCPServer).filter(MCPServer.server_slug == id_or_slug).first()
    return server


def get_latest_score(db: Session, server_id: str) -> Optional[ScoreSnapshot]:
    """Get latest score snapshot for a server"""
    # TODO: Use latest_scores pointer table or materialized view
    return db.query(ScoreSnapshot).filter(
        ScoreSnapshot.server_id == server_id
    ).order_by(ScoreSnapshot.assessed_at.desc()).first()


def get_server_evidence(db: Session, server_id: str) -> Dict[str, Any]:
    """Get evidence items and claims for a server"""
    evidence_items = db.query(EvidenceItem).filter(
        EvidenceItem.server_id == server_id
    ).all()
    
    evidence_ids = [item.evidence_id for item in evidence_items]
    claims = db.query(ExtractedClaim).filter(
        ExtractedClaim.evidence_id.in_(evidence_ids)
    ).all() if evidence_ids else []
    
    return {
        "evidenceItems": evidence_items,
        "claims": claims
    }


def get_server_drift(
    db: Session,
    server_id: str,
    window_days: int = 30
) -> List[DriftEvent]:
    """Get drift events for a server within time window"""
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    
    return db.query(DriftEvent).filter(
        and_(
            DriftEvent.server_id == server_id,
            DriftEvent.detected_at >= cutoff
        )
    ).order_by(DriftEvent.detected_at.desc()).all()
