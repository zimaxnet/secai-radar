"""
Public API service for SecAI Radar Verified MCP
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from src.middleware.etag import etag_middleware

app = FastAPI(
    title="SecAI Radar Public API",
    description="Public read-only API for Verified MCP Trust Hub",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ETag middleware
app.middleware("http")(etag_middleware)

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
from src.routers import public, status

# Include routers
app.include_router(public.router)
app.include_router(status.router)

# Graph router (optional)
try:
    from src.routers import graph
    app.include_router(graph.router)
except ImportError:
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
