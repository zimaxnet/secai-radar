"""
Control Detail API Routes
Provides endpoints for individual control management and evidence collection
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

from ..services.storage import get_storage_service

router = APIRouter(prefix="/api/tenant/{tenant_id}", tags=["controls"])


class ControlUpdate(BaseModel):
    Status: Optional[str] = None
    Owner: Optional[str] = None
    Notes: Optional[str] = None
    ScoreNumeric: Optional[float] = None


class EvidenceItem(BaseModel):
    control_id: str
    file_name: str
    file_url: str
    evidence_type: str
    description: Optional[str] = None


@router.get("/control/{control_id}")
async def get_control_detail(tenant_id: str, control_id: str):
    """Get detailed information for a specific control"""
    try:
        storage = get_storage_service()
        table = storage.get_controls_table()
        
        # Find control by scanning partitions (we need to find which domain it's in)
        controls = [
            e for e in table.list_entities()
            if str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|") and e.get("RowKey") == control_id
        ]
        
        if not controls:
            raise HTTPException(status_code=404, detail="Control not found")
        
        control = dict(controls[0])
        
        # Load related evidence (would be stored in blob storage or separate table)
        # For now, return control with placeholder for evidence
        control["Evidence"] = []  # TODO: Load from blob storage
        
        return control
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/control/{control_id}")
async def update_control(tenant_id: str, control_id: str, update: ControlUpdate):
    """Update a control's status, owner, notes, or score"""
    try:
        storage = get_storage_service()
        table = storage.get_controls_table()
        
        # Find the control
        controls = [
            e for e in table.list_entities()
            if str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|") and e.get("RowKey") == control_id
        ]
        
        if not controls:
            raise HTTPException(status_code=404, detail="Control not found")
        
        control = dict(controls[0])
        
        # Update fields
        if update.Status is not None:
            control["Status"] = update.Status
        if update.Owner is not None:
            control["Owner"] = update.Owner
        if update.Notes is not None:
            control["Notes"] = update.Notes
        if update.ScoreNumeric is not None:
            control["ScoreNumeric"] = update.ScoreNumeric
        
        table.upsert_entity(control)
        
        return {"ok": True, "control": control}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control/{control_id}/evidence")
async def upload_evidence(
    tenant_id: str,
    control_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Query(None)
):
    """Upload evidence for a control"""
    try:
        storage = get_storage_service()
        container = storage.get_blob_container()
        
        # Generate blob name: tenant/control_id/timestamp_filename
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"{tenant_id}/{control_id}/{timestamp}_{file.filename}"
        
        # Upload file to blob storage
        blob_client = container.get_blob_client(blob_name)
        content = await file.read()
        blob_client.upload_blob(content, overwrite=True)
        
        # Get blob URL
        blob_url = blob_client.url
        
        # TODO: Store evidence metadata in a separate table or add to control entity
        
        return {
            "ok": True,
            "evidence": {
                "control_id": control_id,
                "file_name": file.filename,
                "file_url": blob_url,
                "evidence_type": file.content_type or "application/octet-stream",
                "description": description,
                "uploaded_at": timestamp
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/control/{control_id}/evidence")
async def get_control_evidence(tenant_id: str, control_id: str):
    """Get all evidence for a control"""
    try:
        storage = get_storage_service()
        container = storage.get_blob_container()
        
        # List blobs in the control's folder
        blobs = container.list_blobs(name_starts_with=f"{tenant_id}/{control_id}/")
        
        evidence_items = []
        for blob in blobs:
            # Extract filename from blob name
            filename = blob.name.split("/")[-1]
            # Remove timestamp prefix if present
            if "_" in filename:
                filename = "_".join(filename.split("_")[2:])
            
            evidence_items.append({
                "file_name": filename,
                "file_url": container.get_blob_client(blob.name).url,
                "uploaded_at": blob.last_modified.isoformat() if blob.last_modified else None,
                "size": blob.size
            })
        
        return {"items": evidence_items, "total": len(evidence_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

