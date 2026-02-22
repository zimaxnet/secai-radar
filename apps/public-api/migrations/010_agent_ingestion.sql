-- Add observation_type to distinguish agent payloads from MCP payloads
ALTER TABLE raw_observations ADD COLUMN IF NOT EXISTS observation_type VARCHAR(20) NOT NULL DEFAULT 'mcp';

-- Create queue for user submissions
CREATE TABLE IF NOT EXISTS submissions_queue (
    submission_id SERIAL PRIMARY KEY,
    repo_url TEXT NOT NULL,
    integration_type VARCHAR(20) NOT NULL, -- 'mcp' or 'agent'
    contact_email VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_submissions_queue_status_type ON submissions_queue(status, integration_type);
