"""
Unit tests for Trust Score calculator
"""

import pytest
from scoring import (
    calculate_trust_score,
    calculate_evidence_confidence,
    EvidenceItem,
    ExtractedClaim,
    EvidenceType,
    ClaimType,
    EvidenceConfidence,
)


def test_evidence_confidence_none():
    """Test Evidence Confidence = 0 when no evidence"""
    result = calculate_evidence_confidence([])
    assert result == EvidenceConfidence.NONE


def test_evidence_confidence_public_docs():
    """Test Evidence Confidence = 1 with public docs only"""
    evidence = [
        EvidenceItem(
            evidence_id="e1",
            type=EvidenceType.DOCS,
            confidence=1,
            source_url="https://example.com/docs"
        )
    ]
    result = calculate_evidence_confidence(evidence)
    assert result == EvidenceConfidence.PUBLIC_DOCS


def test_evidence_confidence_verifiable():
    """Test Evidence Confidence = 2 with verifiable artifacts"""
    evidence = [
        EvidenceItem(
            evidence_id="e1",
            type=EvidenceType.REPO,
            confidence=2,
            source_url="https://github.com/example/repo"
        )
    ]
    result = calculate_evidence_confidence(evidence)
    assert result == EvidenceConfidence.VERIFIABLE_ARTIFACTS


def test_evidence_confidence_validated():
    """Test Evidence Confidence = 3 with validated pack"""
    evidence = [
        EvidenceItem(
            evidence_id="e1",
            type=EvidenceType.ATTESTATION,
            confidence=3,
            source_url="https://example.com/attestation"
        )
    ]
    result = calculate_evidence_confidence(evidence)
    assert result == EvidenceConfidence.VALIDATED_PACK


def test_fail_fast_no_auth():
    """Test fail-fast flag when no authentication"""
    evidence = [
        EvidenceItem(
            evidence_id="e1",
            type=EvidenceType.DOCS,
            confidence=1,
            source_url="https://example.com/docs"
        )
    ]
    claims = []  # No auth claim
    
    result = calculate_trust_score(evidence, claims)
    
    assert len(result.fail_fast_flags) > 0
    assert result.trust_score.tier.value == "D"
    assert result.trust_score.trust_score == 0.0


def test_scoring_with_auth():
    """Test scoring with authentication claim (sample server 2)"""
    evidence = [
        EvidenceItem(
            evidence_id="e1",
            type=EvidenceType.DOCS,
            confidence=2,
            source_url="https://example.com/docs"
        )
    ]
    claims = [
        ExtractedClaim(
            claim_type=ClaimType.AUTH_MODEL,
            value={"value": "OAuthOIDC"},
            confidence=2,
            source_url="https://example.com/docs",
            source_evidence_id="e1"
        )
    ]
    result = calculate_trust_score(evidence, claims)
    assert len(result.fail_fast_flags) == 0
    assert result.trust_score.tier.value in ["A", "B", "C", "D"]
    assert result.domain_scores.d1 >= 0


def test_scoring_sample_3_high_trust():
    """Sample server 3: repo + auth + hosting -> higher d1,d2,d3"""
    evidence = [
        EvidenceItem(evidence_id="e1", type=EvidenceType.REPO, confidence=2, source_url="https://github.com/x/y"),
    ]
    claims = [
        ExtractedClaim(claim_type=ClaimType.AUTH_MODEL, value={"value": "APIKey"}, confidence=2, source_url="https://github.com/x/y", source_evidence_id="e1"),
        ExtractedClaim(claim_type=ClaimType.HOSTING_CUSTODY, value={"value": "third_party"}, confidence=2, source_url="https://github.com/x/y", source_evidence_id="e1"),
    ]
    result = calculate_trust_score(evidence, claims)
    assert len(result.fail_fast_flags) == 0
    assert result.trust_score.evidence_confidence.value == 2
    assert result.domain_scores.d1 >= 3
    assert result.domain_scores.d3 >= 2


def test_scoring_sample_4_docs_only_no_claims():
    """Sample server 4: docs only, no auth claim -> fail-fast or low tier"""
    evidence = [
        EvidenceItem(evidence_id="e1", type=EvidenceType.DOCS, confidence=1, source_url="https://example.com/readme"),
    ]
    claims = []
    result = calculate_trust_score(evidence, claims)
    assert len(result.fail_fast_flags) > 0 or result.trust_score.tier.value == "D"
    assert result.trust_score.evidence_confidence.value == 1


def test_scoring_sample_5_deterministic():
    """Sample server 5: same inputs -> same outputs (deterministic)"""
    evidence = [
        EvidenceItem(evidence_id="e1", type=EvidenceType.DOCS, confidence=2, source_url="https://example.com/d"),
    ]
    claims = [
        ExtractedClaim(claim_type=ClaimType.AUTH_MODEL, value={"value": "mTLS"}, confidence=2, source_url="https://example.com/d", source_evidence_id="e1"),
    ]
    r1 = calculate_trust_score(evidence, claims)
    r2 = calculate_trust_score(evidence, claims)
    assert r1.domain_scores.d1 == r2.domain_scores.d1
    assert r1.trust_score.trust_score == r2.trust_score.trust_score


if __name__ == "__main__":
    pytest.main([__file__])
