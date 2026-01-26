"""Constants and contractual definitions for the public API."""

from .attestation import (
    VERIFIED_RECENCY_DAYS,
    VERIFIED_MIN_EVIDENCE_CONFIDENCE,
    is_verified,
    build_attestation_envelope,
)

__all__ = [
    "VERIFIED_RECENCY_DAYS",
    "VERIFIED_MIN_EVIDENCE_CONFIDENCE",
    "is_verified",
    "build_attestation_envelope",
]
