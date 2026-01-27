"""
Registry API routes (private). All require workspace_id (query or X-Workspace-Id header) and enforce workspace-scoped RBAC via DB roles.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.middleware.rbac import require_workspace_roles, Role
from src.repositories import inventory as inv_repo
from src.repositories import policies as policies_repo
from src.repositories import evidence_packs as evidence_repo
from src.repositories import exports as exports_repo
from src.repositories import audit_log as audit_repo

router = APIRouter(prefix="/api/v1/private/registry", tags=["registry"])

# All roles (any member) for read-only list endpoints
ANY_MEMBER = [Role.REGISTRY_ADMIN, Role.POLICY_APPROVER, Role.EVIDENCE_VALIDATOR, Role.VIEWER, Role.AUTOMATION_OPERATOR]


class AddServerBody(BaseModel):
    serverId: str  # server_id or server_slug from mcp_servers
    owner: Optional[str] = None
    purpose: Optional[str] = None
    environment: Optional[str] = None


class CreatePolicyBody(BaseModel):
    scope: dict  # {type: 'server'|'tool'|'category', value: str}
    decision: str  # Allow | Deny | RequireApproval
    conditions: Optional[dict] = None  # evidenceConfidence, toolAgency, etc.
    expiresAt: Optional[str] = None  # ISO datetime


@router.get("/servers")
async def list_servers(
    ctx: dict = Depends(require_workspace_roles(ANY_MEMBER)),
    db: Session = Depends(get_db),
):
    """List workspace inventory servers. Requires workspace_id (query or X-Workspace-Id)."""
    items = inv_repo.list_inventory(db, ctx["workspace_id"])
    return {"servers": items, "total": len(items)}


@router.post("/servers")
async def add_server(
    body: AddServerBody,
    ctx: dict = Depends(require_workspace_roles([Role.REGISTRY_ADMIN, Role.EVIDENCE_VALIDATOR])),
    db: Session = Depends(get_db),
):
    """Add server to workspace inventory. serverId may be server_id or server_slug."""
    server_id = inv_repo.resolve_server_id(db, body.serverId)
    if not server_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    try:
        row = inv_repo.add_to_inventory(
            db, ctx["workspace_id"], server_id,
            owner=body.owner, purpose=body.purpose, environment=body.environment,
        )
        audit_repo.log(db, ctx["workspace_id"], ctx["user_id"], "inventory.add", "registry_inventory", str(row["inventoryId"]), {"serverId": server_id})
        db.commit()
        return {"serverId": row["serverId"], "inventoryId": row["inventoryId"], "status": "created"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Server already in workspace inventory")


@router.get("/policies")
async def list_policies(
    ctx: dict = Depends(require_workspace_roles(ANY_MEMBER)),
    db: Session = Depends(get_db),
):
    """List workspace policies."""
    items = policies_repo.list_policies(db, ctx["workspace_id"])
    return {"policies": items}


@router.post("/policies")
async def create_policy(
    body: CreatePolicyBody,
    ctx: dict = Depends(require_workspace_roles([Role.REGISTRY_ADMIN, Role.POLICY_APPROVER])),
    db: Session = Depends(get_db),
):
    """Create policy. decision: Allow|Deny|RequireApproval. conditions: evidenceConfidence, toolAgency, etc."""
    if body.decision not in ("Allow", "Deny", "RequireApproval"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="decision must be Allow, Deny, or RequireApproval")
    expires_at = None
    if body.expiresAt:
        try:
            from datetime import datetime
            expires_at = datetime.fromisoformat(body.expiresAt.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="expiresAt must be ISO format")
    row = policies_repo.create_policy(
        db, ctx["workspace_id"], body.scope, body.decision,
        conditions=body.conditions, expires_at=expires_at,
    )
    audit_repo.log(db, ctx["workspace_id"], ctx["user_id"], "policy.create", "policy", row["policyId"], {"decision": body.decision})
    db.commit()
    return {"policyId": row["policyId"], "status": "created"}


class ApproveDenyBody(BaseModel):
    notes: Optional[str] = None


@router.post("/policies/{policy_id}/approve")
async def approve_policy(
    policy_id: str,
    body: Optional[ApproveDenyBody] = None,
    ctx: dict = Depends(require_workspace_roles([Role.POLICY_APPROVER])),
    db: Session = Depends(get_db),
):
    """Approve policy. Requires PolicyApprover."""
    if policies_repo.get_policy_workspace(db, policy_id) != ctx["workspace_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    row = policies_repo.create_approval(db, policy_id, ctx["user_id"], "Approved", notes=body.notes if body else None)
    audit_repo.log(db, ctx["workspace_id"], ctx["user_id"], "policy.approve", "approval", row["approvalId"], {"policyId": policy_id})
    db.commit()
    return {"approvalId": row["approvalId"], "policyId": policy_id, "decision": "Approved"}


@router.post("/policies/{policy_id}/deny")
async def deny_policy(
    policy_id: str,
    body: Optional[ApproveDenyBody] = None,
    ctx: dict = Depends(require_workspace_roles([Role.POLICY_APPROVER])),
    db: Session = Depends(get_db),
):
    """Deny policy. Requires PolicyApprover."""
    if policies_repo.get_policy_workspace(db, policy_id) != ctx["workspace_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    row = policies_repo.create_approval(db, policy_id, ctx["user_id"], "Denied", notes=body.notes if body else None)
    db.commit()
    return {"approvalId": row["approvalId"], "policyId": policy_id, "decision": "Denied"}


def _upload_blob_or_placeholder(workspace_id: str, pack_id: str, contents: bytes, filename: str) -> str:
    """Return blob path. If Azure Storage configured, upload and return path; else return placeholder path."""
    import os
    try:
        conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container = os.getenv("AZURE_EVIDENCE_CONTAINER", "evidence-packs")
        if conn and container:
            from azure.storage.blob import BlobServiceClient
            client = BlobServiceClient.from_connection_string(conn)
            blob_path = f"{workspace_id}/{pack_id}/{filename or 'upload'}"
            blob = client.get_container_client(container).get_blob_client(blob_path)
            blob.upload_blob(contents, overwrite=True)
            return blob_path
    except Exception:
        pass
    return f"local/{workspace_id}/{pack_id}/{filename or 'upload'}"


@router.get("/evidence-packs")
async def list_evidence_packs(
    ctx: dict = Depends(require_workspace_roles(ANY_MEMBER)),
    db: Session = Depends(get_db),
    serverId: Optional[str] = None,
    status: Optional[str] = None,
):
    """List workspace evidence packs. Optional query: serverId, status (Submitted|Validated|Rejected)."""
    items = evidence_repo.list_packs(db, ctx["workspace_id"], server_id=serverId, status=status)
    return {"items": items, "total": len(items)}


@router.post("/evidence-packs")
async def upload_evidence_pack(
    ctx: dict = Depends(require_workspace_roles([Role.REGISTRY_ADMIN, Role.EVIDENCE_VALIDATOR])),
    db: Session = Depends(get_db),
    serverId: str = Form(...),
    file: Optional[UploadFile] = File(None),
):
    """Upload evidence pack. Pass serverId (form) and optionally file (multipart). Stores in private blob or placeholder path."""
    server_id = inv_repo.resolve_server_id(db, serverId)
    if not server_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    contents = b""
    filename = "upload"
    if file:
        contents = await file.read()
        filename = file.filename or "upload"
    pack_id = ("ep" + __import__("secrets").token_hex(6))[:16]
    blob_ref = _upload_blob_or_placeholder(ctx["workspace_id"], pack_id, contents, filename)
    row = evidence_repo.create_pack(db, ctx["workspace_id"], server_id, blob_ref, pack_id=pack_id)
    audit_repo.log(db, ctx["workspace_id"], ctx["user_id"], "evidence.upload", "evidence_pack", row["packId"], {"serverId": server_id})
    db.commit()
    return {"packId": row["packId"], "serverId": server_id, "status": "Submitted"}


@router.post("/evidence-packs/{pack_id}/validate")
async def validate_evidence_pack(
    pack_id: str,
    ctx: dict = Depends(require_workspace_roles([Role.EVIDENCE_VALIDATOR])),
    db: Session = Depends(get_db),
    confidence: Optional[int] = None,
):
    """Validate evidence pack. Sets status=Validated, validatedAt. Optional confidence 1–3. Recalculation hook is a stub."""
    if evidence_repo.get_pack_workspace(db, pack_id) != ctx["workspace_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence pack not found")
    if confidence is not None and not (1 <= confidence <= 3):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="confidence must be 1–3")
    if not evidence_repo.set_validated(db, pack_id, ctx["user_id"], confidence=confidence):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence pack not found")
    audit_repo.log(db, ctx["workspace_id"], ctx["user_id"], "evidence.validate", "evidence_pack", pack_id, {"confidence": confidence})
    db.commit()
    return {"packId": pack_id, "status": "Validated"}


class AuditPackExportBody(BaseModel):
    dateFrom: Optional[str] = None  # ISO date
    dateTo: Optional[str] = None   # ISO date


def _store_export_blob(workspace_id: str, export_id: str, payload: dict) -> str:
    """Write JSON to blob or placeholder; return blob path."""
    import os
    import json
    data = json.dumps(payload, default=str).encode("utf-8")
    path = f"{workspace_id}/exports/{export_id}/audit-pack.json"
    try:
        conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container = os.getenv("AZURE_EXPORTS_CONTAINER", "exports")
        if conn and container:
            from azure.storage.blob import BlobServiceClient
            client = BlobServiceClient.from_connection_string(conn)
            blob = client.get_container_client(container).get_blob_client(path)
            blob.upload_blob(data, overwrite=True)
            return path
    except Exception:
        pass
    return f"local/{path}"


@router.post("/exports/audit-pack")
async def create_audit_pack_export(
    body: Optional[AuditPackExportBody] = None,
    ctx: dict = Depends(require_workspace_roles([Role.REGISTRY_ADMIN, Role.VIEWER])),
    db: Session = Depends(get_db),
):
    """Create audit pack export (inventory, policies, scores, drift). Returns exportId; poll GET /exports/{id} for status and download URL."""
    req = {"dateFrom": body.dateFrom if body else None, "dateTo": body.dateTo if body else None}
    export_id = exports_repo.create_export(db, ctx["workspace_id"], req)
    st = "Queued"
    try:
        payload = exports_repo.build_audit_json(db, ctx["workspace_id"], req.get("dateFrom"), req.get("dateTo"))
        blob_ref = _store_export_blob(ctx["workspace_id"], export_id, payload)
        exports_repo.set_export_completed(db, export_id, blob_ref)
        st = "Completed"
    except Exception as e:
        exports_repo.set_export_failed(db, export_id, str(e))
        st = "Failed"
    audit_repo.log(db, ctx["workspace_id"], ctx["user_id"], "export.audit_pack", "export", export_id, {"status": st, "request": req})
    db.commit()
    return {"exportId": export_id, "status": st}


@router.get("/exports/{export_id}")
async def get_export_status(
    export_id: str,
    ctx: dict = Depends(require_workspace_roles(ANY_MEMBER)),
    db: Session = Depends(get_db),
):
    """Get export status. When status=Completed, blobRef is set (signed URL in future)."""
    row = exports_repo.get_export(db, export_id, ctx["workspace_id"])
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return {"exportId": row["exportId"], "status": row["status"], "blobRef": row.get("blobRef"), "completedAt": row.get("completedAt"), "errorMessage": row.get("errorMessage")}
