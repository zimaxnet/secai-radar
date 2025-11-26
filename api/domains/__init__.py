"""
Domains Endpoint

Returns the list of security domains in the SecAI Framework.
"""

import json
import logging
import azure.functions as func
from pathlib import Path
from shared.utils import json_response

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Return list of security domains."""
    try:
        seeds_path = Path(__file__).resolve().parents[1] / "seeds_domain_codes.json"
        if not seeds_path.exists():
            logger.error("Domain codes seed file not found: %s", seeds_path)
            return func.HttpResponse(**json_response(
                {"error": "Domain codes configuration not found"},
                status=500
            ))
        
        data = json.loads(seeds_path.read_text())
        items = [{"code": k, "name": v} for k, v in data.items()]
        return func.HttpResponse(**json_response(items))
    
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in domain codes file: %s", e)
        return func.HttpResponse(**json_response(
            {"error": "Invalid domain codes configuration"},
            status=500
        ))
    except Exception as e:
        logger.exception("Unexpected error in domains endpoint")
        return func.HttpResponse(**json_response(
            {"error": "Internal server error", "message": str(e)},
            status=500
        ))
