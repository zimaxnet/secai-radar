"""
Import Controls Endpoint

Imports controls from CSV or JSON into a tenant's assessment.
"""

import csv
import io
import logging
import azure.functions as func
from shared.utils import table_client, json_response

logger = logging.getLogger(__name__)

EXPECTED_HEADERS = [
    "ControlID", "Domain", "ControlTitle", "ControlDescription", "Question",
    "RequiredEvidence", "Status", "Owner", "Frequency", "ScoreNumeric",
    "Weight", "Notes", "SourceRef", "Tags", "UpdatedAt"
]


def parse_csv_bytes(data: bytes) -> list:
    """Parse CSV bytes into list of dicts."""
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Import controls from CSV or JSON.
    
    Accepts:
        - Content-Type: application/json with array of control objects
        - Content-Type: text/csv with CSV data
        - Raw body treated as CSV
    """
    tenant_id = req.route_params.get("tenantId")
    
    if not tenant_id:
        return func.HttpResponse(**json_response(
            {"error": "tenantId is required"},
            status=400
        ))
    
    try:
        table = table_client("Controls")
    except Exception as e:
        logger.exception("Failed to connect to Controls table")
        return func.HttpResponse(**json_response(
            {"error": "Database connection failed", "message": str(e)},
            status=500
        ))
    
    content_type = req.headers.get("content-type", "")
    rows = []
    
    # Parse input based on content type
    try:
        if "application/json" in content_type:
            payload = req.get_json()
            if not isinstance(payload, list):
                return func.HttpResponse(**json_response(
                    {"error": "JSON body must be an array of controls"},
                    status=400
                ))
            rows = payload
        else:
            # Fallback: parse as CSV from raw body
            body = req.get_body()
            if not body:
                return func.HttpResponse(**json_response(
                    {"error": "Request body is empty"},
                    status=400
                ))
            rows = parse_csv_bytes(body)
    except ValueError as e:
        return func.HttpResponse(**json_response(
            {"error": "Invalid JSON body", "message": str(e)},
            status=400
        ))
    except UnicodeDecodeError as e:
        return func.HttpResponse(**json_response(
            {"error": "Invalid CSV encoding. Use UTF-8.", "message": str(e)},
            status=400
        ))
    except Exception as e:
        return func.HttpResponse(**json_response(
            {"error": "Invalid body. Send JSON array or CSV.", "message": str(e)},
            status=400
        ))

    # Validate and upsert controls
    inserted = 0
    skipped = 0
    errors = []
    
    for idx, row in enumerate(rows):
        try:
            # Get control ID
            control_id = row.get("ControlID", "").strip()
            if not control_id:
                skipped += 1
                continue
            
            # Derive domain code from ControlID (e.g., SEC-NET-0001 -> NET)
            domain_code = ""
            if control_id.startswith("SEC-") and "-" in control_id[4:]:
                domain_code = control_id.split("-")[1]
            else:
                domain_code = row.get("DomainCode", "").strip()
            
            # Require domain
            domain = row.get("Domain", "").strip()
            if not domain:
                errors.append(f"Row {idx + 1}: Missing Domain for {control_id}")
                skipped += 1
                continue
            
            # Parse numeric fields safely
            def safe_float(val, default=0.0):
                if val is None or str(val).strip() == "":
                    return default
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return default
            
            entity = {
                "PartitionKey": f"{tenant_id}|{domain_code}",
                "RowKey": control_id,
                "Domain": domain,
                "ControlTitle": row.get("ControlTitle", ""),
                "ControlDescription": row.get("ControlDescription", ""),
                "Question": row.get("Question", ""),
                "RequiredEvidence": row.get("RequiredEvidence", ""),
                "Status": row.get("Status", "NotStarted"),
                "Owner": row.get("Owner", ""),
                "Frequency": row.get("Frequency", ""),
                "ScoreNumeric": safe_float(row.get("ScoreNumeric")),
                "Weight": safe_float(row.get("Weight")),
                "Notes": row.get("Notes", ""),
                "SourceRef": row.get("SourceRef", ""),
                "Tags": row.get("Tags", ""),
                "UpdatedAt": row.get("UpdatedAt", "")
            }
            
            table.upsert_entity(entity)
            inserted += 1
            
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")
            skipped += 1
    
    return func.HttpResponse(**json_response({
        "success": True,
        "inserted": inserted,
        "skipped": skipped,
        "totalRows": len(rows),
        "errors": errors[:10] if errors else None  # Limit error messages
    }))
