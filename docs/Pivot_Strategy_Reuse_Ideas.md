# Reusing Pivot Strategy Ideas (Without the Full Pivot)

**Context:** We are staying with the **daily-update / Verified MCP reporting** strategy. This doc pulls **concrete, reusable ideas** from [SecAI_Radar_Pivot_Strategy.md](./SecAI_Radar_Pivot_Strategy.md) that can improve either the Verified MCP ranking/attestation system or ctxEco MCP, short of building the Authority middleware.

---

## 1. Ideas for Verified MCP Ranking & Attestation

### A. Attestation / proof vocabulary (from Gk schema)

The pivot’s Gk schema uses **integrity_proof**, **security_context**, **provenance**. We can adopt the same language and optional fields in our public model and feeds without running a proxy.

| Pivot concept | Reuse in Verified MCP | Effort |
|---------------|------------------------|--------|
| **Provenance** (Source ID) | Add `assessmentRunId` and/or `evidenceBundleVersion` to server records and to daily brief metadata. Makes “where did this score come from?” explicit and audit-friendly. | Low: extend API response and optional DB/query fields. |
| **Integrity proof** | Add an optional `integrityDigest` (e.g. hash of score + evidence IDs + asOf) on server records or on daily snapshots. Consumers can verify “this snapshot hasn’t been altered.” No Merkle tree required. | Low–medium: hash at publish time, expose in JSON/RSS. |
| **Security context** | We don’t have “caller user ID”; we do have **assessment context**. Add `assessedBy: "SecAI Radar"`, `methodologyVersion`, `asOf` to every ranked output and feed. Makes attestation explicit. | Low: already have methodologyVersion in DailyTrustBrief; ensure it’s in rankings and RSS. |

**Outcome:** Our “Verified” badge and feeds align with the pivot’s idea of **verifiable, attributable context** without running live verification. Good for enterprise and analyst trust.

---

### B. Clear “Verified” definition

The pivot assumes a strict notion of “verified.” We can formalize ours and publish it.

- **Today:** `lastVerifiedAt` and `evidenceConfidence` exist but the exact rule is implicit.
- **Reuse:** Define and document: *“Verified = evidenceConfidence ≥ 2, lastVerifiedAt within last 7 days, and (optional) integrity digest present.”* Use this in UI, RSS, and API descriptions.

**Outcome:** One consistent, defensible definition of “Verified” that matches the pivot’s rigor and helps marketing (“we attest to this”).

---

### C. “Authority” framing in narrative and copy

The pivot’s value prop: *“Who secures the context from external tools? We attest to the payload.”*

- **Reuse:** Use that framing in **Daily Trust Brief** narrative, “About” / methodology pages, and RSS item descriptions. E.g. “SecAI Radar attests to the evidence and context behind each score” or “Independent attestation of MCP server trust posture.”
- **No code required:** Copy and positioning only.

**Outcome:** Same strategic story as the pivot, applied to the reporting product.

---

### D. Optional “verified response” shape in feeds

The pivot’s Gk schema defines what a “verified” payload looks like. We can define a **Verified MCP Feed** shape that mirrors it at the field level (without Merkle or real-time checks).

- **Reuse:** In RSS/JSON feed items (or a dedicated “attestation” feed), include:
  - `provenance`: `{ sourceId, asOf, methodologyVersion }`
  - `integrityDigest`: optional hash of the item body
  - `security_context`: e.g. `{ assessor: "SecAI Radar", scope: "public-ranking" }`

**Outcome:** Feed consumers get a consistent, Gk-friendly shape so that later, if we ever add live verification, the feed format is already aligned.

---

## 2. Ideas for ctxEco MCP

### A. Provenance in responses (no proxy)

The pivot cares about “where did this context come from?”

