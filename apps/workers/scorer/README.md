# Scorer Worker

Trust Score v1 evaluator - computes scores + evidence confidence

## Responsibilities
- Compute score snapshot per server using packages/scoring library
- Write append-only score_snapshots
- Update latest_scores pointer (staging first)

## Schedule
Runs daily at 04:00 UTC (after Evidence Miner)
