"""
Agent model
"""

from sqlalchemy import Column, String, Text, ForeignKey, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
from .provider import Provider

class Agent(Base, TimestampMixin):
    """Agent entity"""
    __tablename__ = "agents"
    
    agent_id = Column(String(16), primary_key=True)
    agent_slug = Column(String(255), nullable=False, unique=True)
    agent_name = Column(String(255), nullable=False)
    provider_id = Column(String(16), ForeignKey("providers.provider_id"), nullable=False)
    category_primary = Column(String(100), nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    agent_type = Column(String(50), nullable=False)  # Copilot Extension, Custom Agent, Plugin, Unknown
    repo_url = Column(Text, nullable=True)
    docs_url = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="Active")  # Active, Deprecated, Unknown
    first_seen_at = Column(DateTime, nullable=False)
    last_seen_at = Column(DateTime, nullable=False)
    metadata_json = Column(JSONB, nullable=True, default={})  # Flexible metadata storage
    
    provider = relationship(Provider, backref="agents")
