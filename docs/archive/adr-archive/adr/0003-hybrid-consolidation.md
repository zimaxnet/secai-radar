# ADR 0003: Hybrid consolidation via Azure Functions (Blob CSV → Table Storage) with summary export

- **Status:** Accepted
- **Date:** 2025-11-03

## Context
Consultants edit per-domain CSVs in the field. We need a cheap, reliable pipeline to normalize that data for dashboards, gap scoring, and Excel reassembly.

## Decision
Adopt a **Hybrid** consolidation pattern:
1) Source of truth: per-domain CSVs in **Blob Storage** under `assessments/{TenantId}/domains/`.
2) An **Azure Functions (Python)** consolidator validates CSVs and **upserts** rows into **Table Storage** (`Controls`, `TenantTools`).
3) Export **summary artifacts** (`summary.json` and/or `consolidated.xlsx`) back to Blob for Excel/BI.

## Options Considered
- Power Query in Excel only: simple but brittle (paths, schema drift), no automation.
- Full DB (Cosmos/Postgres) ingestion: powerful, but overkill/cost for MVP.
- **Hybrid (Chosen):** keeps CSV UX + adds automation, validation, and cheap query surface.

## Consequences
- + Cheap infra, easy local dev with Azurite.
- + Deterministic builds; CI-friendly validation.
- - Table Storage query limitations (acceptable for MVP; migrate to Cosmos when needed).

## Follow-ups
- Implement row-level validation and error reporting per CSV.
- Emit run metadata (counts, hash) for auditability.
