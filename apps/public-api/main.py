"""
Public API service for SecAI Radar Verified MCP
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from src.middleware.etag import etag_middleware
from src.middleware.rate_limit import rate_limit_middleware

app = FastAPI(
    title="SecAI Radar Public API",
    description="Public read-only API for Verified MCP Trust Hub",
    version="1.0.0"
)

# CORS middleware - must be added first to apply to all responses
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "https://secairadar.cloud",
    "https://www.secairadar.cloud"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Rate limiting (T-130) then ETag
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(etag_middleware)

# Global exception handlers to ensure CORS headers are included in error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions with proper CORS headers"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if str(exc) else "Unknown error"
        },
        headers={
            "Access-Control-Allow-Origin": "https://secairadar.cloud, https://www.secairadar.cloud",
            "Access-Control-Allow-Credentials": "true",
        }
    )

METHODOLOGY_VERSION = "v1.0"


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/public/health")
async def public_health():
    """Public health check with methodology version"""
    return {
        "status": "ok",
        "methodologyVersion": METHODOLOGY_VERSION,
        "generatedAt": datetime.utcnow().isoformat()
    }


# Import routers
from src.routers import public, status, pipeline

# Include routers
app.include_router(public.router)
app.include_router(status.router)
app.include_router(pipeline.router)

# Graph router (optional)
try:
    from src.routers import graph
    app.include_router(graph.router)
except ImportError:
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
