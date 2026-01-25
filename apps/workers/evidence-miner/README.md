# Evidence Miner Worker

Docs/repo extractor - extracts structured posture signals

## Responsibilities
- Parse docs/repo for evidence items
- Extract claims: AuthModel, HostingCustody, ToolAgency hints
- Store evidence items with sourceEvidenceId and capturedAt
- Calculate content hash for drift detection

## Schedule
Runs daily at 03:20 UTC (after Curator)
