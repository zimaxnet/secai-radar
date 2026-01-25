# Publisher Worker

Atomic publish worker - dashboards + feeds + API

## Responsibilities
- Run validation checks
- Flip stable pointers (atomic swap)
- Refresh rankings cache
- Ensure feeds read latest daily brief

## Schedule
Runs daily at 05:00 UTC (after Daily Brief)
