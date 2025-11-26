"""
Evidence Upload and Management Endpoint

Handles evidence file uploads to Blob Storage with auto-classification.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import azure.functions as func
from azure.storage.blob import generate_container_sas, ContainerSasPermissions, BlobSasPermissions, generate_blob_sas
from shared.utils import table_client, json_response, blob_container

# Optional AI service import for auto-classification
try:
    from shared.ai_service import get_ai_service
    AI_AVAILABLE = True
except (ImportError, ValueError):
    AI_AVAILABLE = False

# Allowed file types and max size
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.csv', '.txt', '.json', '.xml', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def _get_evidence_blob_path(tenant_id: str, control_id: str, filename: str) -> str:
    """Generate blob path for evidence: assessments/{tenantId}/evidence/{controlId}/{filename}"""
    # Sanitize filename
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")[:255]
    return f"assessments/{tenant_id}/evidence/{control_id}/{safe_filename}"

def _generate_sas_url(blob_name: str, permission: str = "read", expiry_hours: int = 24) -> str:
    """Generate SAS URL for blob access"""
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.core.credentials import AzureNamedKeyCredential
        
        account_key = os.getenv("BLOBS_CONN")
        if not account_key:
            return None
        
        # Parse connection string
        blob_service = BlobServiceClient.from_connection_string(account_key)
        container = blob_container()
        
        # Get account key from connection string
        # Connection string format: "AccountName=...;AccountKey=...;EndpointSuffix=..."
        conn_parts = dict(part.split('=', 1) for part in account_key.split(';') if '=' in part)
        account_name = conn_parts.get('AccountName')
        account_key_value = conn_parts.get('AccountKey')
        
        if not account_name or not account_key_value:
            return None
        
        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container.container_name,
            blob_name=blob_name,
            account_key=account_key_value,
            permission=BlobSasPermissions(read=True) if permission == "read" else BlobSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        # Build URL
        endpoint_suffix = conn_parts.get('EndpointSuffix', 'core.windows.net')
        blob_url = f"https://{account_name}.blob.{endpoint_suffix}/{container.container_name}/{blob_name}?{sas_token}"
        return blob_url
    except Exception as e:
        # Fallback: return blob path without SAS if generation fails
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle evidence upload, list, and download
    
    Routes:
    - POST /api/tenant/{tenantId}/evidence/{controlId} - Upload evidence
    - GET /api/tenant/{tenantId}/evidence/{controlId} - List evidence for control
    - GET /api/tenant/{tenantId}/evidence/{controlId}?filename=... - Get download URL for specific file
    """
    tenant_id = req.route_params.get("tenantId")
    control_id = req.route_params.get("controlId")
    filename = req.params.get("filename")  # Optional query parameter for download
    
    if not tenant_id or not control_id:
        return func.HttpResponse(**json_response({"error": "tenantId and controlId are required"}, status=400))
    
    try:
        container = blob_container()
        
        # GET: List evidence for a control
        if req.method == "GET" and not filename:
            evidence_list = []
            prefix = _get_evidence_blob_path(tenant_id, control_id, "")
            
            # List blobs with this prefix
            blobs = container.list_blobs(name_starts_with=prefix)
            
            # Also check Evidence table for metadata
            try:
                evidence_table = table_client("Evidence")
                evidence_entities = [
                    e for e in evidence_table.list_entities()
                    if e.get("PartitionKey") == tenant_id and e.get("ControlID") == control_id
                ]
                metadata_by_filename = {e.get("FileName"): e for e in evidence_entities}
            except Exception as e:
                logging.warning("Could not load evidence metadata: %s", e)
                metadata_by_filename = {}
            
            for blob in blobs:
                blob_name = blob.name
                file_name = blob_name.split("/")[-1]
                
                metadata = metadata_by_filename.get(file_name, {})
                
                # Generate download URL (SAS)
                download_url = _generate_sas_url(blob_name, permission="read", expiry_hours=24)
                
                evidence_list.append({
                    "fileName": file_name,
                    "size": blob.size,
                    "uploadedAt": blob.last_modified.isoformat() if blob.last_modified else None,
                    "downloadUrl": download_url,
                    "blobPath": blob_name,
                    "classification": {
                        "category": metadata.get("Category", "unknown"),
                        "sensitivity_level": metadata.get("SensitivityLevel", "internal"),
                        "content_type": metadata.get("ContentType", ""),
                        "confidence": float(metadata.get("Confidence", 0.0))
                    } if metadata else None
                })
            
            return func.HttpResponse(**json_response({"items": evidence_list, "total": len(evidence_list)}))
        
        # GET: Get download URL for specific file
        if req.method == "GET" and filename:
            blob_path = _get_evidence_blob_path(tenant_id, control_id, filename)
            blob_client = container.get_blob_client(blob_path)
            
            if not blob_client.exists():
                return func.HttpResponse(**json_response({"error": "File not found"}, status=404))
            
            download_url = _generate_sas_url(blob_path, permission="read", expiry_hours=24)
            return func.HttpResponse(**json_response({"downloadUrl": download_url, "fileName": filename}))
        
        # POST: Upload evidence
        if req.method == "POST":
            # Azure Functions HTTP trigger - expect JSON body with base64 file or multipart
            try:
                body = req.get_json()
            except ValueError:
                body = {}
            
            # Check for base64 encoded file
            if "file" in body and "fileName" in body:
                import base64
                try:
                    # Decode base64 file content
                    file_content = base64.b64decode(body["file"])
                    original_filename = body["fileName"]
                except Exception as e:
                    return func.HttpResponse(**json_response({
                        "error": f"Invalid file data: {str(e)}"
                    }, status=400))
            else:
                # Try multipart form data (if supported)
                # For Azure Functions, we'll primarily use base64
                return func.HttpResponse(**json_response({
                    "error": "File upload requires JSON body with 'file' (base64) and 'fileName' fields"
                }, status=400))
            
            # Validate file
            file_ext = Path(original_filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                return func.HttpResponse(**json_response({
                    "error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                }, status=400))
            
            if len(file_content) > MAX_FILE_SIZE:
                return func.HttpResponse(**json_response({
                    "error": f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
                }, status=400))
            
            # Generate unique filename if needed
            safe_filename = "".join(c for c in original_filename if c.isalnum() or c in ".-_")[:255]
            if not safe_filename:
                safe_filename = f"evidence_{uuid.uuid4().hex[:8]}{file_ext}"
            
            # Upload to blob storage
            blob_path = _get_evidence_blob_path(tenant_id, control_id, safe_filename)
            blob_client = container.get_blob_client(blob_path)
            blob_client.upload_blob(file_content, overwrite=True)
            
            # Auto-classify using AI if available
            classification = None
            description = body.get("description", "") or f"Evidence file: {safe_filename}"
            if AI_AVAILABLE:
                try:
                    ai_service = get_ai_service()
                    classification = ai_service.classify_evidence(
                        evidence_description=description,
                        file_name=safe_filename
                    )
                except Exception as e:
                    # Classification failed, continue without it
                    logging.warning("Evidence classification failed: %s", e)
            
            # Store metadata in Evidence table
            try:
                evidence_table = table_client("Evidence")
                evidence_entity = {
                    "PartitionKey": tenant_id,
                    "RowKey": f"{control_id}|{safe_filename}",
                    "ControlID": control_id,
                    "FileName": safe_filename,
                    "BlobPath": blob_path,
                    "Size": len(file_content),
                    "UploadedAt": datetime.utcnow().isoformat(),
                    "UploadedBy": req.headers.get("x-ms-client-principal-name", "unknown"),
                    "Category": classification.get("category", "other") if classification else "other",
                    "SensitivityLevel": classification.get("sensitivity_level", "internal") if classification else "internal",
                    "ContentType": classification.get("content_type", "") if classification else "",
                    "Confidence": classification.get("confidence", 0.0) if classification else 0.0,
                    "Description": description
                }
                evidence_table.upsert_entity(evidence_entity)
            except Exception as e:
                # Table storage failed, but blob upload succeeded
                logging.warning("Failed to store evidence metadata: %s", e)
            
            # Generate download URL
            download_url = _generate_sas_url(blob_path, permission="read", expiry_hours=24)
            
            return func.HttpResponse(**json_response({
                "success": True,
                "fileName": safe_filename,
                "blobPath": blob_path,
                "size": len(file_content),
                "downloadUrl": download_url,
                "classification": classification
            }))
        
        return func.HttpResponse(**json_response({"error": "Method not allowed"}, status=405))
        
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Server error",
            "message": str(e)
        }, status=500))

