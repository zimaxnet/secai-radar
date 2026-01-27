"""
Audit logging for private registry (T-131). Append-only; queryable by workspace admin.
"""

import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


def log(
    db: Session,
    workspace_id: str,
    user_id: str,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    """Append one audit log record. No-op if audit_log table is missing (migration 005 not applied)."""
    try:
        db.execute(
            text("""
                INSERT INTO audit_log (workspace_id, user_id, action, resource_type, resource_id, details, created_at)
                VALUES (:wid, :uid, :action, :rtype, :rid, CAST(:details AS jsonb), NOW())
            """),
            {
                "wid": workspace_id,
                "uid": user_id,
                "action": action,
                "rtype": resource_type,
                "rid": resource_id,
                "details": json.dumps(details) if details else "{}",
            },
        )
        db.flush()
    except Exception:
        pass
