"""
Daily Brief model
"""

from sqlalchemy import Column, String, Text, Date, JSON, DateTime
from .base import Base


class DailyBrief(Base):
    """Daily Brief entity"""
    __tablename__ = "daily_briefs"
    
    brief_id = Column(String(16), primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    methodology_version = Column(String(50), nullable=False)
    
    headline = Column(Text, nullable=False)
    narrative_short = Column(Text, nullable=False)
    narrative_long = Column(Text, nullable=True)
    
    movers_json = Column(JSON, nullable=False, default=[])
    downgrades_json = Column(JSON, nullable=False, default=[])
    new_entrants_json = Column(JSON, nullable=False, default=[])
    notable_drift_json = Column(JSON, nullable=False, default=[])
    
    tip_of_the_day = Column(Text, nullable=True)
    
    generated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
