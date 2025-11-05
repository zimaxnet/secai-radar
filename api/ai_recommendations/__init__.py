"""
AI Recommendations Endpoint

Provides AI-powered recommendations for specific controls or gaps.
"""

import json
import azure.functions as func
from shared.utils import table_client, json_response

# Optional AI service import
try:
    from shared.ai_service import get_ai_service
    AI_AVAILABLE = True
except (ImportError, ValueError):
    AI_AVAILABLE = False

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate AI-powered recommendations for a control or gap
    
    Query parameters:
    - tenantId: Tenant ID (required)
    - controlId: Control ID (optional, for control-specific recommendations)
    - capabilityId: Capability ID (optional, for gap-specific explanations)
    - gapType: 'hard' or 'soft' (optional, with capabilityId)
    """
    tenant_id = req.route_params.get("tenantId") or req.params.get("tenantId")
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
            
            # Load gaps for this control (simplified - you might want to reuse gaps endpoint logic)
            # For now, return a basic recommendation
            recommendation = ai_service.generate_recommendation(
                control_id=control_id,
                control_title=control.get("ControlTitle", control_id),
                gaps=[],  # Would need to calculate gaps here
                tenant_tools=[],  # Would need to load tenant tools
                stream=False
            )
            
            return func.HttpResponse(**json_response({
                "controlId": control_id,
                "recommendation": recommendation
            }))
        
        # If capabilityId is provided, generate gap explanation
        elif capability_id:
            # This would need more context - for now, return a basic explanation
            explanation = ai_service.explain_gap(
                control_id=control_id or "unknown",
                capability_id=capability_id,
                gap_type=gap_type,
                current_coverage=0.0,
                min_required=0.7,
                available_tools=[]
            )
            
            return func.HttpResponse(**json_response({
                "capabilityId": capability_id,
                "gapType": gap_type,
                "explanation": explanation
            }))
        
        else:
            return func.HttpResponse(**json_response({
                "error": "Either controlId or capabilityId must be provided"
            }, status=400))
            
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "AI service error",
            "message": str(e)
        }, status=500))

