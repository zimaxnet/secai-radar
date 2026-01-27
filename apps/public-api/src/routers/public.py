"""
Public API routes.

Verified badge and attestation follow the definition in docs/VERIFIED-DEFINITION.md
(via src.constants.attestation).
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database import get_db
from src.constants.attestation import (
    VERIFIED_RECENCY_DAYS,
    VERIFIED_MIN_EVIDENCE_CONFIDENCE,
    is_verified,
    build_attestation_envelope,
    record_integrity_digest,
)

router = APIRouter(prefix="/api/v1/public", tags=["public"])

METHODOLOGY_VERSION = "v1.0"


@router.get("/mcp/summary")
async def get_summary(
    window: str = Query("24h", regex="^(24h|7d|30d)$"),
    db: Session = Depends(get_db)
):
    """
    Get summary KPIs and highlights. Verified status uses evidenceConfidence >= 2
    and lastVerifiedAt within 7 days (see docs/VERIFIED-DEFINITION.md).
    Window: 24h, 7d, or 30d.
    """
    from src.services.summary import get_summary_data
    from src.middleware.redaction import redact_response
    
    data = get_summary_data(db, window)
    redacted_data = redact_response(data)
    now = datetime.utcnow()
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "window": window,
        "data": redacted_data,
    }


@router.get("/mcp/recently-updated")
async def get_recently_updated(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get recently updated servers. Frontend expects data.items."""
    from src.services.recently_updated import get_recently_updated as get_recently_updated_data
    from src.middleware.redaction import redact_response
    
    items = get_recently_updated_data(db, limit)
    redacted_items = redact_response(items)
    now = datetime.utcnow()
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": {"items": redacted_items if isinstance(redacted_items, list) else items},
    }


@router.get("/mcp/rankings")
async def get_rankings(
    q: Optional[str] = None,
    category: Optional[str] = None,
    tier: Optional[str] = Query(None, regex="^(A|B|C|D)$"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    sort: str = Query("trustScore", regex="^(trustScore|evidenceConfidence|lastAssessedAt)$"),
    db: Session = Depends(get_db)
):
    """Get rankings with filters and pagination. Verified: evidenceConfidence >= 2,
    lastVerifiedAt within 7 days (docs/VERIFIED-DEFINITION.md)."""
    from src.services.rankings import get_rankings as get_rankings_data
    from src.middleware.redaction import redact_response
    
    data = get_rankings_data(db, q, category, tier, page, pageSize, sort)
    redacted_data = redact_response(data)
    # Frontend expects data.items and meta.{total,page,pageSize}
    items = redacted_data.get("servers") or redacted_data.get("items") or []
    now = datetime.utcnow()
    for it in items:
        sid = it.get("serverId") or it.get("server_id") or ""
        ts = float(it.get("trustScore", it.get("trust_score", 0)) or 0)
        t = it.get("tier") or "D"
        eids = it.get("evidenceIds") or it.get("evidence_ids") or []
        it["integrityDigest"] = record_integrity_digest(sid, ts, t, eids, now)
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": {"items": items},
        "meta": {
            "total": redacted_data.get("total", 0),
            "page": redacted_data.get("page", 1),
            "pageSize": redacted_data.get("pageSize", pageSize),
        },
    }


@router.get("/mcp/servers/{idOrSlug}")
async def get_server(idOrSlug: str, db: Session = Depends(get_db)):
    """Get server detail by ID or slug. Verified badge follows docs/VERIFIED-DEFINITION.md
    (evidenceConfidence >= 2, lastVerifiedAt within 7 days). Optional integrityDigest (A3)."""
    from src.services.server import get_server_by_id_or_slug, get_latest_score, get_server_evidence_ids
    from src.middleware.redaction import redact_response

    server = get_server_by_id_or_slug(db, idOrSlug)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    score = get_latest_score(db, server.server_id)
    provider_name = getattr(server.provider, "provider_name", None) if getattr(server, "provider", None) else None
    trust_score = float(score.trust_score) if score else 0.0
    tier = (score.tier if score else "D") or "D"
    now = datetime.utcnow()
    evidence_ids = get_server_evidence_ids(db, server.server_id)
    integrity_digest = record_integrity_digest(
        server.server_id, trust_score, tier, evidence_ids, now
    )
    data = {
        "serverId": server.server_id,
        "serverSlug": server.server_slug or server.server_id,
        "serverName": server.server_name or server.server_slug or server.server_id,
        "providerId": server.provider_id,
        "providerName": provider_name,
        "trustScore": trust_score,
        "tier": tier,
        "evidenceConfidence": int(score.evidence_confidence) if score else 0,
        "lastAssessedAt": score.assessed_at.isoformat() if score and score.assessed_at else None,
        "domainScores": {},
        "enterpriseFit": (score.enterprise_fit if score else None) or "Experimental",
        "integrityDigest": integrity_digest,
    }
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": redact_response(data),
    }


