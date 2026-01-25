"""
Status endpoint
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from src.database import get_db

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """
    Get system status including last successful pipeline run
    """
    # TODO: Query pipeline_runs table for last successful run
    # For now, return placeholder
    
    return {
        "status": "operational",
        "lastSuccessfulRun": None,  # Will be datetime from pipeline_runs
        "timestamp": datetime.utcnow().isoformat()
    }
