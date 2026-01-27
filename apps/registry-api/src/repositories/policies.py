"""
Policies CRUD (T-101): list/create policies scoped by workspace.
"""

import json
import secrets
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


def _gen_id(prefix: str = "pol") -> str:
    return (prefix + secrets.token_hex(6))[:16]


def list_policies(db: Session, workspace_id: str) -> list[dict]:
    """List policies for workspace."""
    rows = db.execute(
        text("""
            SELECT policy_id, scope_json, decision, conditions_json, expires_at, created_at, updated_at
            FROM policies WHERE workspace_id = :wid ORDER BY created_at DESC
        """),
        {"wid": workspace_id},
    ).fetchall()
    return [
        {
            "policyId": r[0],
            "scope": r[1],
            "decision": r[2],
            "conditions": r[3],
            "expiresAt": r[4].isoformat() if r[4] else None,
            "createdAt": r[5].isoformat() if r[5] else None,
            "updatedAt": r[6].isoformat() if r[6] else None,
        }
        for r in rows
    ]


def create_policy(
    db: Session,
    workspace_id: str,
    scope: dict,
    decision: str,
    conditions: Optional[dict] = None,
    expires_at: Optional[datetime] = None,
) -> dict:
    """Insert policy. scope = {type: 'server'|'tool'|'category', value: str}; conditions = {evidenceConfidence, toolAgency, ...}."""
    policy_id = _gen_id()
    db.execute(
        text("""
            INSERT INTO policies (policy_id, workspace_id, scope_json, decision, conditions_json, expires_at, created_at, updated_at)
            VALUES (:pid, :wid, CAST(:scope AS jsonb), :decision, CAST(:cond AS jsonb), :exp, NOW(), NOW())
        """),
        {
            "pid": policy_id,
            "wid": workspace_id,
            "scope": json.dumps(scope),
            "decision": decision,
            "cond": json.dumps(conditions) if conditions else "{}",
            "exp": expires_at,
        },
    )
    db.flush()
    r = db.execute(
        text("SELECT policy_id, scope_json, decision, conditions_json, expires_at, created_at FROM policies WHERE policy_id = :pid"),
        {"pid": policy_id},
    ).first()
    return {
        "policyId": r[0],
        "scope": r[1],
        "decision": r[2],
        "conditions": r[3],
        "expiresAt": r[4].isoformat() if r[4] else None,
        "createdAt": r[5].isoformat() if r[5] else None,
    }


def get_policy_workspace(db: Session, policy_id: str) -> Optional[str]:
    """Return workspace_id if policy exists, else None."""
    r = db.execute(text("SELECT workspace_id FROM policies WHERE policy_id = :pid"), {"pid": policy_id}).first()
    return r[0] if r else None


def create_approval(
    db: Session,
    policy_id: str,
    approved_by: str,
    decision: str,
    notes: Optional[str] = None,
) -> dict:
    """Record approval. decision: Approved|Denied|Deferred."""
    aid = _gen_id(prefix="apr")
    db.execute(
        text("""
            INSERT INTO approvals (approval_id, policy_id, approved_by, approved_at, decision, notes, created_at)
            VALUES (:aid, :pid, :by, NOW(), :decision, :notes, NOW())
        """),
        {"aid": aid, "pid": policy_id, "by": approved_by, "decision": decision, "notes": notes or ""},
    )
    db.flush()
    r = db.execute(
        text("SELECT approval_id, policy_id, approved_by, decision, approved_at FROM approvals WHERE approval_id = :aid"),
        {"aid": aid},
    ).first()
    return {
        "approvalId": r[0],
        "policyId": r[1],
        "approvedBy": r[2],
        "decision": r[3],
        "approvedAt": r[4].isoformat() if r[4] else None,
    }
