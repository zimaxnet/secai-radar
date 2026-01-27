"""
Trust Score v1 calculation logic
"""

from typing import Any, List, Optional
from .models import (
    EvidenceItem,
    ExtractedClaim,
    ScoreResult,
    DomainScore,
    TrustScore,
    Tier,
    EnterpriseFit,
    EvidenceConfidence,
    EvidenceType,
    Flag,
    ClaimType,
)


def calculate_evidence_confidence(evidence_items: List[EvidenceItem]) -> EvidenceConfidence:
    """
    Calculate Evidence Confidence (0-3) from evidence items.
    
    Rules:
    - 0: No evidence
    - 1: Public docs only
    - 2: Verifiable artifacts (repo, config)
    - 3: Validated evidence pack
    """
    if not evidence_items:
        return EvidenceConfidence.NONE
    
    has_validated_pack = any(
        item.type == EvidenceType.ATTESTATION and item.confidence == 3
        for item in evidence_items
    )
    if has_validated_pack:
        return EvidenceConfidence.VALIDATED_PACK

    has_verifiable = any(
        item.type in (EvidenceType.REPO, EvidenceType.CONFIG, EvidenceType.REPORT)
        and item.confidence >= 2
        for item in evidence_items
    )
    if has_verifiable:
        return EvidenceConfidence.VERIFIABLE_ARTIFACTS

    has_public_docs = any(
        item.type == EvidenceType.DOCS and item.confidence >= 1
        for item in evidence_items
    )
    if has_public_docs:
        return EvidenceConfidence.PUBLIC_DOCS
    
    return EvidenceConfidence.NONE


def _claim_value(claims: List[ExtractedClaim], claim_type: ClaimType) -> Optional[Any]:
    for c in claims:
        if c.claim_type == claim_type:
            return c.value.get("value") if isinstance(c.value, dict) else c.value
    return None


def calculate_domain_scores(
    evidence_items: List[EvidenceItem],
    claims: List[ExtractedClaim],
) -> DomainScore:
    """
    Deterministic domain subscores (D1-D6) from evidence and claims.
    D1=Auth, D2=Authz/Scopes, D3=Data/Hosting, D4=Audit, D5=Ops, D6=Compliance.
    Uses claim values and evidence presence; scale 0-5.
    """
    auth = _claim_value(claims, ClaimType.AUTH_MODEL)
    tool_agency = _claim_value(claims, ClaimType.TOOL_CAPABILITIES) or _claim_value(
        claims, ClaimType.TOOL_LIST
    )
    hosting = _claim_value(claims, ClaimType.HOSTING_CUSTODY)
    n_evidence = len(evidence_items)
    base = 2.0 if n_evidence else 0.0

    d1 = 4.0 if auth and str(auth).lower() not in ("unknown", "none", "") else max(0.0, base - 1.0)
    d2 = 3.5 if tool_agency else base
    d3 = 3.0 if hosting else base
    d4 = min(5.0, base + 0.5 * n_evidence)
    d5 = min(5.0, base + 0.3 * n_evidence)
    d6 = base

    return DomainScore(
        d1=min(5.0, max(0.0, d1)),
        d2=min(5.0, max(0.0, d2)),
        d3=min(5.0, max(0.0, d3)),
        d4=min(5.0, max(0.0, d4)),
        d5=min(5.0, max(0.0, d5)),
        d6=min(5.0, max(0.0, d6)),
    )


def calculate_weighted_trust_score(domain_scores: DomainScore) -> float:
    """
    Calculate weighted Trust Score (0-100) from domain subscores.
    
    Formula: Weighted average of D1-D6
    """
    # Placeholder weights - adjust based on methodology
    weights = {
        "d1": 0.20,  # Authentication
        "d2": 0.20,  # Authorization
        "d3": 0.20,  # Data Protection
        "d4": 0.15,  # Audit & Logging
        "d5": 0.15,  # Operational Security
        "d6": 0.10,  # Compliance
    }
    
    weighted_sum = (
        domain_scores.d1 * weights["d1"] +
        domain_scores.d2 * weights["d2"] +
        domain_scores.d3 * weights["d3"] +
        domain_scores.d4 * weights["d4"] +
        domain_scores.d5 * weights["d5"] +
        domain_scores.d6 * weights["d6"]
    )
    
    # Convert from 0-5 scale to 0-100 scale
    return weighted_sum * 20.0


def assign_tier(trust_score: float) -> Tier:
    """Assign tier based on Trust Score"""
    if trust_score >= 80:
        return Tier.A
    elif trust_score >= 60:
        return Tier.B
    elif trust_score >= 40:
        return Tier.C
    else:
        return Tier.D


