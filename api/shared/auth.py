import os
import logging
import jwt
from functools import wraps
import azure.functions as func
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

def validate_token(f):
    @wraps(f)
    def decorated_function(req: func.HttpRequest, *args, **kwargs):
        token = None
        auth_header = req.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return func.HttpResponse("Missing authentication token", status_code=401)

        try:
            tenant_id = os.getenv("ENTRA_TENANT_ID")
            client_id = os.getenv("ENTRA_CLIENT_ID")
            
            if not tenant_id or not client_id:
                logger.error("Entra configuration missing")
                return func.HttpResponse("Server configuration error", status_code=500)

            # Entra External ID (CIAM) issuer format
            # https://login.microsoftonline.com/{tenant_id}/v2.0 or https://{domain}.ciamlogin.com/{tenant_id}/v2.0
            # We'll use the JWKS endpoint to fetch keys
            
            # Construct JWKS URL. For CIAM, it's often:
            # https://{tenant_subdomain}.ciamlogin.com/{tenant_id}/discovery/v2.0/keys
            # But standard Entra is: https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys
            
            # We'll try the standard one first or allow override
            jwks_url = os.getenv("ENTRA_JWKS_URL", f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys")
            
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            # Validate token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=client_id,
                # Issuer validation can be tricky with CIAM vs standard, so we might skip or make it flexible
                # issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0", 
                options={"verify_iss": False} # verifying issuer strictly can fail if using ciamlogin.com vs login.microsoftonline.com
            )
            
            # Add user info to request context (if possible) or just pass
            # req.context['user'] = payload # Azure Functions req doesn't have mutable context like Flask
            
        except jwt.ExpiredSignatureError:
            return func.HttpResponse("Token expired", status_code=401)
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return func.HttpResponse("Invalid token", status_code=401)
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return func.HttpResponse("Authentication failed", status_code=401)

        return f(req, *args, **kwargs)
    
    return decorated_function
