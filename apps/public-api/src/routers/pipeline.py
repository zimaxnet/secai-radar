"""
Pipeline runs endpoint - view pipeline run history and progress
"""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from src.database import get_db

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/pipeline/runs")
async def get_pipeline_runs(
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None, regex="^(Running|Completed|Failed|Partial|running|success|failed)$"),
    db: Session = Depends(get_db)
):
    """
    Get recent pipeline runs with status and progress.
    Useful for monitoring pipeline execution.
    """
    try:
        query = """
            SELECT run_id, date, status, started_at, completed_at, 
                   stages_json, deliverables_json, errors_json
            FROM pipeline_runs
            WHERE 1=1
        """
        params = []
        
        if status:
            # Normalize status values
            if status.lower() in ('success', 'completed'):
                query += " AND status IN ('Completed', 'success')"
            elif status.lower() == 'failed':
                query += " AND status IN ('Failed', 'failed')"
            elif status.lower() == 'running':
                query += " AND status IN ('Running', 'running')"
            else:
                query += " AND status = %s"
                params.append(status)
        
        query += " ORDER BY started_at DESC LIMIT %s"
        params.append(limit)
        
        rows = db.execute(text(query), params).fetchall()
        
        runs: List[Dict[str, Any]] = []
        for row in rows:
            import json
            runs.append({
                "runId": row[0],
                "date": str(row[1]) if row[1] else None,
                "status": row[2],
                "startedAt": row[3].isoformat() if row[3] and hasattr(row[3], "isoformat") else str(row[3]) if row[3] else None,
                "completedAt": row[4].isoformat() if row[4] and hasattr(row[4], "isoformat") else str(row[4]) if row[4] else None,
                "stages": json.loads(row[5]) if row[5] else [],
                "deliverables": json.loads(row[6]) if row[6] else {},
                "errors": json.loads(row[7]) if row[7] else [],
            })
        
        return {
            "runs": runs,
            "count": len(runs),
        }
    except Exception as e:
        return {
            "runs": [],
            "count": 0,
            "error": str(e),
        }


@router.get("/pipeline/runs/{run_id}")
async def get_pipeline_run(
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific pipeline run.
    """
    try:
        row = db.execute(
            text("""
                SELECT run_id, date, status, started_at, completed_at,
                       stages_json, deliverables_json, errors_json
                FROM pipeline_runs
                WHERE run_id = %s
            """),
            (run_id,)
        ).first()
        
        if not row:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Pipeline run not found")
        
        import json
        return {
            "runId": row[0],
            "date": str(row[1]) if row[1] else None,
            "status": row[2],
            "startedAt": row[3].isoformat() if row[3] and hasattr(row[3], "isoformat") else str(row[3]) if row[3] else None,
            "completedAt": row[4].isoformat() if row[4] and hasattr(row[4], "isoformat") else str(row[4]) if row[4] else None,
            "stages": json.loads(row[5]) if row[5] else [],
            "deliverables": json.loads(row[6]) if row[6] else {},
            "errors": json.loads(row[7]) if row[7] else [],
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
