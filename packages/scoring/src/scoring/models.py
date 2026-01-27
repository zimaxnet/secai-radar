"""
Data models for Trust Score calculation
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Tier(str, Enum):
    """Trust Score tier"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class EnterpriseFit(str, Enum):
    """Enterprise fit classification"""
    REGULATED = "Regulated"
    STANDARD = "Standard"
    EXPERIMENTAL = "Experimental"


class EvidenceConfidence(int, Enum):
    """Evidence confidence level (0-3)"""
    NONE = 0
    PUBLIC_DOCS = 1
    VERIFIABLE_ARTIFACTS = 2
    VALIDATED_PACK = 3


class EvidenceType(str, Enum):
    """Evidence item type"""
    DOCS = "Docs"
    REPO = "Repo"
    REPORT = "Report"
    CONFIG = "Config"
    LOGS = "Logs"
    ATTESTATION = "Attestation"


class ClaimType(str, Enum):
    """Extracted claim type"""
    AUTH_MODEL = "AuthModel"
    TOKEN_TTL = "TokenTTL"
    SCOPES = "Scopes"
    HOSTING_CUSTODY = "HostingCustody"
    TOOL_LIST = "ToolList"
    TOOL_CAPABILITIES = "ToolCapabilities"
    AUDIT_LOGGING = "AuditLogging"
    DATA_RETENTION = "DataRetention"
    DATA_DELETION = "DataDeletion"
    RESIDENCY = "Residency"
    ENCRYPTION = "Encryption"
    SBOM = "SBOM"
    SIGNING = "Signing"
    VULN_DISCLOSURE = "VulnDisclosure"
    IR_POLICY = "IRPolicy"


class Flag(BaseModel):
    """Risk or fail-fast flag"""
    type: str  # "fail-fast" or "risk"
    code: str
    severity: str  # "Critical", "High", "Medium", "Low"
    message: str


class ExtractedClaim(BaseModel):
    """Extracted claim from evidence"""
    claim_type: ClaimType
    value: Dict[str, Any]
    confidence: int = Field(ge=1, le=3)
    source_url: str
    source_evidence_id: str


class EvidenceItem(BaseModel):
    """Evidence item"""
    evidence_id: str
    type: EvidenceType
    url: Optional[str] = None
    confidence: int = Field(ge=1, le=3)
    source_url: str
    claims: List[ExtractedClaim] = []


class DomainScore(BaseModel):
    """Domain subscore (0-5)"""
    d1: float = Field(ge=0, le=5, description="Authentication")
    d2: float = Field(ge=0, le=5, description="Authorization")
    d3: float = Field(ge=0, le=5, description="Data Protection")
    d4: float = Field(ge=0, le=5, description="Audit & Logging")
    d5: float = Field(ge=0, le=5, description="Operational Security")
    d6: float = Field(ge=0, le=5, description="Compliance")


class TrustScore(BaseModel):
    """Trust Score result"""
    trust_score: float = Field(ge=0, le=100, description="Weighted Trust Score (0-100)")
    tier: Tier
    enterprise_fit: EnterpriseFit
    evidence_confidence: EvidenceConfidence


class ServerMetadata(BaseModel):
    """Server metadata for scoring context"""
    publisher: Optional[str] = None
    deployment_type: Optional[str] = None  # Remote, Local, Hybrid, Unknown
    transport: Optional[str] = None
    source_provenance: Optional[str] = None  # Official Registry, MCPAnvil, Other
    popularity_signals: Optional[Dict[str, Any]] = None  # stars, downloads, etc.


class ScoreResult(BaseModel):
    """Complete score result"""
    domain_scores: DomainScore
    trust_score: TrustScore
    fail_fast_flags: List[Flag] = []
    risk_flags: List[Flag] = []
    explainability: Dict[str, Any] = Field(default_factory=dict)
