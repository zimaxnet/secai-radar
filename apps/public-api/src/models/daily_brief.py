"""
Daily Brief model
"""

from sqlalchemy import Column, String, Text, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class DailyBrief(Base):
    """Daily Brief entity"""
    __tablename__ = "daily_briefs"
    
    date = Column(Date, primary_key=True)
    methodology_version = Column(String(50), nullable=False)
    
    headline = Column(Text, nullable=False)
    narrative_short = Column(Text, nullable=False)
    narrative_long = Column(Text, nullable=True)
    
    highlights = Column(JSONB, nullable=False)  # Array of strings
    payload_json = Column(JSONB, nullable=False)  # Full DailyBrief object with movers/downgrades/newEntrants/notableDrift
    
    generated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
