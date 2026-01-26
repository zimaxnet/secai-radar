# Verified MCP — Definition of “Verified”

**Authority:** SecAI Radar Public API and docs.  
**Version:** 1.0  
**See also:** [Pivot_Strategy_Reuse_Ideas.md](./Pivot_Strategy_Reuse_Ideas.md)

---

## Rule

A server or score snapshot is **Verified** if and only if:

1. **Evidence confidence** is at least **2** (on the 0–3 scale).
2. **Last verified at** is within the last **7 days** (inclusive).
3. *(Optional)* An **integrity digest** is present for the snapshot or feed item. When present, it strengthens attestation; when absent, the first two conditions alone still qualify as Verified.

In code (public-api): `src.constants.attestation.is_verified(evidence_confidence, last_verified_at, has_integrity_digest=False)`.

---

## Constants

| Constant | Value | Purpose |
|----------|--------|---------|
| `VERIFIED_MIN_EVIDENCE_CONFIDENCE` | 2 | Minimum evidence confidence (0–3) for Verified. |
| `VERIFIED_RECENCY_DAYS` | 7 | Maximum age in days of `lastVerifiedAt` for Verified. |

---

## Record integrity digest (optional, A3)

Server-detail and ranking items may include an optional **`integrityDigest`** for snapshot-level tamper checking. Algorithm:

- **Inputs:** `server_id`, `trust_score`, `tier`, `evidence_ids` (ordered list), `asOf` (ISO timestamp).
- **Canonical form:** JSON object `{"asOf","evidence_ids","server_id","tier","trust_score"}` with sorted keys; `evidence_ids` is sorted. Same as `json.dumps(payload, sort_keys=True)` in Python.
- **Digest:** SHA-256 of the UTF-8 encoding of that JSON, expressed as lowercase hex.

In code: `src.constants.attestation.record_integrity_digest(server_id, trust_score, tier, evidence_ids, as_of)`.

Consumers can recompute the digest from the same fields and compare to `integrityDigest` to verify the record was not altered.

---

## Usage

- **API:** Responses that expose a “Verified” badge or flag must use this definition (e.g. `is_verified(...)` or equivalent logic).
- **Feeds:** RSS/JSON feed metadata and item-level attestation reference this definition.
- **Methodology:** “SecAI Radar attests to the evidence and context behind each score” — the “Verified” badge reflects this definition.
