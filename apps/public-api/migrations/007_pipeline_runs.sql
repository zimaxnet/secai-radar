-- Pipeline run logging (T-080). One row per full run; status endpoint uses latest successful.
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR(32) PRIMARY KEY,
    trigger VARCHAR(64) NOT NULL DEFAULT 'manual',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'running',  -- running | success | failed
    stages_json JSONB,   -- optional per-stage timestamps/status
    errors_json JSONB,   -- optional error details
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started ON pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status) WHERE status = 'success';
