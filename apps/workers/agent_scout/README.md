# Scout Worker

Discovery ingestor - finds MCP servers from multiple sources

## Responsibilities
- Pull from Tier 1 sources (official MCP registry, directories)
- Store raw observations with sourceUrl, retrievedAt, rawHash
- Append-only storage (never overwrite)

## Schedule
Runs daily at 02:30 UTC
