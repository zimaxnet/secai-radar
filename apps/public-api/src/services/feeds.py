"""
Feed generation services (RSS and JSON Feed)
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from src.models.daily_brief import DailyBrief
import xml.etree.ElementTree as ET
from xml.dom import minidom


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
    
    # Build RSS feed
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "SecAI Radar MCP Daily Brief"
    ET.SubElement(channel, "link").text = "https://secairadar.cloud/mcp"
    ET.SubElement(channel, "description").text = "Daily Trust Brief for Verified MCP Servers"
    ET.SubElement(channel, "language").text = "en-US"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    for brief in briefs:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = brief.headline
        ET.SubElement(item, "link").text = f"https://secairadar.cloud/mcp/daily/{brief.date.isoformat()}"
        ET.SubElement(item, "description").text = brief.narrative_short
        ET.SubElement(item, "pubDate").text = brief.generated_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(item, "guid", isPermaLink="true").text = f"https://secairadar.cloud/mcp/daily/{brief.date.isoformat()}"
    
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
        items.append({
            "id": f"https://secairadar.cloud/mcp/daily/{brief.date.isoformat()}",
            "url": f"https://secairadar.cloud/mcp/daily/{brief.date.isoformat()}",
            "title": brief.headline,
            "content_text": brief.narrative_short,
            "date_published": brief.generated_at.isoformat()
        })
    
    return {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "SecAI Radar MCP Daily Brief",
        "feed_url": "https://secairadar.cloud/mcp/feed.json",
        "home_page_url": "https://secairadar.cloud/mcp",
        "items": items
    }
