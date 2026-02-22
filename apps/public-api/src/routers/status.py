"""
Status endpoint (T-081). Returns last successful pipeline run for stale-data banner.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
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
    last_pipeline_run: Optional[str] = None
    current_run: Optional[dict] = None
    
    try:
        # Get last successful run (supports legacy and newer status values)
        r = db.execute(
            text("""
                SELECT completed_at FROM pipeline_runs
                WHERE LOWER(status) IN ('completed', 'success', 'succeeded')
                  AND completed_at IS NOT NULL
                ORDER BY completed_at DESC LIMIT 1
            """)
        ).first()
        if r and r[0]:
            last_success = r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0])

        # Get most recent pipeline run (regardless of success/failure)
        latest = db.execute(
            text("""
                SELECT COALESCE(completed_at, started_at) AS run_at
                FROM pipeline_runs
                ORDER BY COALESCE(completed_at, started_at) DESC
                LIMIT 1
            """)
        ).first()
        if latest and latest[0]:
            last_pipeline_run = latest[0].isoformat() if hasattr(latest[0], "isoformat") else str(latest[0])
        
        # Get current running pipeline (if any)
        current = db.execute(
            text("""
                SELECT run_id, status, started_at, stages_json, errors_json
                FROM pipeline_runs
                WHERE LOWER(status) IN ('running', 'in_progress', 'processing')
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

    payload = {
        "status": "operational",
        "lastSuccessfulRun": last_success,
        "lastPipelineRun": last_pipeline_run,
        "currentRun": current_run,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Never cache status so stale banner always reflects latest pipeline activity.
    return JSONResponse(
        content=payload,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
