# Curator Worker

Normalizer + canonicalizer - resolves duplicates and creates stable IDs

## Responsibilities
- Generate canonical providerId and serverId
- Normalize names and URLs
- Deduplicate servers/providers
- Create alias records for ambiguous matches

## Schedule
Runs daily at 03:00 UTC (after Scout)
