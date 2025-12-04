import azure.functions as func
import json
from ..shared.auth import validate_token

@validate_token
def main(req: func.HttpRequest) -> func.HttpResponse:
    # If we reached here, token is valid
    # In a real app, we might extract user info from the token payload
    # For now, just return success
    
    return func.HttpResponse(
        json.dumps({
            "status": "authenticated",
            "message": "You have accessed a protected endpoint!",
            "tenant_id": "cc8dfa60-ec68-406a-bebf-63fcf331d433"
        }),
        mimetype="application/json"
    )
