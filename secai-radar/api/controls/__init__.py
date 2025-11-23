
import azure.functions as func
from shared.utils import table_client, json_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")
    domain = req.params.get("domain")
    status = req.params.get("status")
    q = (req.params.get("q") or "").lower()
    table = table_client("Controls")
    entities = []
    if domain:
        entities = [e for e in table.query_entities(f"PartitionKey eq '{tenant_id}|{domain}'")]
    else:
        entities = [e for e in table.list_entities() if str(e.get("PartitionKey","")).startswith(f"{tenant_id}|")]
    if status:
        entities = [e for e in entities if str(e.get('Status','')) == status]
    if q:
        def has_q(e):
            for k in ("ControlTitle","ControlDescription","Question","Notes"):
                if q in str(e.get(k,"")).lower(): return True
            return False
        entities = [e for e in entities if has_q(e)]
    return func.HttpResponse(**json_response({"items": entities, "total": len(entities)}))
