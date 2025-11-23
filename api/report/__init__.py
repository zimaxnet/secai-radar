"""
Report Generation Endpoint

Generates AI-powered executive summaries and assessment reports.
"""

import json
import azure.functions as func
from pathlib import Path
from collections import defaultdict
from shared.utils import table_client, json_response

# Optional AI service import
try:
    from shared.ai_service import get_ai_service
    AI_AVAILABLE = True
except (ImportError, ValueError):
    AI_AVAILABLE = False

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate assessment report with optional AI-powered executive summary
    
    Query parameters:
    - tenantId: Tenant ID (required, from route)
    - includeAI: 'true' to include AI-generated executive summary (default: false)
    - format: 'json' or 'summary' (default: 'json')
    """
    tenant_id = req.route_params.get("tenantId")
    include_ai = req.params.get("includeAI", "false").lower() == "true"
    format_type = req.params.get("format", "json").lower()
    
    if not tenant_id:
        return func.HttpResponse(**json_response({"error": "tenantId is required"}, status=400))
    
    # Load summary data (by domain)
    table = table_client("Controls")
    items = [e for e in table.list_entities() if str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|")]
    agg = defaultdict(lambda: {"total": 0, "complete": 0, "inProgress": 0, "notStarted": 0})
    for e in items:
        domain = str(e["PartitionKey"]).split("|", 1)[1]
        agg[domain]["total"] += 1
        st = (e.get("Status") or "").lower()
        if st == "complete":
            agg[domain]["complete"] += 1
        elif st == "inprogress":
            agg[domain]["inProgress"] += 1
        elif st == "notstarted":
            agg[domain]["notStarted"] += 1
    
    summary_by_domain = [{"domain": d, **v} for d, v in agg.items()]
    
    # Load gaps data
    root = Path(__file__).resolve().parents[1]
    tool_caps = json.loads((root / "seeds_tool_capabilities.json").read_text())
    toolcap = defaultdict(dict)
    for t in tool_caps:
        toolcap[t["vendorToolId"]][t["capabilityId"]] = float(t.get("strength", 0))
    
    control_reqs = json.loads((root / "seeds_control_requirements.json").read_text())
    reqs_by_control = defaultdict(list)
    for r in control_reqs:
        reqs_by_control[r["controlId"]].append(r)
    
    # Load tenant tools inventory
    tt = table_client("TenantTools")
    tenant_tools_raw = [e for e in tt.list_entities() if e.get("PartitionKey") == tenant_id]
    tenant_tools = {e["RowKey"]: float(e.get("ConfigScore", 1.0)) 
                    for e in tenant_tools_raw if e.get("Enabled", True)}
    
    # Calculate gaps for all controls
    gaps_summary = []
    for e in items:
        control_id = e["RowKey"]
        reqs = reqs_by_control.get(control_id, [])
        if not reqs:
            continue
        
        coverage_score = 0.0
        sum_w = 0.0
        hard_gaps = []
        soft_gaps = []
        
        for r in reqs:
            cap = r["capabilityId"]
            w = float(r.get("weight", 0))
            min_s = float(r.get("minStrength", 0))
            sum_w += w
            best = 0.0
            for tool_id, cfg in tenant_tools.items():
                s = toolcap.get(tool_id, {}).get(cap, 0.0) * cfg
                if s > best:
                    best = s
            coverage_score += w * best
            if best == 0.0:
                hard_gaps.append({"capabilityId": cap, "weight": w})
            elif best < min_s:
                soft_gaps.append({"capabilityId": cap, "weight": w, "best": best, "min": min_s})
        
        normalized = (coverage_score / sum_w) if sum_w > 0 else 0.0
        
        if hard_gaps or soft_gaps:
            gaps_summary.append({
                "ControlID": control_id,
                "ControlTitle": e.get("ControlTitle", control_id),
                "Domain": str(e["PartitionKey"]).split("|", 1)[1],
                "Coverage": round(normalized, 3),
                "HardGaps": hard_gaps,
                "SoftGaps": soft_gaps
            })
    
    # Prepare report structure
    report = {
        "tenantId": tenant_id,
        "summary": {
            "byDomain": summary_by_domain,
            "totalControls": len(items),
            "totalGaps": len(gaps_summary),
            "criticalGaps": len([g for g in gaps_summary if g["HardGaps"]])
        },
        "gaps": gaps_summary,
        "generatedAt": None  # Would use datetime, but keeping simple
    }
    
    # Add AI-generated executive summary if requested
    if include_ai:
        if not AI_AVAILABLE:
            report["aiError"] = "AI service not configured"
            report["aiEnabled"] = False
        else:
            try:
                ai_service = get_ai_service()
                executive_summary = ai_service.generate_report_summary(
                    tenant_id=tenant_id,
                    summary_data=report["summary"],
                    gaps_summary=gaps_summary
                )
                report["executiveSummary"] = executive_summary
                report["aiEnabled"] = True
            except Exception as e:
                report["aiError"] = str(e)
                report["aiEnabled"] = False
    
    # Return format based on request
    if format_type == "summary" and include_ai and "executiveSummary" in report:
        # Return just the AI summary as plain text
        return func.HttpResponse(
            report.get("executiveSummary", "AI summary not available"),
            mimetype="text/plain",
            status_code=200
        )
    else:
        # Return full JSON report
        return func.HttpResponse(**json_response(report))

