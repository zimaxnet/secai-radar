-- Add metadata_json column to mcp_servers for flexible metadata storage
-- Stores publisher, description, transport, package info, source_provenance, etc.

ALTER TABLE mcp_servers
ADD COLUMN IF NOT EXISTS metadata_json JSONB DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_mcp_servers_metadata ON mcp_servers USING GIN(metadata_json);

COMMENT ON COLUMN mcp_servers.metadata_json IS 'Flexible JSONB storage for publisher, description, transport, package, source_provenance, popularity signals, etc.';
