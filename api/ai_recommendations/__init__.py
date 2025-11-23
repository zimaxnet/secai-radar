"""
AI Recommendations Endpoint

Provides AI-powered recommendations for specific controls or gaps.
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

def _calculate_gaps_for_control(tenant_id: str, control_id: str, control_entity: dict):
    """
    Calculate gaps for a specific control (reusing logic from gaps endpoint)
    Returns: (hard_gaps, soft_gaps, coverage_score, tenant_tools_list)
    """
    # Load seeds for tool capabilities and control requirements
    root = Path(__file__).resolve().parents[1]
    tool_caps = json.loads((root / "seeds_tool_capabilities.json").read_text())
    toolcap = defaultdict(dict)
    for t in tool_caps:
        toolcap[t["vendorToolId"]][t["capabilityId"]] = float(t.get("strength", 0))

    control_reqs = json.loads((root / "seeds_control_requirements.json").read_text())
    reqs_by_control = defaultdict(list)
    for r in control_reqs:
        reqs_by_control[r["controlId"]].append(r)

    # Load vendor tools catalog
    vendor_tools = json.loads((root / "seeds_vendor_tools.json").read_text())
    vendor_tools_dict = {t["id"]: t for t in vendor_tools}

    # Load tenant tools inventory
    tt = table_client("TenantTools")
    tenant_tools_raw = [e for e in tt.list_entities() if e.get("PartitionKey") == tenant_id]
    tenant_tools = {e["RowKey"]: float(e.get("ConfigScore", 1.0)) 
                    for e in tenant_tools_raw if e.get("Enabled", True)}
    tenant_tools_list = [
        {
            "id": e["RowKey"],
            "name": vendor_tools_dict.get(e["RowKey"], {}).get("name", e["RowKey"]),
            "configScore": float(e.get("ConfigScore", 1.0))
        }
        for e in tenant_tools_raw if e.get("Enabled", True)
    ]

    # Calculate gaps for this control
    reqs = reqs_by_control.get(control_id, [])
    if not reqs:
        return [], [], 0.0, tenant_tools_list

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

    normalized = (coverage_score / sum_w) if sum_w > 0 else 0.0
    return hard_gaps, soft_gaps, normalized, tenant_tools_list

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate AI-powered recommendations for a control or gap
    
    Query parameters:
    - tenantId: Tenant ID (required, from route)
    - controlId: Control ID (required for control recommendations)
    - capabilityId: Capability ID (optional, for gap-specific explanations)
    - gapType: 'hard' or 'soft' (optional, with capabilityId)
    - controlId: Control ID (optional, required with capabilityId for gap explanation)
    """
    tenant_id = req.route_params.get("tenantId")
    control_id = req.params.get("controlId")
    capability_id = req.params.get("capabilityId")
    gap_type = req.params.get("gapType", "hard")
    
    if not tenant_id:
        return func.HttpResponse(**json_response({"error": "tenantId is required"}, status=400))
    
    if not AI_AVAILABLE:
        return func.HttpResponse(**json_response({
            "error": "AI service not configured",
            "message": "Set AZURE_OPENAI_API_KEY and related environment variables"
        }, status=503))
    
    try:
        ai_service = get_ai_service()
        
        # If controlId is provided, get control details and generate recommendation
        if control_id:
            # Load control details
            controls = table_client("Controls")
            control = None
            for e in controls.list_entities():
                if e.get("RowKey") == control_id and str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|"):
                    control = e
                    break
            
            if not control:
                return func.HttpResponse(**json_response({"error": "Control not found"}, status=404))
            
            # Calculate gaps for this control
            hard_gaps, soft_gaps, coverage_score, tenant_tools_list = _calculate_gaps_for_control(
                tenant_id, control_id, control
            )
            
            # If capabilityId is also provided, generate gap explanation
            if capability_id:
                # Find the specific gap
                gap_info = None
                current_coverage = 0.0
                min_required = 0.7
                
                # Check hard gaps first
                for gap in hard_gaps:
                    if gap.get("capabilityId") == capability_id:
                        gap_info = gap
                        gap_type = "hard"
                        break
                
                # Check soft gaps
                if not gap_info:
                    for gap in soft_gaps:
                        if gap.get("capabilityId") == capability_id:
                            gap_info = gap
                            gap_type = "soft"
                            current_coverage = gap.get("best", 0.0)
                            min_required = gap.get("min", 0.7)
                            break
                
                if not gap_info:
                    return func.HttpResponse(**json_response({
                        "error": "Capability gap not found for this control"
                    }, status=404))
                
                # Get available tools for this capability
                root = Path(__file__).resolve().parents[1]
                tool_caps = json.loads((root / "seeds_tool_capabilities.json").read_text())
                available_tools = [
                    t["vendorToolId"] for t in tool_caps 
                    if t["capabilityId"] == capability_id
                ]
                
                explanation = ai_service.explain_gap(
                    control_id=control_id,
                    capability_id=capability_id,
                    gap_type=gap_type,
                    current_coverage=current_coverage,
                    min_required=min_required,
                    available_tools=available_tools
                )
                
                return func.HttpResponse(**json_response({
                    "controlId": control_id,
                    "capabilityId": capability_id,
                    "gapType": gap_type,
                    "explanation": explanation,
                    "coverage": coverage_score
                }))
            
            # Generate full recommendation for the control
            all_gaps = hard_gaps + soft_gaps
            recommendation = ai_service.generate_recommendation(
                control_id=control_id,
                control_title=control.get("ControlTitle", control_id),
                gaps=all_gaps,
                tenant_tools=tenant_tools_list,
                stream=False
            )
            
            return func.HttpResponse(**json_response({
                "controlId": control_id,
                "controlTitle": control.get("ControlTitle", control_id),
                "coverage": coverage_score,
                "hardGaps": hard_gaps,
                "softGaps": soft_gaps,
                "recommendation": recommendation
            }))
        
        else:
            return func.HttpResponse(**json_response({
                "error": "controlId is required"
            }, status=400))
            
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "AI service error",
            "message": str(e)
        }, status=500))

