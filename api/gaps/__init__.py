
import json
import azure.functions as func
from pathlib import Path
from collections import defaultdict
from shared.utils import table_client, json_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")

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

    # Load tenant tools inventory
    tt = table_client("TenantTools")
    tenant_tools = { e["RowKey"]: float(e.get("ConfigScore",1.0)) for e in tt.list_entities() if e.get("PartitionKey")==tenant_id and e.get("Enabled", True) }

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
        results.append({
            "ControlID": control_id,
            "DomainPartition": e["PartitionKey"],
            "Coverage": round(normalized, 3),
            "HardGaps": hard_gaps,
            "SoftGaps": soft_gaps
        })

    return func.HttpResponse(**json_response({"items": results, "total": len(results)}))
