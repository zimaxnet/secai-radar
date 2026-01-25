"""
Evidence models
"""

from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, JSON
from .base import Base, TimestampMixin


class EvidenceItem(Base, TimestampMixin):
    """Evidence Item entity"""
    __tablename__ = "evidence_items"
    
    evidence_id = Column(String(16), primary_key=True)
    server_id = Column(String(16), ForeignKey("mcp_servers.server_id"), nullable=False)
    type = Column(String(50), nullable=False)  # Docs, Repo, Report, Config, Logs, Attestation
    url = Column(Text, nullable=True)  # public URL
    blob_ref = Column(Text, nullable=True)  # private blob reference
    captured_at = Column(DateTime, nullable=False)
    confidence = Column(Integer, nullable=False)  # 1-3
    content_hash = Column(String(64), nullable=False)  # SHA-256
    source_url = Column(Text, nullable=False)
    parser_version = Column(String(50), nullable=True)


class ExtractedClaim(Base, TimestampMixin):
    """Extracted Claim entity"""
    __tablename__ = "evidence_claims"
    
    claim_id = Column(String(16), primary_key=True)
    evidence_id = Column(String(16), ForeignKey("evidence_items.evidence_id"), nullable=False)
    claim_type = Column(String(50), nullable=False)
    value_json = Column(JSON, nullable=False)  # Flexible value storage
    confidence = Column(Integer, nullable=False)  # 1-3
    source_url = Column(Text, nullable=False)
    captured_at = Column(DateTime, nullable=False)
