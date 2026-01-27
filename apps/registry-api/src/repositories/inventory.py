"""
Registry inventory access (T-100): list/add servers in workspace.
"""

import secrets
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def list_inventory(db: Session, workspace_id: str) -> list[dict]:
    """List registry_inventory rows for workspace. Joins mcp_servers for slug/name."""
    rows = db.execute(
        text("""
            SELECT ri.inventory_id, ri.server_id, ri.owner, ri.purpose, ri.environment, ri.status, ri.created_at,
                   m.server_slug, m.server_name
            FROM registry_inventory ri
            JOIN mcp_servers m ON m.server_id = ri.server_id
            WHERE ri.workspace_id = :wid
            ORDER BY ri.created_at DESC
        """),
        {"wid": workspace_id},
    ).fetchall()
    return [
        {
            "inventoryId": r[0],
            "serverId": r[1],
            "owner": r[2],
            "purpose": r[3],
            "environment": r[4],
            "status": r[5],
            "createdAt": r[6].isoformat() if r[6] else None,
            "serverSlug": r[7],
            "serverName": r[8],
        }
        for r in rows
    ]


def resolve_server_id(db: Session, server_id_or_slug: str) -> Optional[str]:
    """Return mcp_servers.server_id for given server_id or server_slug."""
    r = db.execute(
        text("SELECT server_id FROM mcp_servers WHERE server_id = :v OR server_slug = :v"),
        {"v": server_id_or_slug},
    ).first()
    return r[0] if r else None


def add_to_inventory(
    db: Session,
    workspace_id: str,
    server_id: str,
    owner: Optional[str] = None,
    purpose: Optional[str] = None,
    environment: Optional[str] = None,
) -> dict:
    """Insert into registry_inventory. Returns the new row. Raises if (workspace_id, server_id) exists."""
    db.execute(
        text("""
            INSERT INTO registry_inventory (workspace_id, server_id, owner, purpose, environment, status, created_at, updated_at)
            VALUES (:wid, :sid, :owner, :purpose, :env, 'Active', NOW(), NOW())
        """),
        {"wid": workspace_id, "sid": server_id, "owner": owner, "purpose": purpose, "env": environment},
    )
    db.flush()
    r = db.execute(
        text("""
            SELECT inventory_id, server_id, owner, purpose, environment, status, created_at
            FROM registry_inventory WHERE workspace_id = :wid AND server_id = :sid
        """),
        {"wid": workspace_id, "sid": server_id},
    ).first()
    return {
        "inventoryId": r[0],
        "serverId": r[1],
        "owner": r[2],
        "purpose": r[3],
        "environment": r[4],
        "status": r[5],
        "createdAt": r[6].isoformat() if r[6] else None,
    }
