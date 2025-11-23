
import json
import azure.functions as func
from pathlib import Path
from collections import defaultdict
from shared.utils import table_client, json_response

# Optional AI service import (will fail gracefully if not configured)
try:
    from shared.ai_service import get_ai_service
    AI_AVAILABLE = True
except (ImportError, ValueError):
    AI_AVAILABLE = False

def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")
    include_ai = req.params.get("ai", "false").lower() == "true"  # Optional ?ai=true parameter

    # Load seeds for tool capabilities and control requirements
    root = Path(__file__).resolve().parents[1]
    tool_caps = json.loads((root / "seeds_tool_capabilities.json").read_text())
    # index tool->cap strength
    toolcap = defaultdict(dict)
    for t in tool_caps:
        toolcap[t["vendorToolId"]][t["capabilityId"]] = float(t.get("strength",0))

    control_reqs = json.loads((root / "seeds_control_requirements.json").read_text())
    reqs_by_control = defaultdict(list)
    for r in control_reqs:
        reqs_by_control[r["controlId"]].append(r)

    # Load vendor tools catalog for AI recommendations
    vendor_tools = json.loads((root / "seeds_vendor_tools.json").read_text())
    vendor_tools_dict = {t["id"]: t for t in vendor_tools}

    # Load tenant tools inventory
    tt = table_client("TenantTools")
    tenant_tools_raw = [e for e in tt.list_entities() if e.get("PartitionKey")==tenant_id]
    tenant_tools = { e["RowKey"]: float(e.get("ConfigScore",1.0)) for e in tenant_tools_raw if e.get("Enabled", True) }
    tenant_tools_list = [
        {
            "id": e["RowKey"],
            "name": vendor_tools_dict.get(e["RowKey"], {}).get("name", e["RowKey"]),
            "configScore": float(e.get("ConfigScore", 1.0))
        }
        for e in tenant_tools_raw if e.get("Enabled", True)
    ]

    # Load controls
    controls = table_client("Controls")
    rows = [e for e in controls.list_entities() if str(e.get("PartitionKey","")).startswith(f"{tenant_id}|")]
    results = []
    for e in rows:
        control_id = e["RowKey"]
        reqs = reqs_by_control.get(control_id, [])
        if not reqs:
            continue
        # for each capability required, pick best active tool: strength * configScore
        coverage_score = 0.0
        sum_w = 0.0
        hard_gaps = []
        soft_gaps = []
        for r in reqs:
            cap = r["capabilityId"]
            w = float(r.get("weight",0))
            min_s = float(r.get("minStrength",0))
            sum_w += w
            best = 0.0
            best_tool = None
            for tool_id, cfg in tenant_tools.items():
                s = toolcap.get(tool_id, {}).get(cap, 0.0) * cfg
                if s > best:
                    best = s
                    best_tool = tool_id
            coverage_score += w * best
            if best == 0.0:
                hard_gaps.append({"capabilityId": cap, "weight": w})
            elif best < min_s:
                soft_gaps.append({"capabilityId": cap, "weight": w, "best": best, "min": min_s, "tool": best_tool})
        if sum_w > 0:
            normalized = coverage_score / sum_w
        else:
            normalized = 0
        
        result = {
            "ControlID": control_id,
            "DomainPartition": e["PartitionKey"],
            "Coverage": round(normalized, 3),
            "HardGaps": hard_gaps,
            "SoftGaps": soft_gaps
        }
        
        # Add AI-powered recommendation if requested and available
        if include_ai and AI_AVAILABLE and (hard_gaps or soft_gaps):
            try:
                ai_service = get_ai_service()
                all_gaps = hard_gaps + soft_gaps
                recommendation = ai_service.generate_recommendation(
                    control_id=control_id,
                    control_title=e.get("ControlTitle", control_id),
                    gaps=all_gaps,
                    tenant_tools=tenant_tools_list,
                    stream=False
                )
                result["AIRecommendation"] = recommendation
            except Exception as ex:
                # AI service failed - continue without AI recommendation
                result["AIRecommendation"] = None
                result["AIError"] = str(ex)
        
        results.append(result)

    return func.HttpResponse(**json_response({"items": results, "total": len(results), "aiEnabled": include_ai and AI_AVAILABLE}))
