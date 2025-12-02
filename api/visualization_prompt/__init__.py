"""
Visualization Prompt Endpoint

Uses Elena Bridges (Business Impact Strategist) agent to craft
contextually-aware visualization prompts for executive-ready graphics.
"""

import json
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
    Craft a visualization prompt using the Elena Bridges agent.
    
    Request body (POST):
    {
        "intent": "What the user wants to visualize",
        "style": "diagram|infographic|chart|architecture" (optional, default: diagram),
        "contextType": "assessment|gaps|tools|custom" (optional, default: assessment),
        "assessmentData": {...} (optional, provides context for better prompts)
    }
    
    Returns:
    {
        "crafted_prompt": "The AI-crafted prompt ready for image generation",
        "agent": "elena_bridges",
        "agent_role": "Business Impact Strategist",
        "style": "requested style",
        "context_type": "context type used",
        "original_intent": "user's original request"
    }
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    if req.method != "POST":
        return func.HttpResponse(**json_response(
            {"error": "Method not allowed. Use POST."},
            status=405
        ))
    
    if not AI_AVAILABLE:
        return func.HttpResponse(**json_response({
            "error": "AI service not configured",
            "message": "Set AZURE_OPENAI_API_KEY and related environment variables"
        }, status=503))
    
    try:
        # Parse request body
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(**json_response(
                {"error": "Invalid JSON in request body"},
                status=400
            ))
        
        intent = body.get("intent")
        if not intent:
            return func.HttpResponse(**json_response(
                {"error": "Missing required field: intent"},
                status=400
            ))
        
        style = body.get("style", "diagram")
        context_type = body.get("contextType", "assessment")
        assessment_data = body.get("assessmentData")
        
        # Validate style
        valid_styles = ["diagram", "infographic", "chart", "architecture"]
        if style not in valid_styles:
            style = "diagram"
        
        # Get AI service and craft prompt
        ai_service = get_ai_service()
        result = ai_service.craft_visualization_prompt(
            user_intent=intent,
            context_type=context_type,
            assessment_data=assessment_data,
            style=style
        )
        
        return func.HttpResponse(**json_response(result))
        
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Failed to craft visualization prompt",
            "message": str(e)
        }, status=500))

