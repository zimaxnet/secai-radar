"""
Verified MCP attestation constants and helpers.

Definition (see docs/VERIFIED-DEFINITION.md):
  Verified = (evidenceConfidence >= VERIFIED_MIN_EVIDENCE_CONFIDENCE)
            AND (lastVerifiedAt within last VERIFIED_RECENCY_DAYS)
            AND (optional: integrityDigest present)
"""

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Any, Dict, List

VERIFIED_RECENCY_DAYS = 7
VERIFIED_MIN_EVIDENCE_CONFIDENCE = 2
ASSESSED_BY = "SecAI Radar"


def build_attestation_envelope(
    methodology_version: str,
    as_of: Optional[datetime] = None,
    assessment_run_id: Optional[str] = None,
    evidence_bundle_version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the standard attestation envelope for public API responses.
    Same shape for summary, rankings, server, daily brief, and feeds.
    """
    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    envelope = {
        "assessedBy": ASSESSED_BY,
        "methodologyVersion": methodology_version,
        "asOf": now.isoformat(),
    }
    if assessment_run_id is not None:
        envelope["assessmentRunId"] = assessment_run_id
    if evidence_bundle_version is not None:
        envelope["evidenceBundleVersion"] = evidence_bundle_version
    return envelope


def is_verified(
    evidence_confidence: int,
    last_verified_at: Optional[datetime],
    has_integrity_digest: bool = False,
) -> bool:
    """
    Return True if the server/snapshot meets the published Verified definition.

    Args:
        evidence_confidence: 0–3; must be >= VERIFIED_MIN_EVIDENCE_CONFIDENCE.
        last_verified_at: When the snapshot was last verified; must be within
            VERIFIED_RECENCY_DAYS. None is treated as not verified.
        has_integrity_digest: If True, integrity digest is present (optional
            strengthener). Does not disqualify when False.

    Returns:
        True if Verified per docs/VERIFIED-DEFINITION.md.
    """
    if evidence_confidence < VERIFIED_MIN_EVIDENCE_CONFIDENCE:
        return False
    if last_verified_at is None:
        return False
    now = datetime.now(timezone.utc)
    if last_verified_at.tzinfo is None:
        last_verified_at = last_verified_at.replace(tzinfo=timezone.utc)
    cutoff = now - timedelta(days=VERIFIED_RECENCY_DAYS)
    if last_verified_at < cutoff:
        return False
    return True


def record_integrity_digest(
    server_id: str,
    trust_score: float,
    tier: str,
    evidence_ids: List[str],
    as_of: datetime,
) -> str:
    """
    SHA-256 digest of canonical snapshot fields for server/ranking records (A3).

    Canonical form: JSON with keys server_id, trust_score, tier, evidence_ids (sorted),
    asOf (ISO). Consumers can recompute and compare to verify integrity.
    """
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    payload = {
        "server_id": server_id,
        "trust_score": trust_score,
        "tier": tier,
        "evidence_ids": sorted(evidence_ids),
        "asOf": as_of.isoformat(),
    }
    canonical = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
