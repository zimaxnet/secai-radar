from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="SecAI Radar API", version="2.0.0", description="Security Assessment AI Platform")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "SecAI Radar API v2.0 is running",
        "version": "2.0.0",
        "features": [
            "Multi-Agent AI System",
            "Security Assessment Workflows",
            "Control Management",
            "Gap Analysis",
            "Tool Inventory"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Import routes
from src.routes import assessments, controls
app.include_router(assessments.router)
app.include_router(controls.router)

# Agent endpoints
from src.orchestrator import Orchestrator
from pydantic import BaseModel

orchestrator = Orchestrator()

class ChatRequest(BaseModel):
    message: str

@app.post("/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Chat with a specific AI agent"""
    response = await orchestrator.dispatch(agent_id, {"query": request.message})
    return response

@app.post("/agents/aris/upload")
async def upload_to_aris(file: UploadFile = File(...)):
    """
    Upload a file to Aris's knowledge base.
    """
    agent = orchestrator.agents.get("aris")
    if not agent:
        return {"error": "Aris agent not found"}
    
    # Save uploaded file temporarily
    import tempfile
    import os
    
    # Create temp directory if it doesn't exist
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        result = await agent.upload_knowledge_base(temp_path, display_name=file.filename)
    return result
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

