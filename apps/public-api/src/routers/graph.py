"""
Graph API endpoint (T-121). GET /api/v1/public/mcp/servers/{idOrSlug}/graph
Returns latest snapshot redacted; 200 with empty nodes/edges when missing.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from src.database import get_db
from src.services.server import get_server_by_id_or_slug

router = APIRouter(prefix="/api/v1/public/mcp", tags=["public"])


def _redact(graph: dict) -> dict:
    if not isinstance(graph, dict):
        return graph
    for node in graph.get("nodes", []):
        props = node.get("properties") or {}
        props.pop("blob_ref", None)
        props.pop("workspace_id", None)
    return graph


@router.get("/servers/{idOrSlug}/graph")
async def get_server_graph(
    idOrSlug: str,
    db: Session = Depends(get_db)
):
    """Get server graph (redacted). 200 with empty data when no snapshot."""
    server = get_server_by_id_or_slug(db, idOrSlug)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    server_id = getattr(server, "server_id", server) if hasattr(server, "server_id") else str(server)

    row = db.execute(
        text("""
            SELECT graph_json FROM server_graph_snapshots
            WHERE server_id = :sid ORDER BY assessed_at DESC LIMIT 1
        """),
        {"sid": server_id},
    ).first()

    if not row or not row[0]:
        return {
            "methodologyVersion": "v1.0",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "data": {"nodes": [], "edges": []},
            "meta": {"hasSnapshot": False},
        }

    graph = _redact(dict(row[0]) if hasattr(row[0], "items") else (row[0] or {"nodes": [], "edges": []}))
    return {
        "methodologyVersion": "v1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "data": graph,
        "meta": {"hasSnapshot": True},
    }
