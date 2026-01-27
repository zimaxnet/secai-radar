-- Fix latest_scores to point to highest-scoring snapshots instead of latest
-- This ensures rankings show the best scores, not just the most recent (which might be zero)

-- Update latest_scores to use highest-scoring snapshots
UPDATE latest_scores ls
SET score_id = (
    SELECT score_id 
    FROM score_snapshots ss
    WHERE ss.server_id = ls.server_id
    ORDER BY ss.trust_score DESC, ss.assessed_at DESC
    LIMIT 1
)
WHERE EXISTS (
    SELECT 1 
    FROM score_snapshots ss
    WHERE ss.server_id = ls.server_id
);

-- Also update latest_scores_staging if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'latest_scores_staging'
    ) THEN
        UPDATE latest_scores_staging ls
        SET score_id = (
            SELECT score_id 
            FROM score_snapshots ss
            WHERE ss.server_id = ls.server_id
            ORDER BY ss.trust_score DESC, ss.assessed_at DESC
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 
            FROM score_snapshots ss
            WHERE ss.server_id = ls.server_id
        );
    END IF;
END $$;

COMMENT ON TABLE latest_scores IS 'Points to highest-scoring snapshot per server (not just latest)';
