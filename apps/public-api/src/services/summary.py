"""
Summary service - business logic for summary endpoint
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.server import MCPServer
from src.models.score_snapshot import ScoreSnapshot
from src.models.latest_score import LatestScore
from src.models.provider import Provider
from src.models.daily_brief import DailyBrief


def _enrich_server_data(
    db: Session,
    items: List[Dict[str, Any]],
    server_id_key: str = "server_id"
) -> List[Dict[str, Any]]:
    """
    Enrich items with server names and provider names from database.
    """
    if not items:
        return []
    
    # Get all unique server IDs
    server_ids = [item.get(server_id_key) for item in items if item.get(server_id_key)]
    if not server_ids:
        return items
    
    # Query servers with providers
    servers = (
        db.query(MCPServer, Provider)
        .join(Provider, MCPServer.provider_id == Provider.provider_id)
        .filter(MCPServer.server_id.in_(server_ids))
        .all()
    )
    
    # Create lookup map
    server_map = {
        server.server_id: {
            "serverName": server.server_name,
            "serverSlug": server.server_slug,
            "providerName": provider.provider_name,
            "providerId": provider.provider_id,
            "providerSlug": provider.primary_domain.split('.')[0] if provider.primary_domain else "",
        }
        for server, provider in servers
    }
    
    # Enrich items
    enriched = []
    for item in items:
        server_id = item.get(server_id_key)
        if server_id and server_id in server_map:
            enriched_item = item.copy()
            enriched_item.update(server_map[server_id])
            enriched.append(enriched_item)
        else:
            # Keep item even if server not found (shouldn't happen, but be safe)
            # Add placeholder values
            enriched_item = item.copy()
            enriched_item.setdefault("serverName", "Unknown")
            enriched_item.setdefault("serverSlug", "")
            enriched_item.setdefault("providerName", "Unknown")
            enriched_item.setdefault("providerId", "")
            enriched_item.setdefault("providerSlug", "")
            enriched.append(enriched_item)
    
    return enriched


def get_summary_data(db: Session, window: str) -> Dict[str, Any]:
    """
    Get summary KPIs and highlights for a given time window.
    Shape matches frontend SummaryResponse (serversTracked, topMovers, etc.).
    """
    # Calculate window cutoff (not used for counts, but available for filtering)
    if window == "24h":
        delta = timedelta(days=1)
    elif window == "7d":
        delta = timedelta(days=7)
    else:
        delta = timedelta(days=30)
    cutoff_time = datetime.utcnow() - delta

    # 1. Query active servers count
    servers_tracked = db.query(MCPServer).filter(MCPServer.status == 'Active').count()
    
    # 2. Query providers count
    providers_tracked = db.query(Provider).count()
    
    # 3. Query tier distribution from latest scores
    tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    tier_results = (
        db.query(ScoreSnapshot.tier, func.count())
        .join(LatestScore, ScoreSnapshot.score_id == LatestScore.score_id)
        .join(MCPServer, LatestScore.server_id == MCPServer.server_id)
        .filter(MCPServer.status == 'Active')
        .group_by(ScoreSnapshot.tier)
        .all()
    )
    for tier, count in tier_results:
        if tier in tier_counts:
            tier_counts[tier] = count
    
    # 4. Query evidence confidence distribution
    evidence_counts = {"0": 0, "1": 0, "2": 0, "3": 0}
    evidence_results = (
        db.query(ScoreSnapshot.evidence_confidence, func.count())
        .join(LatestScore, ScoreSnapshot.score_id == LatestScore.score_id)
        .join(MCPServer, LatestScore.server_id == MCPServer.server_id)
        .filter(MCPServer.status == 'Active')
        .group_by(ScoreSnapshot.evidence_confidence)
        .all()
    )
    for confidence, count in evidence_results:
        confidence_str = str(int(confidence)) if confidence is not None else "0"
        if confidence_str in evidence_counts:
            evidence_counts[confidence_str] = count
    
    # 5. Query fail-fast count (servers with any fail-fast flags)
    # Get all active servers with scores, then filter in Python (simpler than JSONB query)
    all_scored_servers = (
        db.query(MCPServer, ScoreSnapshot)
        .join(LatestScore, MCPServer.server_id == LatestScore.server_id)
        .join(ScoreSnapshot, LatestScore.score_id == ScoreSnapshot.score_id)
        .filter(MCPServer.status == 'Active')
        .all()
    )
    fail_fast_count = sum(
        1 for server, score in all_scored_servers
        if score.fail_fast_flags and len(score.fail_fast_flags) > 0
    )
    
    # 6. Get latest daily brief and extract movers/downgrades/newEntrants/notableDrift
    latest_brief = db.query(DailyBrief).order_by(DailyBrief.date.desc()).first()
    
    top_movers: List[Dict[str, Any]] = []
    top_downgrades: List[Dict[str, Any]] = []
    new_entrants: List[Dict[str, Any]] = []
    notable_drift: List[Dict[str, Any]] = []
    
    if latest_brief and latest_brief.payload_json:
        # Handle JSONB - it might be a dict already or a string
        payload = latest_brief.payload_json
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                payload = {}
        
        # Extract movers
        if isinstance(payload, dict):
            movers_raw = payload.get("movers", [])
            if movers_raw:
                top_movers = _enrich_server_data(db, movers_raw, "server_id")
                # Format for frontend: ensure serverName, providerName, delta, score fields
                top_movers = [
                    {
                        "serverId": m.get("server_id"),
                        "serverName": m.get("serverName", "Unknown"),
                        "serverSlug": m.get("serverSlug", ""),
                        "providerName": m.get("providerName", "Unknown"),
                        "providerId": m.get("providerId", ""),
                        "scoreDelta": float(m.get("delta", 0)),
                        "trustScore": float(m.get("trust_score", 0)),
                        "tier": m.get("tier", "D"),
                        "permalink": f"/mcp/servers/{m.get('serverSlug', m.get('server_id', ''))}",
                    }
                    for m in top_movers[:10]  # Limit to top 10
                ]
            
            # Extract downgrades
            downgrades_raw = payload.get("downgrades", [])
            if downgrades_raw:
                top_downgrades = _enrich_server_data(db, downgrades_raw, "server_id")
                # Format for frontend
                top_downgrades = [
                    {
                        "serverId": d.get("server_id"),
                        "serverName": d.get("serverName", "Unknown"),
                        "serverSlug": d.get("serverSlug", ""),
                        "providerName": d.get("providerName", "Unknown"),
                        "providerId": d.get("providerId", ""),
                        "scoreDelta": float(d.get("delta", 0)),
                        "trustScore": float(d.get("trust_score", 0)),
                        "tier": d.get("tier", "D"),
                        "flags": d.get("diff", {}).get("fail_fast_flags_added", []),
                        "permalink": f"/mcp/servers/{d.get('serverSlug', d.get('server_id', ''))}",
                    }
                    for d in top_downgrades[:10]  # Limit to top 10
                ]
            
            # Extract new entrants
            new_entrants_raw = payload.get("newEntrants", [])
            if new_entrants_raw:
                # Deduplicate by server_id before enriching (safety check)
                seen_server_ids = set()
                deduplicated_raw = []
                for entry in new_entrants_raw:
                    server_id = entry.get("server_id") if isinstance(entry, dict) else None
                    if server_id and server_id not in seen_server_ids:
                        seen_server_ids.add(server_id)
                        deduplicated_raw.append(entry)
                
                new_entrants = _enrich_server_data(db, deduplicated_raw, "server_id")
                # Format for frontend
                new_entrants = [
                    {
                        "serverId": n.get("server_id"),
                        "serverName": n.get("serverName", "Unknown"),
                        "serverSlug": n.get("serverSlug", ""),
                        "providerName": n.get("providerName", "Unknown"),
                        "providerId": n.get("providerId", ""),
                        "trustScore": float(n.get("trust_score", 0)),
                        "tier": n.get("tier", "D"),
                        "firstAssessedAt": n.get("assessed_at"),
                        "permalink": f"/mcp/servers/{n.get('serverSlug', n.get('server_id', ''))}",
                    }
                    for n in new_entrants[:10]  # Limit to top 10
                ]
            
            # Extract notable drift
            notable_drift_raw = payload.get("notableDrift", [])
            if notable_drift_raw:
                notable_drift = _enrich_server_data(db, notable_drift_raw, "server_id")
                # Format for frontend
                notable_drift = [
                    {
                        "serverId": d.get("server_id"),
                        "serverName": d.get("serverName", "Unknown"),
                        "serverSlug": d.get("serverSlug", ""),
                        "eventType": d.get("event_type", "Unknown"),
                        "severity": d.get("severity", "Low"),
                        "summary": d.get("summary", ""),
                        "detectedAt": d.get("detected_at"),
                        "permalink": f"/mcp/servers/{d.get('serverSlug', d.get('server_id', ''))}",
                    }
                    for d in notable_drift[:20]  # Limit to top 20
                ]
    
    return {
        "serversTracked": servers_tracked,
        "providersTracked": providers_tracked,
        "tierCounts": tier_counts,
        "evidenceConfidenceCounts": evidence_counts,
        "failFastCount": fail_fast_count,
        "topMovers": top_movers,
        "topDowngrades": top_downgrades,
        "newEntrants": new_entrants,
        "notableDrift": notable_drift,
    }
