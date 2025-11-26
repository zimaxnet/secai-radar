"""
Summary Endpoint

Returns aggregated summary statistics for a tenant's security assessment.
"""

import logging
import azure.functions as func
from collections import defaultdict
from shared.utils import table_client, json_response

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get summary statistics for a tenant.
    
    Returns:
        - byDomain: Array of domain statistics with completion counts
        - totals: Overall totals across all domains
    """
    tenant_id = req.route_params.get("tenantId")
    
    if not tenant_id:
        return func.HttpResponse(**json_response(
            {"error": "tenantId is required"},
            status=400
        ))
    
    try:
        table = table_client("Controls")
        prefix = f"{tenant_id}|"
        items = [
            e for e in table.list_entities()
            if str(e.get("PartitionKey", "")).startswith(prefix)
        ]
        
        # Aggregate by domain
        agg = defaultdict(lambda: {
            "total": 0,
            "complete": 0,
            "inProgress": 0,
            "notStarted": 0,
            "notApplicable": 0
        })
        
        for e in items:
            partition_key = str(e.get("PartitionKey", ""))
            domain = partition_key.split("|", 1)[1] if "|" in partition_key else "UNKNOWN"
            agg[domain]["total"] += 1
            
            status = (e.get("Status") or "").lower()
            if status == "complete":
                agg[domain]["complete"] += 1
            elif status == "inprogress":
                agg[domain]["inProgress"] += 1
            elif status == "notstarted":
                agg[domain]["notStarted"] += 1
            elif status == "notapplicable":
                agg[domain]["notApplicable"] += 1
        
        by_domain = [{"domain": d, **v} for d, v in sorted(agg.items())]
        
        # Calculate totals
        totals = {
            "total": sum(d["total"] for d in by_domain),
            "complete": sum(d["complete"] for d in by_domain),
            "inProgress": sum(d["inProgress"] for d in by_domain),
            "notStarted": sum(d["notStarted"] for d in by_domain),
            "notApplicable": sum(d["notApplicable"] for d in by_domain),
            "domainsCount": len(by_domain)
        }
        
        # Calculate completion percentage
        if totals["total"] > 0:
            totals["completionPercent"] = round(
                (totals["complete"] / totals["total"]) * 100, 1
            )
        else:
            totals["completionPercent"] = 0
        
        return func.HttpResponse(**json_response({
            "tenantId": tenant_id,
            "byDomain": by_domain,
            "totals": totals
        }))
    
    except Exception as e:
        logger.exception("Error fetching summary for tenant %s", tenant_id)
        return func.HttpResponse(**json_response(
            {"error": "Failed to fetch summary", "message": str(e)},
            status=500
        ))
