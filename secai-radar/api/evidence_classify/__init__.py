"""
Evidence Classification Endpoint

Uses AI to classify evidence types and extract metadata.
"""

import azure.functions as func
from shared.utils import json_response

# Optional AI service import
try:
    from shared.ai_service import get_ai_service
    AI_AVAILABLE = True
except (ImportError, ValueError):
    AI_AVAILABLE = False

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Classify evidence type and extract metadata using AI
    
    Request body (JSON):
    {
        "description": "Evidence description or content preview",
        "fileName": "optional-file-name.pdf"
    }
    
    Query parameters:
    - tenantId: Tenant ID (required, from route)
    - controlId: Control ID (optional, for context)
    """
    tenant_id = req.route_params.get("tenantId")
    control_id = req.params.get("controlId")
    
    if not tenant_id:
        return func.HttpResponse(**json_response({"error": "tenantId is required"}, status=400))
    
    if not AI_AVAILABLE:
        return func.HttpResponse(**json_response({
            "error": "AI service not configured",
            "message": "Set AZURE_OPENAI_API_KEY and related environment variables"
        }, status=503))
    
    try:
        # Parse request body
        if req.method == "POST":
            try:
                body = req.get_json()
            except:
                body = {}
        else:
            # For GET, use query parameters
            body = {
                "description": req.params.get("description", ""),
                "fileName": req.params.get("fileName")
            }
        
        description = body.get("description", "")
        file_name = body.get("fileName")
        
        if not description:
            return func.HttpResponse(**json_response({
                "error": "description is required"
            }, status=400))
        
        # Get AI service and classify evidence
        ai_service = get_ai_service()
        classification = ai_service.classify_evidence(
            evidence_description=description,
            file_name=file_name
        )
        
        # Add context if controlId provided
        result = {
            "tenantId": tenant_id,
            "classification": classification,
            "metadata": {
                "fileName": file_name,
                "controlId": control_id
            }
        }
        
        return func.HttpResponse(**json_response(result))
        
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "AI service error",
            "message": str(e)
        }, status=500))