@router.get("/mcp/servers/{idOrSlug}/evidence")
async def get_server_evidence(
    idOrSlug: str,
    db: Session = Depends(get_db)
):
    """Get server evidence list"""
    from src.services.server import get_server_by_id_or_slug, get_server_evidence
    from src.middleware.redaction import redact_evidence_item
    from src.middleware.redaction import redact_response
    
    server = get_server_by_id_or_slug(db, idOrSlug)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    evidence_data = get_server_evidence(db, server.server_id)
    
    # Redact evidence items
    redacted_items = [redact_evidence_item(item.__dict__) for item in evidence_data["evidenceItems"]]
    
    data = {
        "evidenceItems": redacted_items,
        "claims": [claim.__dict__ for claim in evidence_data["claims"]]
    }
    
    redacted_data = redact_response(data)
    now = datetime.utcnow()
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": redacted_data,
    }


@router.get("/mcp/servers/{idOrSlug}/drift")
async def get_server_drift(
    idOrSlug: str,
    window: str = Query("30d", regex="^(7d|30d|90d)$")
):
    """Get server drift timeline"""
    # TODO: Implement actual database query
    now = datetime.utcnow()
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": {"driftEvents": []},
    }


@router.get("/mcp/daily/{date}")
async def get_daily_brief(
    date: str,
    db: Session = Depends(get_db)
):
    """Get daily brief for a specific date (YYYY-MM-DD). Attestation and Verified
    criteria in docs/VERIFIED-DEFINITION.md."""
    from src.services.daily_brief import get_daily_brief as get_brief
    from datetime import datetime
    
    try:
        brief_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    brief = get_brief(db, brief_date)
    if not brief:
        raise HTTPException(status_code=404, detail="Daily brief not found for this date")
    
    data = {
        "briefId": brief.brief_id,
        "date": brief.date.isoformat(),
        "headline": brief.headline,
        "narrativeShort": brief.narrative_short,
        "narrativeLong": brief.narrative_long,
        "movers": brief.movers_json or [],
        "downgrades": brief.downgrades_json or [],
        "newEntrants": brief.new_entrants_json or [],
        "notableDrift": brief.notable_drift_json or [],
        "tipOfTheDay": brief.tip_of_the_day,
        "generatedAt": brief.generated_at.isoformat()
    }
    now = datetime.utcnow()
    return {
        "attestation": build_attestation_envelope(
            brief.methodology_version or METHODOLOGY_VERSION,
            as_of=now,
            assessment_run_id=None,
            evidence_bundle_version=None,
        ),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        "data": data,
    }


@router.get("/mcp/feed.xml")
async def get_rss_feed(db: Session = Depends(get_db)):
    """Get RSS/Atom feed. Items include provenance and integrityDigest per docs/VERIFIED-DEFINITION.md."""
    from src.services.feeds import generate_rss_feed
    from fastapi.responses import Response
    xml = generate_rss_feed(db)
    return Response(content=xml, media_type="application/rss+xml")


@router.get("/mcp/feed.json")
async def get_json_feed(db: Session = Depends(get_db)):
    """Get JSON Feed. Items include provenance and integrityDigest per
    docs/VERIFIED-DEFINITION.md and Pivot_Strategy_Reuse_Ideas."""
    from src.services.feeds import generate_json_feed
    
    feed = generate_json_feed(db)
    now = datetime.utcnow()
    return {
        "attestation": build_attestation_envelope(METHODOLOGY_VERSION, as_of=now),
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": now.isoformat(),
        **feed,
    }
