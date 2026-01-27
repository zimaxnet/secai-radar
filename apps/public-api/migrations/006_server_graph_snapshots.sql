-- Graph snapshots (Phase 4, T-120). From database-schema.sql lines 389–398.
CREATE TABLE IF NOT EXISTS server_graph_snapshots (
    snapshot_id VARCHAR(16) PRIMARY KEY,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    assessed_at TIMESTAMPTZ NOT NULL,
    graph_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_graph_snapshots_server ON server_graph_snapshots(server_id);
CREATE INDEX IF NOT EXISTS idx_graph_snapshots_assessed ON server_graph_snapshots(assessed_at DESC);
