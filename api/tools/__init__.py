"""
Tools Catalog Endpoint

Returns the catalog of vendor security tools available in the SecAI Framework.
"""

import json
import logging
import azure.functions as func
from pathlib import Path
from shared.utils import json_response

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Return catalog of vendor security tools."""
    try:
        seeds_path = Path(__file__).resolve().parents[1] / "seeds_vendor_tools.json"
        if not seeds_path.exists():
            logger.error("Vendor tools seed file not found: %s", seeds_path)
            return func.HttpResponse(**json_response(
                {"error": "Vendor tools catalog not found"},
                status=500
            ))
        
        data = json.loads(seeds_path.read_text())
        
        # Optional filtering by vendor or capability
        vendor_filter = req.params.get("vendor")
        capability_filter = req.params.get("capability")
        
        if vendor_filter:
            data = [t for t in data if t.get("vendor", "").lower() == vendor_filter.lower()]
        
        if capability_filter:
            data = [
                t for t in data
                if capability_filter in t.get("capabilities", [])
            ]
        
        return func.HttpResponse(**json_response({
            "items": data,
            "total": len(data)
        }))
    
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in vendor tools file: %s", e)
        return func.HttpResponse(**json_response(
            {"error": "Invalid vendor tools catalog"},
            status=500
        ))
    except Exception as e:
        logger.exception("Unexpected error in tools endpoint")
        return func.HttpResponse(**json_response(
            {"error": "Internal server error", "message": str(e)},
            status=500
        ))
