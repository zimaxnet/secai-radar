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
    """Test scoring with authentication claim"""
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
            value={"type": "OAuthOIDC"},
            confidence=2,
            source_url="https://example.com/docs",
            source_evidence_id="e1"
        )
    ]
    
    result = calculate_trust_score(evidence, claims)
    
    assert len(result.fail_fast_flags) == 0
    assert result.trust_score.tier.value in ["A", "B", "C", "D"]


if __name__ == "__main__":
    pytest.main([__file__])