- **Reuse:** When ctxEco returns tool/output data, add optional **response metadata**: e.g. `X-SecAI-Provenance: source=ctxeco; timestamp=…; run_id=…` or a small JSON block `{ "provenance": { "source": "ctxeco", "timestamp": "…", "instance": "…" } }`.
- **Scope:** Start on one or two high-value endpoints (e.g. context for Foundry, or specific MCP tools). No proxy; ctxEco just adds headers or fields.

**Outcome:** Enterprises can trace “this context came from ctxEco at this time.” Supports the pivot’s “payload accountability” story from the tool side.

---

### B. Integrity digest on exports / evidence packs

The pivot’s “anti-tamper” idea is Merkle proofs. We can do a lighter version at export time.

- **Reuse:** For any **export** or **evidence pack** (e.g. audit pack, context snapshot), append a small manifest: `payload_hash`, `generated_at`, `source: secairadar.cloud` or `source: ctxeco`. Consumer (or a later SecAI Radar check) can verify the export wasn’t modified.
- **Where:** ctxEco export endpoints, or SecAI Radar’s registry/export APIs if they produce downloads.

**Outcome:** “Verified export” matches the pivot’s integrity story in a batch/export scenario.

---

### C. Structured (graph-like) output as an option

The pivot’s Gk standard uses **nodes and edges** so agents “reason only over edges.”

- **Reuse:** For **one** ctxEco capability (e.g. a specific tool or graph endpoint), offer an optional response shape: list of `nodes` and `edges` instead of or in addition to prose. No signing required initially; just the structure.
- **Scope:** Single use case (e.g. “context graph for X”) so we don’t redesign the whole MCP surface.

**Outcome:** Early compatibility with “graph knowledge” style consumption and a path to later Gk alignment.

---

### D. Caller/identity context in logs (auditability)

The pivot’s middleware “validates user’s Entra ID.” We’re not a proxy, but we can improve **auditability**.

- **Reuse:** When ctxEco is called in a context where **caller identity** or **tenant** is available (e.g. from Azure AI Foundry or from our own auth), log it (or a hash) with the request. “Who asked for what, when” becomes queryable for compliance.
- **Scope:** Logging/observability only; no change to response shape or auth model.

**Outcome:** Enterprises get “we know who used this tool,” which supports the pivot’s identity narrative from the tool side.

---

## 3. Summary Table

| Idea | Applies to | Effort | Delivers |
|------|------------|--------|----------|
| Provenance + assessmentRunId / evidenceBundleVersion | Verified MCP | Low | Clear “where did this come from” for scores and briefs |
| Optional integrityDigest on records/snapshots | Verified MCP | Low–medium | Snapshot-level tamper check for consumers |
| Formal “Verified” definition (evidence + recency + optional digest) | Verified MCP | Low | Single, publishable definition of Verified |
| “Authority” / attestation framing in copy and narratives | Verified MCP | None | Aligns messaging with pivot story |
| Gk-like fields in feeds (provenance, integrityDigest, security_context) | Verified MCP | Low | Feed shape ready for future verification |
| Response provenance (header or metadata) | ctxEco | Low | Traceability “this came from ctxEco at time X” |
| Integrity digest on exports / evidence packs | ctxEco or SecAI | Low | “Verified export” without Merkle |
| Optional nodes/edges response on one capability | ctxEco | Medium | Early graph-shaped output, Gk-friendly |
| Caller/tenant in logs (when available) | ctxEco | Low | Audit trail “who asked for what” |

---

## 4. What we are *not* doing (full pivot)

- We are **not** building the transparent proxy or mandatory gateway.
- We are **not** requiring Azure Policy or “all MCP via api.secairadar.cloud.”
- We are **not** implementing full Gk Merkle verification or a “hallucination firewall” in the request path.
- We are **not** changing our product from “daily report + rankings + RSS” to “Authority middleware.”

We are only reusing **vocabulary, optional fields, definitions, and light integrity/provenance features** so that both Verified MCP and ctxEco are stronger on attestation and traceability, and better aligned with the pivot story if we ever choose to move in that direction later.
