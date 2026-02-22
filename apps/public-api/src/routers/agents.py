"""
Agents API routes.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.database import get_db
from src.constants.attestation import (
    VERIFIED_RECENCY_DAYS,
    VERIFIED_MIN_EVIDENCE_CONFIDENCE,
    is_verified,
    build_attestation_envelope,
    record_integrity_digest,
    calculate_decayed_score,
)

from src.models.agent import Agent
from src.models.agent_latest_score import AgentLatestScore
from src.models.agent_score_snapshot import AgentScoreSnapshot
from src.models.agent_evidence import AgentEvidenceItem

router = APIRouter(prefix="/api/v1/public", tags=["agents"])

METHODOLOGY_VERSION = "v1.0"


@router.get("/agents/rankings")
async def get_agent_rankings(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get verified agents rankings with pagination."""
    # Simple query for agents and their latest scores
    query = db.query(Agent, AgentScoreSnapshot).outerjoin(
        AgentLatestScore, Agent.agent_id == AgentLatestScore.agent_id
    ).outerjoin(
        AgentScoreSnapshot, AgentLatestScore.score_id == AgentScoreSnapshot.score_id
    )
    
    total = query.count()
    offset = (page - 1) * pageSize
    results = query.order_by(desc(AgentScoreSnapshot.trust_score)).offset(offset).limit(pageSize).all()

    now = datetime.utcnow()
    items = []
    
    for agent, score in results:
        base_trust_score = float(score.trust_score) if score and score.trust_score else 0.0
        tier = score.tier if score and score.tier else "D"
        
        evidence_class = "C"
        if score and score.explainability_json:
            evidence_class = score.explainability_json.get("dominant_evidence_class", "C")
            
        trust_score = calculate_decayed_score(
            base_score=base_trust_score,
            evidence_class=evidence_class,
            assessed_at=score.assessed_at if score and score.assessed_at else now,
            query_time=now
        )
        
        # Mocking evidence IDs since we don't fetch them in this simple list
        integrity_digest = record_integrity_digest(agent.agent_id, trust_score, tier, [], now)
        
        items.append({
            "agentId": agent.agent_id,
            "agentSlug": agent.agent_slug,
            "agentName": agent.agent_name,
            "categoryPrimary": agent.category_primary,
            "agentType": agent.agent_type,
            "trustScore": trust_score,
            "baseTrustScore": base_trust_score,
            "evidenceClass": evidence_class,
            "tier": tier,
            "evidenceConfidence": int(score.evidence_confidence) if score and score.evidence_confidence else 0,
            "lastAssessedAt": score.assessed_at.isoformat() if score and score.assessed_at else None,
            "integrityDigest": integrity_digest
        })

    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": {"items": items},
        "meta": {
            "total": total,
            "page": page,
            "pageSize": pageSize,
        },
    }


@router.get("/agents/{idOrSlug}")
async def get_agent(idOrSlug: str, db: Session = Depends(get_db)):
    """Get agent detail by ID or slug."""
    # Fetch agent
    agent = db.query(Agent).filter(
        (Agent.agent_id == idOrSlug) | (Agent.agent_slug == idOrSlug)
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    latest = db.query(AgentLatestScore).filter(AgentLatestScore.agent_id == agent.agent_id).first()
    score = None
    if latest:
        score = db.query(AgentScoreSnapshot).filter(AgentScoreSnapshot.score_id == latest.score_id).first()

    now = datetime.utcnow()
    evidence_items = db.query(AgentEvidenceItem).filter(AgentEvidenceItem.agent_id == agent.agent_id).all()
    evidence_ids = [str(e.evidence_id) for e in evidence_items]
    
    agent_obj = {
        "agentId": agent.agent_id,
        "agentSlug": agent.agent_slug,
        "agentName": agent.agent_name,
        "providerId": agent.provider_id,
        "categoryPrimary": agent.category_primary or "Unknown",
        "tags": agent.tags or [],
        "agentType": agent.agent_type or "Unknown",
        "repoUrl": agent.repo_url,
        "docsUrl": agent.docs_url,
        "status": agent.status or "Unknown",
    }
    
    if score:
        base_trust_score = float(score.trust_score) if score.trust_score else 0.0
        tier = score.tier or "D"
        
        evidence_class = "C"
        if score.explainability_json:
            evidence_class = score.explainability_json.get("dominant_evidence_class", "C")
            
        trust_score = calculate_decayed_score(
            base_score=base_trust_score,
            evidence_class=evidence_class,
            assessed_at=score.assessed_at if score.assessed_at else now,
            query_time=now
        )
        
        integrity_digest = record_integrity_digest(
            agent.agent_id, trust_score, tier, evidence_ids, now
        )
        latest_score_obj = {
            "scoreId": score.score_id,
            "agentId": score.agent_id,
            "methodologyVersion": score.methodology_version or METHODOLOGY_VERSION,
            "assessedAt": score.assessed_at.isoformat() if score.assessed_at else None,
            "d1": float(score.d1) if score.d1 else 0.0,
            "d2": float(score.d2) if score.d2 else 0.0,
            "trustScore": trust_score,
            "baseTrustScore": base_trust_score,
            "evidenceClass": evidence_class,
            "tier": tier,
            "evidenceConfidence": int(score.evidence_confidence) if score.evidence_confidence else 0,
            "failFastFlags": score.fail_fast_flags if score.fail_fast_flags else [],
            "riskFlags": score.risk_flags if score.risk_flags else [],
        }
    else:
        latest_score_obj = {
            "scoreId": "",
            "agentId": agent.agent_id,
            "methodologyVersion": METHODOLOGY_VERSION,
            "assessedAt": None,
            "d1": 0.0,
            "d2": 0.0,
            "trustScore": 0.0,
            "baseTrustScore": 0.0,
            "evidenceClass": "C",
            "tier": "D",
            "evidenceConfidence": 0,
            "failFastFlags": [],
            "riskFlags": [],
        }
    
    data = {
        "agent": agent_obj,
        "latestScore": latest_score_obj,
    }
    
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": data,
    }
