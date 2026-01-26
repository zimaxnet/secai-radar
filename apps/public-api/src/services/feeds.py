"""
Feed generation services (RSS and JSON Feed).

Each feed item includes Gk-like attestation fields: provenance, integrityDigest,
security_context (see Pivot_Strategy_Reuse_Ideas.md).
"""

import hashlib
import json
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.models.daily_brief import DailyBrief
import xml.etree.ElementTree as ET
from xml.dom import minidom

METHODOLOGY_VERSION = "v1.0"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


def _item_integrity_digest(
    date_str: str,
    headline: str,
    narrative_short: str,
    methodology_version: str,
    generated_at: str,
) -> str:
    """SHA-256 of canonical item fields for tamper check."""
    canonical = f"{date_str}|{headline}|{narrative_short}|{methodology_version}|{generated_at}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _item_attestation_fields(
    date_str: str,
    headline: str,
    narrative_short: str,
    methodology_version: str,
    generated_at: datetime,
) -> Dict[str, Any]:
    """Provenance, integrityDigest, security_context for one feed item."""
    as_of = generated_at.isoformat() if hasattr(generated_at, "isoformat") else str(generated_at)
    digest = _item_integrity_digest(
        date_str, headline, narrative_short or "", methodology_version or METHODOLOGY_VERSION, as_of
    )
    return {
        "provenance": {
            "sourceId": "secai-radar",
            "asOf": as_of,
            "methodologyVersion": methodology_version or METHODOLOGY_VERSION,
        },
        "integrityDigest": digest,
        "security_context": {"assessor": "SecAI Radar", "scope": "public-ranking"},
    }


def generate_rss_feed(db: Session, limit: int = 30) -> str:
    """
    Generate RSS/Atom feed XML
    
    Args:
        db: Database session
        limit: Maximum number of items
    
    Returns:
        RSS feed XML string
    """
    # Get recent daily briefs
    cutoff = datetime.utcnow().date() - timedelta(days=limit)
    briefs = db.query(DailyBrief).filter(
        DailyBrief.date >= cutoff
    ).order_by(DailyBrief.date.desc()).limit(limit).all()
    
    # Build RSS feed (content namespace for attestation in each item)
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:content", CONTENT_NS)
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "SecAI Radar MCP Daily Brief"
    ET.SubElement(channel, "link").text = "https://secairadar.cloud/mcp"
    ET.SubElement(channel, "description").text = (
        "SecAI Radar attests to the evidence and context behind each score. "
        "Independent attestation of MCP server trust posture. Daily briefs, rankings, evidence, and drift tracking."
    )
    ET.SubElement(channel, "language").text = "en-US"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    for brief in briefs:
        date_str = brief.date.isoformat()
        gen_at = brief.generated_at
        gen_at_iso = gen_at.isoformat() if hasattr(gen_at, "isoformat") else str(gen_at)
        att = _item_attestation_fields(
            date_str, brief.headline, brief.narrative_short or "", brief.methodology_version or METHODOLOGY_VERSION, gen_at
        )
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = brief.headline
        ET.SubElement(item, "link").text = f"https://secairadar.cloud/mcp/daily/{date_str}"
        ET.SubElement(item, "description").text = brief.narrative_short or ""
        ET.SubElement(item, "pubDate").text = gen_at.strftime("%a, %d %b %Y %H:%M:%S GMT") if hasattr(gen_at, "strftime") else gen_at_iso
        ET.SubElement(item, "guid", isPermaLink="true").text = f"https://secairadar.cloud/mcp/daily/{date_str}"
        enc = ET.SubElement(item, f"{{{CONTENT_NS}}}encoded")
        enc.text = json.dumps(att)
    
    # Convert to string
    rough_string = ET.tostring(rss, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def generate_json_feed(db: Session, limit: int = 30) -> dict:
    """
    Generate JSON Feed
    
    Args:
        db: Database session
        limit: Maximum number of items
    
    Returns:
        JSON Feed dictionary
    """
    # Get recent daily briefs
    cutoff = datetime.utcnow().date() - timedelta(days=limit)
    briefs = db.query(DailyBrief).filter(
        DailyBrief.date >= cutoff
    ).order_by(DailyBrief.date.desc()).limit(limit).all()
    
    items = []
    for brief in briefs:
        date_str = brief.date.isoformat()
        gen_at = brief.generated_at
        gen_at_iso = gen_at.isoformat() if hasattr(gen_at, "isoformat") else str(gen_at)
        att = _item_attestation_fields(
            date_str, brief.headline, brief.narrative_short or "", brief.methodology_version or METHODOLOGY_VERSION, gen_at
        )
        items.append({
            "id": f"https://secairadar.cloud/mcp/daily/{date_str}",
            "url": f"https://secairadar.cloud/mcp/daily/{date_str}",
            "title": brief.headline,
            "content_text": brief.narrative_short or "",
            "date_published": gen_at_iso,
            "provenance": att["provenance"],
            "integrityDigest": att["integrityDigest"],
            "security_context": att["security_context"],
        })
    
    return {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "SecAI Radar MCP Daily Brief",
        "description": (
            "SecAI Radar attests to the evidence and context behind each score. "
            "Independent attestation of MCP server trust posture. Daily briefs, rankings, evidence, and drift tracking."
        ),
        "feed_url": "https://secairadar.cloud/mcp/feed.json",
        "home_page_url": "https://secairadar.cloud/mcp",
        "items": items
    }
