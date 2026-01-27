"""
Workspace and membership model access (T-091).
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def get_workspace(db: Session, workspace_id: str) -> Optional[dict]:
    """Return workspace by id or None."""
    r = db.execute(
        text("SELECT workspace_id, tenant_id, name FROM workspaces WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    ).first()
    if not r:
        return None
    return {"workspace_id": r[0], "tenant_id": r[1], "name": r[2]}


def get_user_roles_in_workspace(db: Session, workspace_id: str, user_id: str) -> list[str]:
    """Return list of roles for user in workspace (empty if not a member)."""
    r = db.execute(
        text("""
            SELECT role FROM workspace_members
            WHERE workspace_id = :wid AND user_id = :uid
        """),
        {"wid": workspace_id, "uid": user_id},
    ).fetchall()
    return [row[0] for row in r]


def get_workspace_ids_for_user(db: Session, user_id: str) -> list[str]:
    """Return workspace_ids the user is a member of."""
    r = db.execute(
        text("SELECT workspace_id FROM workspace_members WHERE user_id = :uid"),
        {"uid": user_id},
    ).fetchall()
    return [row[0] for row in r]
