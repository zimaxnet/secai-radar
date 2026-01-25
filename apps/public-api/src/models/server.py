"""
MCP Server model
"""

from sqlalchemy import Column, String, Text, ForeignKey, ARRAY, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class MCPServer(Base, TimestampMixin):
    """MCP Server entity"""
    __tablename__ = "mcp_servers"
    
    server_id = Column(String(16), primary_key=True)
    server_slug = Column(String(255), nullable=False, unique=True)
    server_name = Column(String(255), nullable=False)
    provider_id = Column(String(16), ForeignKey("providers.provider_id"), nullable=False)
    category_primary = Column(String(100), nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    deployment_type = Column(String(50), nullable=False)  # Remote, Local, Hybrid, Unknown
    auth_model = Column(String(50), nullable=False)  # OAuthOIDC, APIKey, PAT, mTLS, Unknown
    tool_agency = Column(String(50), nullable=False)  # ReadOnly, ReadWrite, DestructivePresent, Unknown
    repo_url = Column(Text, nullable=True)
    docs_url = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="Active")  # Active, Deprecated, Unknown
    first_seen_at = Column(DateTime, nullable=False)
    last_seen_at = Column(DateTime, nullable=False)
    
    provider = relationship("Provider", backref="servers")
