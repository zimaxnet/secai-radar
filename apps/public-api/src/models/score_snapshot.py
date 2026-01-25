"""
Score Snapshot model
"""

from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, JSON
from .base import Base


class ScoreSnapshot(Base):
    """Score Snapshot entity (append-only)"""
    __tablename__ = "score_snapshots"
    
    score_id = Column(String(16), primary_key=True)
    server_id = Column(String(16), ForeignKey("mcp_servers.server_id"), nullable=False)
    methodology_version = Column(String(50), nullable=False)
    assessed_at = Column(DateTime, nullable=False)
    
    # Domain subscores (0-5)
    d1 = Column(Numeric(3, 1), nullable=False)  # Authentication
    d2 = Column(Numeric(3, 1), nullable=False)  # Authorization
    d3 = Column(Numeric(3, 1), nullable=False)  # Data Protection
    d4 = Column(Numeric(3, 1), nullable=False)  # Audit & Logging
    d5 = Column(Numeric(3, 1), nullable=False)  # Operational Security
    d6 = Column(Numeric(3, 1), nullable=False)  # Compliance
    
    trust_score = Column(Numeric(5, 2), nullable=False)  # 0-100
    tier = Column(String(1), nullable=False)  # A, B, C, D
    enterprise_fit = Column(String(50), nullable=False)  # Regulated, Standard, Experimental
    evidence_confidence = Column(Numeric(1, 0), nullable=False)  # 0-3
    
    fail_fast_flags = Column(JSON, nullable=False, default=[])
    risk_flags = Column(JSON, nullable=False, default=[])
    explainability_json = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, nullable=False)
