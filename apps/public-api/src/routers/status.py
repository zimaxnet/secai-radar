"""
Status endpoint (T-081). Returns last successful pipeline run for stale-data banner.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Optional
from src.database import get_db

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """
    Get system status including last successful pipeline run and current run progress.
    FE uses lastSuccessfulRun to show a stale-data banner when >24h.
    """
    last_success: Optional[str] = None
    current_run: Optional[dict] = None
    
    try:
        # Get last successful run
        r = db.execute(
            text("""
                SELECT completed_at FROM pipeline_runs
                WHERE status IN ('Completed', 'success') AND completed_at IS NOT NULL
                ORDER BY completed_at DESC LIMIT 1
            """)
        ).first()
        if r and r[0]:
            last_success = r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0])
        
        # Get current running pipeline (if any)
        current = db.execute(
            text("""
                SELECT run_id, status, started_at, stages_json, errors_json
                FROM pipeline_runs
                WHERE status IN ('Running', 'running')
                ORDER BY started_at DESC LIMIT 1
            """)
        ).first()
        
        if current:
            import json
            stages = json.loads(current[3]) if current[3] else []
            errors = json.loads(current[4]) if current[4] else []
            current_run = {
                "runId": current[0],
                "status": current[1],
                "startedAt": current[2].isoformat() if hasattr(current[2], "isoformat") else str(current[2]),
                "stages": stages,
                "errors": errors[:5] if errors else [],  # Limit error output
            }
    except Exception as e:
        pass  # table may not exist yet or query failed

    return {
        "status": "operational",
        "lastSuccessfulRun": last_success,
        "currentRun": current_run,
        "timestamp": datetime.utcnow().isoformat(),
    }
