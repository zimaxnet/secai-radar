
import azure.functions as func
from collections import defaultdict
from shared.utils import table_client, json_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")
    table = table_client("Controls")
    items = [e for e in table.list_entities() if str(e.get("PartitionKey","")).startswith(f"{tenant_id}|")]
    agg = defaultdict(lambda: {"total":0,"complete":0,"inProgress":0,"notStarted":0})
    for e in items:
        domain = str(e["PartitionKey"]).split("|",1)[1]
        agg[domain]["total"] += 1
        st = (e.get("Status") or "").lower()
        if st=="complete": agg[domain]["complete"] +=1
        elif st=="inprogress": agg[domain]["inProgress"] +=1
        elif st=="notstarted": agg[domain]["notStarted"] +=1
    result = [{"domain": d, **v} for d,v in agg.items()]
    return func.HttpResponse(**json_response({"byDomain": result}))
