"""
Evidence packs (T-103, T-104, T-207): upload metadata, validation, list by workspace.
"""

import os
import secrets
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def _gen_id(prefix: str = "ep") -> str:
    return (prefix + secrets.token_hex(6))[:16]


def create_pack(
    db: Session,
    workspace_id: str,
    server_id: str,
    blob_ref: str,
    pack_id: Optional[str] = None,
) -> dict:
    """Insert evidence_packs row with status=Submitted. pack_id optional (generated if omitted)."""
    pack_id = pack_id or _gen_id()
    db.execute(
        text("""
            INSERT INTO evidence_packs (pack_id, workspace_id, server_id, blob_ref, status, submitted_at, created_at)
            VALUES (:pid, :wid, :sid, :ref, 'Submitted', NOW(), NOW())
        """),
        {"pid": pack_id, "wid": workspace_id, "sid": server_id, "ref": blob_ref},
    )
    db.flush()
    r = db.execute(
        text("SELECT pack_id, server_id, status, submitted_at FROM evidence_packs WHERE pack_id = :pid"),
        {"pid": pack_id},
    ).first()
    return {"packId": r[0], "serverId": r[1], "status": r[2], "submittedAt": r[3].isoformat() if r[3] else None}


def get_pack_workspace(db: Session, pack_id: str) -> Optional[str]:
    """Return workspace_id if pack exists, else None."""
    r = db.execute(text("SELECT workspace_id FROM evidence_packs WHERE pack_id = :pid"), {"pid": pack_id}).first()
    return r[0] if r else None


def list_packs(
    db: Session,
    workspace_id: str,
    server_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[dict]:
    """List evidence packs for workspace. Optional filters: server_id, status (Submitted|Validated|Rejected)."""
    q = """
        SELECT pack_id, server_id, status, submitted_at, validated_at, validated_by, confidence
        FROM evidence_packs
        WHERE workspace_id = :wid
    """
    params: dict = {"wid": workspace_id}
    if server_id is not None:
        q += " AND server_id = :sid"
        params["sid"] = server_id
    if status is not None:
        q += " AND status = :st"
        params["st"] = status
    q += " ORDER BY submitted_at DESC"
    rows = db.execute(text(q), params).fetchall()
    return [
        {
            "packId": r[0],
            "serverId": r[1],
            "status": r[2],
            "submittedAt": r[3].isoformat() if r[3] else None,
            "validatedAt": r[4].isoformat() if r[4] else None,
            "validatedBy": r[5],
            "confidence": r[6],
        }
        for r in rows
    ]


def set_validated(db: Session, pack_id: str, validated_by: str, confidence: Optional[int] = None) -> bool:
    """Set status=Validated, validated_at, validated_by, optional confidence. Returns True if updated."""
    result = db.execute(
        text("""
            UPDATE evidence_packs
            SET status = 'Validated', validated_at = NOW(), validated_by = :by,
                confidence = COALESCE(:conf, confidence), created_at = created_at
            WHERE pack_id = :pid
        """),
        {"pid": pack_id, "by": validated_by, "conf": confidence},
    )
    db.flush()
    return result.rowcount > 0
