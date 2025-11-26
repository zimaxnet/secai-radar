"""
Controls Endpoint

Returns controls for a tenant with optional filtering by domain, status, and search query.
"""

import logging
import azure.functions as func
from shared.utils import table_client, json_response

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get controls for a tenant.
    
    Query parameters:
        - domain: Filter by domain code (e.g., NET, ID)
        - status: Filter by status (NotStarted, InProgress, Complete)
        - q: Search query for title, description, question, notes
    """
    tenant_id = req.route_params.get("tenantId")
    
    if not tenant_id:
        return func.HttpResponse(**json_response(
            {"error": "tenantId is required"},
            status=400
        ))
    
    domain = req.params.get("domain")
    status = req.params.get("status")
    q = (req.params.get("q") or "").lower()
    
    try:
        table = table_client("Controls")
        entities = []
        
        # Use query for specific domain (more efficient)
        if domain:
            # Sanitize domain to prevent injection
            safe_domain = "".join(c for c in domain if c.isalnum())
            partition_key = f"{tenant_id}|{safe_domain}"
            entities = list(table.query_entities(f"PartitionKey eq '{partition_key}'"))
        else:
            # List all for tenant (filter client-side)
            prefix = f"{tenant_id}|"
            entities = [
                e for e in table.list_entities()
                if str(e.get("PartitionKey", "")).startswith(prefix)
            ]
        
        # Apply status filter
        if status:
            entities = [e for e in entities if str(e.get("Status", "")) == status]
        
        # Apply text search
        if q:
            def matches_query(e):
                for key in ("ControlTitle", "ControlDescription", "Question", "Notes"):
                    if q in str(e.get(key, "")).lower():
                        return True
                return False
            entities = [e for e in entities if matches_query(e)]
        
        return func.HttpResponse(**json_response({
            "items": entities,
            "total": len(entities),
            "filters": {
                "domain": domain,
                "status": status,
                "query": q if q else None
            }
        }))
    
    except Exception as e:
        logger.exception("Error fetching controls for tenant %s", tenant_id)
        return func.HttpResponse(**json_response(
            {"error": "Failed to fetch controls", "message": str(e)},
            status=500
        ))
