"""
ETag and caching middleware
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import hashlib
import json


def generate_etag(data: dict) -> str:
    """Generate ETag from response data"""
    content = json.dumps(data, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


async def etag_middleware(request: Request, call_next):
    """ETag middleware for caching"""
    response = await call_next(request)
    
    # Only add ETag for GET requests with JSON responses
    if request.method == "GET" and isinstance(response, JSONResponse):
        body = response.body
        if body:
            try:
                data = json.loads(body)
                etag = generate_etag(data)
                response.headers["ETag"] = f'"{etag}"'
                response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
                
                # Check If-None-Match header
                if_none_match = request.headers.get("If-None-Match")
                if if_none_match and if_none_match.strip('"') == etag:
                    return Response(
                        status_code=304,
                        headers={
                            "ETag": f'"{etag}"',
                            "Cache-Control": "public, max-age=300",
                        },
                    )
            except:
                pass
    
    return response
