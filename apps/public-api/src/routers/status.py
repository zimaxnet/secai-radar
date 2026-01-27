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
    Get system status including last successful pipeline run.
    FE uses lastSuccessfulRun to show a stale-data banner when >24h.
    """
    last_success: Optional[str] = None
    try:
        r = db.execute(
            text("""
                SELECT completed_at FROM pipeline_runs
                WHERE status = 'success' AND completed_at IS NOT NULL
                ORDER BY completed_at DESC LIMIT 1
            """)
        ).first()
        if r and r[0]:
            last_success = r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0])
    except Exception:
        pass  # table may not exist yet

    return {
        "status": "operational",
        "lastSuccessfulRun": last_success,
        "timestamp": datetime.utcnow().isoformat(),
    }
