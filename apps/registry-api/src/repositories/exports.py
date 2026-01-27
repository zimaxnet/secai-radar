"""
Audit pack exports (T-105): create export row, build JSON, store in blob.
"""

import json
import os
import secrets
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


def _gen_id(prefix: str = "ex") -> str:
    return (prefix + secrets.token_hex(6))[:16]


def create_export(db: Session, workspace_id: str, request_json: dict) -> str:
    """Insert exports row (Queued). Returns export_id."""
    eid = _gen_id()
    db.execute(
        text("""
            INSERT INTO exports (export_id, workspace_id, status, requested_at, request_json, created_at)
            VALUES (:eid, :wid, 'Queued', NOW(), CAST(:req AS jsonb), NOW())
        """),
        {"eid": eid, "wid": workspace_id, "req": json.dumps(request_json)},
    )
    db.flush()
    return eid


def set_export_completed(db: Session, export_id: str, blob_ref: str) -> None:
    """Set status=Completed, blob_ref, completed_at."""
    db.execute(
        text("""
            UPDATE exports SET status = 'Completed', blob_ref = :ref, completed_at = NOW() WHERE export_id = :eid
        """),
        {"eid": export_id, "ref": blob_ref},
    )
    db.flush()


def set_export_failed(db: Session, export_id: str, error_message: str) -> None:
    """Set status=Failed, error_message."""
    db.execute(
        text("""
            UPDATE exports SET status = 'Failed', error_message = :msg WHERE export_id = :eid
        """),
        {"eid": export_id, "msg": error_message},
    )
    db.flush()


def get_export(db: Session, export_id: str, workspace_id: str) -> Optional[dict]:
    """Return export row if it belongs to workspace."""
    r = db.execute(
        text("""
            SELECT export_id, status, blob_ref, requested_at, completed_at, error_message, request_json
            FROM exports WHERE export_id = :eid AND workspace_id = :wid
        """),
        {"eid": export_id, "wid": workspace_id},
    ).first()
    if not r:
        return None
    return {
        "exportId": r[0],
        "status": r[1],
        "blobRef": r[2],
        "requestedAt": r[3].isoformat() if r[3] else None,
        "completedAt": r[4].isoformat() if r[4] else None,
        "errorMessage": r[5],
        "requestJson": r[6],
    }


def build_audit_json(db: Session, workspace_id: str, date_from: Optional[str], date_to: Optional[str]) -> dict:
    """Build audit pack payload: inventory, policies, scores, drift for date range."""
    inv = db.execute(
        text("""
            SELECT ri.inventory_id, ri.server_id, ri.owner, ri.purpose, ri.environment, ri.status, m.server_slug, m.server_name
            FROM registry_inventory ri JOIN mcp_servers m ON m.server_id = ri.server_id
            WHERE ri.workspace_id = :wid
        """),
        {"wid": workspace_id},
    ).fetchall()
    policies = db.execute(
        text("SELECT policy_id, scope_json, decision, conditions_json, expires_at FROM policies WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    ).fetchall()
    server_ids = [r[1] for r in inv]
    payload = {
        "exportedAt": datetime.utcnow().isoformat() + "Z",
        "workspaceId": workspace_id,
        "dateFrom": date_from,
        "dateTo": date_to,
        "inventory": [
            {"inventoryId": r[0], "serverId": r[1], "owner": r[2], "purpose": r[3], "environment": r[4], "status": r[5], "serverSlug": r[6], "serverName": r[7]}
            for r in inv
        ],
        "policies": [
            {"policyId": r[0], "scope": r[1], "decision": r[2], "conditions": r[3], "expiresAt": r[4].isoformat() if r[4] else None}
            for r in policies
        ],
        "scores": [],
        "drift": [],
    }
    # Scores: score_snapshots for servers in inventory, filtered by date if present
    try:
        if server_ids and date_from and date_to:
            rows = db.execute(
                text("""
                    SELECT ss.server_id, ss.trust_score, ss.tier, ss.assessed_at
                    FROM score_snapshots ss
                    WHERE ss.server_id = ANY(:sids) AND ss.assessed_at::date >= :dfrom::date AND ss.assessed_at::date <= :dto::date
                    ORDER BY ss.assessed_at DESC
                """),
                {"sids": server_ids, "dfrom": date_from, "dto": date_to},
            ).fetchall()
        elif server_ids:
            rows = db.execute(
                text("""
                    SELECT server_id, trust_score, tier, assessed_at
                    FROM score_snapshots
                    WHERE server_id = ANY(:sids)
                    ORDER BY assessed_at DESC
                """),
                {"sids": server_ids},
            ).fetchall()
        else:
            rows = []
        payload["scores"] = [{"serverId": r[0], "trustScore": float(r[1]), "tier": r[2], "assessedAt": r[3].isoformat() if r[3] else None} for r in rows]
    except Exception:
        pass
    # Drift: drift_events if table exists, for date range
    try:
        if date_from and date_to and server_ids:
            drift_rows = db.execute(
                text("""
                    SELECT server_id, event_type, detected_at, details
                    FROM drift_events
                    WHERE server_id = ANY(:sids) AND detected_at::date >= :dfrom::date AND detected_at::date <= :dto::date
                """),
                {"sids": server_ids, "dfrom": date_from, "dto": date_to},
            ).fetchall()
        else:
            drift_rows = []
        payload["drift"] = [{"serverId": r[0], "eventType": r[1], "detectedAt": r[2].isoformat() if r[2] else None, "details": r[3]} for r in drift_rows]
    except Exception:
        pass
    return payload
