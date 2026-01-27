-- Staging area for latest_scores (T-051). Pipeline writes here; publisher validates and flips to latest_scores.
CREATE TABLE IF NOT EXISTS latest_scores_staging (
    server_id VARCHAR(16) NOT NULL,
    score_id VARCHAR(16) NOT NULL REFERENCES score_snapshots(score_id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (server_id)
);

CREATE INDEX IF NOT EXISTS idx_latest_scores_staging_score ON latest_scores_staging(score_id);
