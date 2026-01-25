"""
Authentication middleware for Entra ID OIDC
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from jwt import PyJWKClient
import os

JWKS_URL = os.getenv("ENTRA_ID_JWKS_URL", "")
AUDIENCE = os.getenv("ENTRA_ID_AUDIENCE", "")

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """Verify JWT token and extract claims"""
    if not JWKS_URL or not AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication not configured"
        )
    
    try:
        # Get signing key from JWKS
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(credentials.credentials)
        
        # Decode and verify token
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUDIENCE
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from request"""
    credentials = await security(request)
    return await verify_token(credentials)
