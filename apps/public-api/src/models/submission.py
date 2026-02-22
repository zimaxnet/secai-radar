"""
User submissions queue model
"""

from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.sql import func
from .base import Base

class Submission(Base):
    """User submitted integrations queue"""
    __tablename__ = "submissions_queue"
    
    submission_id = Column(Integer, primary_key=True, autoincrement=True)
    repo_url = Column(Text, nullable=False)
    integration_type = Column(String(20), nullable=False) # 'mcp' or 'agent'
    contact_email = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
