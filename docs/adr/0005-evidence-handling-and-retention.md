# ADR 0005: Evidence handling & retention (Blob + SAS + lifecycle)

- **Status:** Proposed
- **Date:** 2025-11-03

## Context
Assessments collect sensitive evidence (screenshots, exports). We need a low-cost, safe approach with minimal operational burden and clear retention.

## Decision
- **Storage:** Evidence in **Blob Storage** at `assessments/{TenantId}/evidence/{ControlID}/...`.
- **Access:** Use **SAS URLs** with short TTL for downloads/uploads; prefer **Managed Identity** for server-side access.
- **Classification:** Tag evidence metadata (`sensitivity`, `source`, `owner`, `retention`) alongside pointers in a simple `Evidence` table (optional in MVP).
- **Retention:** Default **180 days** post-assessment; configurable per customer. Support legal hold flag.
- **Privacy:** Redact PII where feasible; avoid raw secrets in files; enforce max file size and allowed types.

## Options Considered
- Embedding evidence in Table/DB: not suitable for binaries.
- External doc systems (SharePoint/Jira): adds friction/integration work.
- **Blob + SAS (Chosen):** simple, secure, auditable, cost-effective.

## Consequences
- + Clear, revocable access links; minimal back-end code.
- + Lifecycle management via Blob policies.
- - Need a simple reviewer workflow for acceptance/redaction (future).

## Follow-ups
- Implement SAS helper in API, with role checks.
- Add a lifecycle policy on the evidence container.
