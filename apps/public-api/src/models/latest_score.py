"""
Latest score pointer model - one row per server pointing to latest score_snapshot.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime
from .base import Base


class LatestScore(Base):
    """Points to the latest score_snapshot per server (projection for speed)."""
    __tablename__ = "latest_scores"

    server_id = Column(String(16), ForeignKey("mcp_servers.server_id", ondelete="CASCADE"), primary_key=True)
    score_id = Column(String(16), ForeignKey("score_snapshots.score_id"), nullable=False)
    updated_at = Column(DateTime, nullable=False)
