---
layout: default
title: Trust Scoring Methodology
---

# Trust Scoring Methodology

SecAI Radar calculates a dynamic **0-100 Trust Score** for each tracked integration (MCP Server or AI Agent).

## Core Assessment Domains

The score is derived from six foundational domains:

1. **D1: Authentication** (How does the server verify inbound connections?)
2. **D2: Authorization** (What level of access control does it enforce?)
3. **D3: Data Protection** (Encryption in transit and at rest)
4. **D4: Audit & Logging** (Can actions be traced?)
5. **D5: Operational Security** (Vulnerability disclosures, patching)
6. **D6: Compliance** (SBOM presence, residency)

## Temporal Decay Mechanism

To ensure rankings reflect active, maintained projects, the engine applies a **Decay Factor**.
If an integration has not been observed active (no commits, registry updates, or pings) within a set threshold (e.g. 30, 60, 90 days), its core Trust Score slowly decays. This prevents abandoned repositories from holding high visibility simply because they were secure a year ago.

## Agentic Access

The methodology relies on the `analyzer` background worker synthesizing gathered payloads without human review logic. If evidence isn't programmatically available, the integration score naturally degrades, enforcing an "Agentic First" responsibility on authors to publish machine-readable security policies.
