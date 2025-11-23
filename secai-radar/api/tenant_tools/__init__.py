
import json
import azure.functions as func
from shared.utils import table_client, json_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")
    table = table_client("TenantTools")
    if req.method == "GET":
        items = [e for e in table.list_entities() if e.get("PartitionKey")==tenant_id]
        return func.HttpResponse(**json_response({"items": items, "total": len(items)}))
    else:
        try:
            body = req.get_json()
        except Exception:
            return func.HttpResponse(**json_response({"error":"Invalid JSON"}, status=400))
        # Body: { vendorToolId, Enabled, ConfigScore?, Owner?, Notes? }
        if not body.get("vendorToolId"):
            return func.HttpResponse(**json_response({"error":"vendorToolId required"}, status=400))
        entity = {
            "PartitionKey": tenant_id,
            "RowKey": body["vendorToolId"],
            "Enabled": bool(body.get("Enabled", True)),
            "ConfigScore": float(body.get("ConfigScore", 0.8)),
            "Owner": body.get("Owner",""),
            "Notes": body.get("Notes","")
        }
        table.upsert_entity(entity)
        return func.HttpResponse(**json_response({"ok": True, "item": entity}))
