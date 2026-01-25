"""
Public API routes
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/public", tags=["public"])

METHODOLOGY_VERSION = "v1.0"


@router.get("/mcp/summary")
async def get_summary(
    window: str = Query("24h", regex="^(24h|7d|30d)$"),
    db: Session = Depends(get_db)
):
    """
    Get summary KPIs and highlights
    
    Window: 24h, 7d, or 30d
    """
    from src.services.summary import get_summary_data
    from src.middleware.redaction import redact_response
    
    data = get_summary_data(db, window)
    redacted_data = redact_response(data)
    
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        "window": window,
        "data": redacted_data
    }


@router.get("/mcp/recently-updated")
async def get_recently_updated(limit: int = Query(10, ge=1, le=100)):
    """Get recently updated servers"""
    # TODO: Implement actual database query
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        "data": {
            "servers": []
        }
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
    """Get rankings with filters and pagination"""
    from src.services.rankings import get_rankings as get_rankings_data
    from src.middleware.redaction import redact_response
    
    data = get_rankings_data(db, q, category, tier, page, pageSize, sort)
    redacted_data = redact_response(data)
    
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        "data": redacted_data
    }


@router.get("/mcp/servers/{idOrSlug}")
async def get_server(idOrSlug: str):
    """Get server detail by ID or slug"""
    # TODO: Implement actual database query
    raise HTTPException(status_code=404, detail="Server not found")


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
    
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        "data": redacted_data
    }


@router.get("/mcp/servers/{idOrSlug}/drift")
async def get_server_drift(
    idOrSlug: str,
    window: str = Query("30d", regex="^(7d|30d|90d)$")
):
    """Get server drift timeline"""
    # TODO: Implement actual database query
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        "data": {
            "driftEvents": []
        }
    }


@router.get("/mcp/daily/{date}")
async def get_daily_brief(
    date: str,
    db: Session = Depends(get_db)
):
    """Get daily brief for a specific date (YYYY-MM-DD)"""
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
    
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        "data": data
    }


@router.get("/mcp/feed.xml")
async def get_rss_feed():
    """Get RSS/Atom feed"""
    # TODO: Implement RSS feed generation
    from fastapi.responses import Response
    return Response(
        content='<?xml version="1.0"?><rss version="2.0"><channel><title>SecAI Radar MCP</title></channel></rss>',
        media_type="application/rss+xml"
    )


@router.get("/mcp/feed.json")
async def get_json_feed(db: Session = Depends(get_db)):
    """Get JSON Feed"""
    from src.services.feeds import generate_json_feed
    
    feed = generate_json_feed(db)
    return {
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat(),
        **feed
    }
