"""
Daily Brief service
"""

from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.models.daily_brief import DailyBrief


def get_daily_brief(db: Session, brief_date: date) -> Optional[DailyBrief]:
    """Get daily brief for a specific date"""
    return db.query(DailyBrief).filter(DailyBrief.date == brief_date).first()
