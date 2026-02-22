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
    ServerMetadata,
)


def calculate_evidence_confidence(
    evidence_items: List[EvidenceItem],
    metadata: Optional[ServerMetadata] = None
) -> EvidenceConfidence:
    """
    Calculate Evidence Confidence (0-3) from evidence items and metadata.
    
    Rules:
    - 0: No evidence
    - 1: Public docs only
    - 2: Verifiable artifacts (repo, config)
    - 3: Validated evidence pack
    
    Provenance boost:
    - Official Registry: +1 confidence boost (capped at 3)
    - MCPAnvil: neutral
    - Other: neutral
    """
    if not evidence_items:
        return EvidenceConfidence.NONE
    
    base_confidence = EvidenceConfidence.NONE
    
    has_validated_pack = any(
        item.type == EvidenceType.ATTESTATION and item.confidence == 3
        for item in evidence_items
    )
    if has_validated_pack:
        base_confidence = EvidenceConfidence.VALIDATED_PACK
    else:
        has_verifiable = any(
            item.type in (EvidenceType.REPO, EvidenceType.CONFIG, EvidenceType.REPORT)
            and item.confidence >= 2
            for item in evidence_items
        )
        if has_verifiable:
            base_confidence = EvidenceConfidence.VERIFIABLE_ARTIFACTS
        else:
            has_public_docs = any(
                item.type == EvidenceType.DOCS and item.confidence >= 1
                for item in evidence_items
            )
            if has_public_docs:
                base_confidence = EvidenceConfidence.PUBLIC_DOCS
    
    # Apply provenance boost
    if metadata and metadata.source_provenance == "Official Registry":
        # Boost by 1, but cap at 3
        boosted_value = min(base_confidence.value + 1, 3)
        return EvidenceConfidence(boosted_value)
    
    return base_confidence


def _claim_value(claims: List[ExtractedClaim], claim_type: ClaimType) -> Optional[Any]:
    for c in claims:
        if c.claim_type == claim_type:
            return c.value.get("value") if isinstance(c.value, dict) else c.value
    return None


def calculate_domain_scores(
    evidence_items: List[EvidenceItem],
    claims: List[ExtractedClaim],
    metadata: Optional[ServerMetadata] = None,
) -> DomainScore:
    """
    Deterministic domain subscores (D1-D6) from evidence and claims.
    D1=Auth, D2=Authz/Scopes, D3=Data/Hosting, D4=Audit, D5=Ops, D6=Compliance.
    Uses claim values, evidence presence, and real metric signals; scale 0-5.
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
    
    # Calculate D5 (Ops) algorithmically via authentic popularity metrics
    d5 = base
    if metadata and metadata.popularity_signals:
        github = metadata.popularity_signals.get("github", {})
        if github:
            stars = github.get("stars", 0)
            forks = github.get("forks", 0)
            
            # Algorithmic popularity tiering
            if stars > 1000: d5 += 2.0
            elif stars > 100: d5 += 1.0
            elif stars > 10: d5 += 0.5
            
            if forks > 100: d5 += 0.5
            
            # Check for recency signals (within 90 days)
            updated_str = github.get("updated_at")
            if updated_str:
                try:
                    from datetime import datetime
                    updated = datetime.strptime(updated_str[:10], "%Y-%m-%d")
                    delta = (datetime.utcnow() - updated).days
                    if delta <= 90:
                        d5 += 1.0
                except:
                    pass

    # Calculate D6 (Compliance) strictly based on claimed evidence
    d6 = base
    has_sbom = _claim_value(claims, ClaimType.SBOM)
    has_ir = _claim_value(claims, ClaimType.IR_POLICY)
    has_vuln = _claim_value(claims, ClaimType.VULN_DISCLOSURE)
    has_signing = _claim_value(claims, ClaimType.SIGNING)
    
    if has_sbom: d6 += 1.0
    if has_ir: d6 += 1.0
    if has_vuln: d6 += 0.5
    if has_signing: d6 += 0.5

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
    methodology_version: str = "v1.0",
    metadata: Optional[ServerMetadata] = None
) -> ScoreResult:
    """
    Calculate complete Trust Score from evidence and claims.
    
    Args:
        evidence_items: List of evidence items
        claims: List of extracted claims
        methodology_version: Methodology version used
        metadata: Optional server metadata for provenance weighting
    
    Returns:
        ScoreResult with domain scores, trust score, tier, flags, and explainability
    """
    # Calculate evidence confidence (with provenance boost)
    evidence_confidence = calculate_evidence_confidence(evidence_items, metadata)
    
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
    
    # Calculate domain scores with real metadata signals
    domain_scores = calculate_domain_scores(evidence_items, claims, metadata)
    
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
