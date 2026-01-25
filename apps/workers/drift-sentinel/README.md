# Drift Sentinel Worker

Diff + change classifier - detects meaningful changes

## Responsibilities
- Diff score snapshots (compare latest vs previous)
- Detect flag changes and evidence additions/removals
- Classify severity (Critical/High/Medium/Low)
- Generate drift events
- Calculate top movers/downgrades

## Schedule
Runs daily at 04:20 UTC (after Scorer)
