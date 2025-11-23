
import io, csv, json
import azure.functions as func
from shared.utils import table_client, json_response

HEADERS = ["ControlID","Domain","ControlTitle","ControlDescription","Question","RequiredEvidence",
  "Status","Owner","Frequency","ScoreNumeric","Weight","Notes","SourceRef","Tags","UpdatedAt"]

def parse_csv_bytes(b: bytes):
    text = b.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]

def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")
    table = table_client("Controls")
    content_type = req.headers.get("content-type","")
    rows = []
    # Accept JSON array
    try:
        if "application/json" in content_type:
            payload = req.get_json()
            assert isinstance(payload, list)
            rows = payload
        else:
            # fallback: parse as CSV from raw body
            rows = parse_csv_bytes(req.get_body())
    except Exception:
        return func.HttpResponse(**json_response({"error":"Invalid body. Send JSON array or CSV."}, status=400))

    # Basic validation + upsert
    inserted = 0
    for r in rows:
        # derive domain code from ControlID if present; else from Domain
        control_id = r.get("ControlID") or ""
        domain_code = ""
        if control_id.startswith("SEC-") and "-" in control_id[4:]:
            domain_code = control_id.split("-")[1]
        else:
            # try first word of Domain name mapping (e.g., "Network security" -> "NET" expected in client)
            # if not provided, reject row
            domain_code = r.get("DomainCode","")
        if not control_id or not r.get("Domain"):
            # minimal guard
            continue
        entity = {
            "PartitionKey": f"{tenant_id}|{domain_code}",
            "RowKey": control_id,
            "Domain": r.get("Domain"),
            "ControlTitle": r.get("ControlTitle",""),
            "ControlDescription": r.get("ControlDescription",""),
            "Question": r.get("Question",""),
            "RequiredEvidence": r.get("RequiredEvidence",""),
            "Status": r.get("Status","NotStarted"),
            "Owner": r.get("Owner",""),
            "Frequency": r.get("Frequency",""),
            "ScoreNumeric": float(r.get("ScoreNumeric") or 0) if str(r.get("ScoreNumeric") or "").strip()!="" else 0,
            "Weight": float(r.get("Weight") or 0) if str(r.get("Weight") or "").strip()!="" else 0,
            "Notes": r.get("Notes",""),
            "SourceRef": r.get("SourceRef",""),
            "Tags": r.get("Tags",""),
            "UpdatedAt": r.get("UpdatedAt","")
        }
        table.upsert_entity(entity)
        inserted += 1

    return func.HttpResponse(**json_response({"ok": True, "inserted": inserted}))
