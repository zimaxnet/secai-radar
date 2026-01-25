"""
Drift Event model
"""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON
from .base import Base


class DriftEvent(Base):
    """Drift Event entity (append-only)"""
    __tablename__ = "drift_events"
    
    drift_id = Column(String(16), primary_key=True)
    server_id = Column(String(16), ForeignKey("mcp_servers.server_id"), nullable=False)
    detected_at = Column(DateTime, nullable=False)
    severity = Column(String(50), nullable=False)  # Critical, High, Medium, Low
    event_type = Column(String(50), nullable=False)  # ToolsAdded, ToolsRemoved, AuthChanged, etc.
    summary = Column(Text, nullable=False)
    diff_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)
