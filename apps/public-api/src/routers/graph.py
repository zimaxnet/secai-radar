"""
Graph API endpoint
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from src.database import get_db
from src.services.server import get_server_by_id_or_slug

router = APIRouter(prefix="/api/v1/public/mcp", tags=["public"])


@router.get("/servers/{idOrSlug}/graph")
async def get_server_graph(
    idOrSlug: str,
    db: Session = Depends(get_db)
):
    """Get server graph (redacted for public)"""
    server = get_server_by_id_or_slug(db, idOrSlug)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Get latest graph snapshot
    # Note: This uses raw SQL for now - would use SQLAlchemy models in production
    import psycopg2
    conn = db.connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT graph_json
            FROM server_graph_snapshots
            WHERE server_id = %s
            ORDER BY assessed_at DESC
            LIMIT 1
        """, (server.server_id,))
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        graph = row[0]
        
        # Redact private references
        # Remove blob_refs, internal metadata, etc.
        if isinstance(graph, dict):
            # Remove private fields from nodes
            for node in graph.get("nodes", []):
                node.get("properties", {}).pop("blob_ref", None)
                node.get("properties", {}).pop("workspace_id", None)
        
        return {
            "methodologyVersion": "v1.0",
            "generatedAt": datetime.utcnow().isoformat(),
            "data": graph
        }
