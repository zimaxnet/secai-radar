-- Raw observations from Scout (T-070). Append-only discovery ingest.
-- sourceUrl + retrievedAt + rawHash (content_hash); no overwrites.

CREATE TABLE IF NOT EXISTS raw_observations (
    observation_id VARCHAR(32) NOT NULL PRIMARY KEY,
    source_url TEXT NOT NULL,
    content_json TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_raw_observations_content_hash ON raw_observations(content_hash);
CREATE INDEX IF NOT EXISTS idx_raw_observations_retrieved ON raw_observations(retrieved_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_observations_processed ON raw_observations(processed_at) WHERE processed_at IS NULL;
