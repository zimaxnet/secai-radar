"""
Registry API routes (private)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import get_db
from src.middleware.auth import get_current_user
from src.middleware.rbac import require_role, Role

router = APIRouter(prefix="/api/v1/private/registry", tags=["registry"])


@router.get("/servers")
async def list_servers(
    workspace_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workspace inventory servers"""
    # TODO: Implement actual query with workspace filtering
    return {
        "servers": [],
        "total": 0
    }


@router.post("/servers")
@require_role([Role.REGISTRY_ADMIN, Role.EVIDENCE_VALIDATOR])
async def add_server(
    workspace_id: str,
    server_data: dict,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add server to workspace inventory"""
    # TODO: Implement server creation
    return {"serverId": "new-server-id", "status": "created"}


@router.get("/policies")
async def list_policies(
    workspace_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workspace policies"""
    return {"policies": []}


@router.post("/policies")
@require_role([Role.REGISTRY_ADMIN, Role.POLICY_APPROVER])
async def create_policy(
    workspace_id: str,
    policy_data: dict,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create policy"""
    return {"policyId": "new-policy-id", "status": "created"}


@router.post("/evidence-packs")
@require_role([Role.REGISTRY_ADMIN, Role.EVIDENCE_VALIDATOR])
async def upload_evidence_pack(
    workspace_id: str,
    pack_data: dict,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload evidence pack"""
    return {"packId": "new-pack-id", "status": "uploaded"}


@router.post("/exports/audit-pack")
@require_role([Role.REGISTRY_ADMIN, Role.VIEWER])
async def create_audit_pack_export(
    workspace_id: str,
    export_params: dict,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create audit pack export"""
    return {"exportId": "new-export-id", "status": "queued"}
