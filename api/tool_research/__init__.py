"""
Tool Research Endpoint

Allows consultants to input a list of security vendor tools and have the system
automatically research and map them to the 340 controls across 12 security domains.
"""

import json
import azure.functions as func
from pathlib import Path
from shared.utils import table_client, json_response

try:
    from shared.tool_research import ToolResearchService
    RESEARCH_AVAILABLE = True
except ImportError:
    RESEARCH_AVAILABLE = False

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Research vendor tools and map them to controls
    
    POST /api/tool-research
    Body: {
        "tools": [
            {"name": "Palo Alto Firewall", "vendor": "Palo Alto Networks"},
            {"name": "CrowdStrike Falcon", "vendor": "CrowdStrike"}
        ],
        "tenantId": "NICO"  # Optional, for saving results
    }
    
    GET /api/tool-research?toolName=...&vendor=...
    """
    if not RESEARCH_AVAILABLE:
        return func.HttpResponse(**json_response({
            "error": "Tool research service not available",
            "message": "Dependencies not installed"
        }, status=503))
    
    try:
        research_service = ToolResearchService()
        
        if req.method == "POST":
            # Research multiple tools and map to controls
            body = req.get_json() or {}
            tools = body.get("tools", [])
            tenant_id = body.get("tenantId")
            
            if not tools:
                return func.HttpResponse(**json_response({
                    "error": "tools array is required"
                }, status=400))
            
            # Load all controls (340 controls across 12 domains)
            root = Path(__file__).resolve().parents[1]
            control_reqs_path = root / "seeds_control_requirements.json"
            if not control_reqs_path.exists():
                return func.HttpResponse(**json_response({
                    "error": "Control requirements seed file not found",
                    "path": str(control_reqs_path)
                }, status=500))
            control_reqs = json.loads(control_reqs_path.read_text())
            
            # Group requirements by control
            from collections import defaultdict
            reqs_by_control = defaultdict(list)
            for r in control_reqs:
                reqs_by_control[r["controlId"]].append(r)
            
            # Build control list with requirements
            controls = [
                {"controlId": cid, "requirements": reqs}
                for cid, reqs in reqs_by_control.items()
            ]
            
            # Map tools to controls
            mapping_result = research_service.map_tools_to_controls(tools, controls)
            
            # Optionally save to tenant tools if tenantId provided
            if tenant_id:
                # Save discovered tools to TenantTools table
                # This would require additional logic to merge with existing tools
                pass
            
            return func.HttpResponse(**json_response(mapping_result))
        
        elif req.method == "GET":
            # Research a single tool
            tool_name = req.params.get("toolName")
            vendor = req.params.get("vendor")
            
            if not tool_name:
                return func.HttpResponse(**json_response({
                    "error": "toolName parameter is required"
                }, status=400))
            
            # Research tool capabilities
            research_result = research_service.search_tool_info(tool_name, vendor)
            
            return func.HttpResponse(**json_response(research_result))
        
        else:
            return func.HttpResponse(**json_response({
                "error": "Method not allowed"
            }, status=405))
            
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Research failed",
            "message": str(e)
        }, status=500))

