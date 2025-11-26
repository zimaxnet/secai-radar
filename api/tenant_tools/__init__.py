"""
Tenant Tools Endpoint

Manages the security tool inventory for a tenant.
"""

import logging
import azure.functions as func
from shared.utils import table_client, json_response

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get or update tenant tool inventory.
    
    GET: Returns list of tools configured for the tenant
    POST: Upserts a tool configuration
    
    POST body:
        - vendorToolId: Required - Tool identifier from catalog
        - Enabled: Optional - Whether tool is enabled (default: true)
        - ConfigScore: Optional - Configuration quality score 0.0-1.0 (default: 0.8)
        - Owner: Optional - Tool owner
        - Notes: Optional - Notes about the tool
    """
    tenant_id = req.route_params.get("tenantId")
    
    if not tenant_id:
        return func.HttpResponse(**json_response(
            {"error": "tenantId is required"},
            status=400
        ))
    
    try:
        table = table_client("TenantTools")
        
        if req.method == "GET":
            items = [e for e in table.list_entities() if e.get("PartitionKey") == tenant_id]
            return func.HttpResponse(**json_response({
                "tenantId": tenant_id,
                "items": items,
                "total": len(items)
            }))
        
        elif req.method == "POST":
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(**json_response(
                    {"error": "Invalid JSON body"},
                    status=400
                ))
            
            if not body.get("vendorToolId"):
                return func.HttpResponse(**json_response(
                    {"error": "vendorToolId is required"},
                    status=400
                ))
            
            # Validate ConfigScore if provided
            config_score = body.get("ConfigScore", 0.8)
            try:
                config_score = float(config_score)
                if not 0.0 <= config_score <= 1.0:
                    return func.HttpResponse(**json_response(
                        {"error": "ConfigScore must be between 0.0 and 1.0"},
                        status=400
                    ))
            except (TypeError, ValueError):
                return func.HttpResponse(**json_response(
                    {"error": "ConfigScore must be a number"},
                    status=400
                ))
            
            entity = {
                "PartitionKey": tenant_id,
                "RowKey": body["vendorToolId"],
                "Enabled": bool(body.get("Enabled", True)),
                "ConfigScore": config_score,
                "Owner": body.get("Owner", ""),
                "Notes": body.get("Notes", "")
            }
            
            table.upsert_entity(entity)
            
            return func.HttpResponse(**json_response({
                "success": True,
                "item": entity
            }))
        
        else:
            return func.HttpResponse(**json_response(
                {"error": "Method not allowed"},
                status=405
            ))
    
    except Exception as e:
        logger.exception("Error in tenant_tools for tenant %s", tenant_id)
        return func.HttpResponse(**json_response(
            {"error": "Internal server error", "message": str(e)},
            status=500
        ))
