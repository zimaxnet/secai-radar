# ADR 0001: Azure-native, cost-first architecture (SWA + Functions + Tables/Blobs)

- **Status:** Accepted
- **Date:** 2025-11-03

## Context
We need a low-cost, low-friction stack to support consultants running Azure security assessments across customers, with easy auth and simple local dev.

## Decision
Use **Azure Static Web Apps** (hosting + Entra auth) + **Azure Functions (Python)** for API, and **Azure Table Storage + Blob Storage** for data and artifacts.

## Options Considered
- SWA + Functions + Tables/Blobs (Chosen): minimal infra, easy auth, cheap, quick to ship.
- AKS + managed Postgres: powerful but heavy and costly for MVP.
- App Service + Cosmos DB (serverless): flexible but more moving parts initially.

## Consequences
- + Easy local dev with Azurite; quick deploys.
- + Lowest cost footprint for MVP.
- - Table Storage has limited query semantics; may migrate to Cosmos serverless later.
- Follow-ups: define partition/row key patterns; add CI validation for schemas.

## References
- SecAI Radar Build Brief