def assign_enterprise_fit(
    trust_score: float,
    tier: Tier,
    evidence_confidence: EvidenceConfidence
) -> EnterpriseFit:
    """Assign enterprise fit classification"""
    if tier == Tier.A and evidence_confidence >= EvidenceConfidence.VERIFIABLE_ARTIFACTS:
        return EnterpriseFit.REGULATED
    elif tier in [Tier.A, Tier.B]:
        return EnterpriseFit.STANDARD
    else:
        return EnterpriseFit.EXPERIMENTAL


def detect_fail_fast_flags(
    evidence_items: List[EvidenceItem],
    claims: List[ExtractedClaim]
) -> List[Flag]:
    """
    Detect fail-fast flags that immediately disqualify a server.
    
    Examples:
    - No authentication
    - Destructive tools without safeguards
    - Known security vulnerabilities
    """
    flags: List[Flag] = []
    
    # Check for authentication
    has_auth = any(
        claim.claim_type == ClaimType.AUTH_MODEL
        for claim in claims
    )
    if not has_auth:
        flags.append(Flag(
            type="fail-fast",
            code="NO_AUTH",
            severity="Critical",
            message="No authentication mechanism detected"
        ))
    
    # TODO: Add more fail-fast checks
    
    return flags


def detect_risk_flags(
    evidence_items: List[EvidenceItem],
    claims: List[ExtractedClaim],
    domain_scores: DomainScore
) -> List[Flag]:
    """
    Detect risk flags that indicate potential issues.
    """
    flags: List[Flag] = []
    
    # Low domain scores
    if domain_scores.d1 < 2.0:
        flags.append(Flag(
            type="risk",
            code="LOW_AUTH_SCORE",
            severity="High",
            message="Authentication domain score is low"
        ))
    
    # TODO: Add more risk flag checks
    
    return flags


def calculate_trust_score(
    evidence_items: List[EvidenceItem],
    claims: List[ExtractedClaim],
    methodology_version: str = "v1.0"
) -> ScoreResult:
    """
    Calculate complete Trust Score from evidence and claims.
    
    Args:
        evidence_items: List of evidence items
        claims: List of extracted claims
        methodology_version: Methodology version used
    
    Returns:
        ScoreResult with domain scores, trust score, tier, flags, and explainability
    """
    # Calculate evidence confidence
    evidence_confidence = calculate_evidence_confidence(evidence_items)
    
    # Detect fail-fast flags (if any, return early with D tier)
    fail_fast_flags = detect_fail_fast_flags(evidence_items, claims)
    if fail_fast_flags:
        return ScoreResult(
            domain_scores=DomainScore(d1=0, d2=0, d3=0, d4=0, d5=0, d6=0),
            trust_score=TrustScore(
                trust_score=0.0,
                tier=Tier.D,
                enterprise_fit=EnterpriseFit.EXPERIMENTAL,
                evidence_confidence=evidence_confidence
            ),
            fail_fast_flags=fail_fast_flags,
            risk_flags=[],
            explainability={
                "methodology_version": methodology_version,
                "fail_fast_reason": fail_fast_flags[0].message
            }
        )
    
    # Calculate domain scores
    domain_scores = calculate_domain_scores(evidence_items, claims)
    
    # Calculate weighted trust score
    trust_score_value = calculate_weighted_trust_score(domain_scores)
    
    # Assign tier
    tier = assign_tier(trust_score_value)
    
    # Assign enterprise fit
    enterprise_fit = assign_enterprise_fit(trust_score_value, tier, evidence_confidence)
    
    # Detect risk flags
    risk_flags = detect_risk_flags(evidence_items, claims, domain_scores)
    
    # Generate explainability payload (Pydantic v2: model_dump)
    _dump = lambda m: m.model_dump() if hasattr(m, "model_dump") else m.dict()
    explainability = {
        "methodology_version": methodology_version,
        "domain_scores": _dump(domain_scores),
        "evidence_confidence": evidence_confidence.value,
        "flags": [_dump(f) for f in fail_fast_flags + risk_flags],
    }
    
    return ScoreResult(
        domain_scores=domain_scores,
        trust_score=TrustScore(
            trust_score=trust_score_value,
            tier=tier,
            enterprise_fit=enterprise_fit,
            evidence_confidence=evidence_confidence
        ),
        fail_fast_flags=fail_fast_flags,
        risk_flags=risk_flags,
        explainability=explainability
    )
