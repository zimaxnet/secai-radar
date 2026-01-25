# Graph Builder Worker

Builds per-server graph snapshots for GK Explorer

## Responsibilities
- Build per-server graph: Server → Tools → Scopes → DataDomains → Evidence → Flags
- Create nodes (14 node types) and edges (13 edge types)
- Store graph JSON in server_graph_snapshots table

## Schedule
Runs after Scorer (04:10 UTC)
