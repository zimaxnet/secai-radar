"""
Latest agent score pointer model - one row per agent pointing to latest agent_score_snapshot.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime
from .base import Base


class AgentLatestScore(Base):
    """Points to the latest agent_score_snapshot per agent (projection for speed)."""
    __tablename__ = "agent_latest_scores"

    agent_id = Column(String(16), ForeignKey("agents.agent_id", ondelete="CASCADE"), primary_key=True)
    score_id = Column(String(16), ForeignKey("agent_score_snapshots.score_id"), nullable=False)
    updated_at = Column(DateTime, nullable=False)
