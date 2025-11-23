"""
Multi-Agent Assessment API Endpoint

Provides HTTP API for triggering and managing multi-agent security assessments.
"""

import json
import asyncio
import azure.functions as func
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add src directory to path for imports
src_path = Path(__file__).resolve().parents[1] / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from shared.utils import json_response

# Import orchestrator components
try:
    # Import from src/orchestrator
    import sys
    from pathlib import Path
    src_path = Path(__file__).resolve().parents[1] / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from orchestrator.initialize import initialize_orchestrator
    from orchestrator.state import StateManager
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Orchestrator not available: {e}")
    ORCHESTRATOR_AVAILABLE = False
    initialize_orchestrator = None
    StateManager = None


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle multi-agent assessment requests.
    
    Endpoints:
    - POST /api/tenant/{tenantId}/multi-agent-assessment
        Start a new multi-agent assessment
        
    - GET /api/tenant/{tenantId}/multi-agent-assessment/{assessmentId}
        Get assessment status and results
        
    - GET /api/tenant/{tenantId}/multi-agent-assessment
        List all assessments for tenant
    """
    tenant_id = req.route_params.get("tenantId")
    assessment_id = req.route_params.get("assessmentId")
    
    if not tenant_id:
        return func.HttpResponse(
            **json_response({"error": "tenantId is required"}, status=400)
        )
    
    if req.method == "POST":
        return _start_assessment(req, tenant_id)
    elif req.method == "GET":
        if assessment_id:
            return _get_assessment_status(tenant_id, assessment_id)
        else:
            return _list_assessments(tenant_id)
    else:
        return func.HttpResponse(
            **json_response({"error": "Method not allowed"}, status=405)
        )


def _start_assessment(req: func.HttpRequest, tenant_id: str) -> func.HttpResponse:
    """Start a new multi-agent assessment"""
    if not ORCHESTRATOR_AVAILABLE:
        return func.HttpResponse(
            **json_response({
                "error": "Multi-agent orchestrator not available. Check configuration.",
                "details": "Ensure all dependencies are installed and environment variables are set."
            }, status=503)
        )
    
    try:
        # Parse request body
        body = req.get_json() or {}
        
        # Generate assessment ID if not provided
        assessment_id = body.get("assessment_id") or f"assessment-{tenant_id}-{int(__import__('time').time())}"
        
        # Get budget from request or use default
        budget = float(body.get("budget", 100000.0))
        
        # Initialize orchestrator
        try:
            graph = initialize_orchestrator()
        except Exception as e:
            return func.HttpResponse(
                **json_response({
                    "error": "Failed to initialize orchestrator",
                    "details": str(e)
                }, status=500)
            )
        
        # Create initial state
        state_manager = StateManager()
        initial_state = state_manager.create_initial_state(
            assessment_id=assessment_id,
            tenant_id=tenant_id,
            budget=budget
        )
        
        # Run assessment asynchronously
        # Note: In production, you might want to use Durable Functions or a queue
        # For now, we'll run it synchronously (which may timeout for long assessments)
        try:
            # Create event loop and run the graph
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                final_state = loop.run_until_complete(graph.run(initial_state))
            finally:
                loop.close()
            
            # Extract results
            results = {
                "assessment_id": assessment_id,
                "tenant_id": tenant_id,
                "status": "completed" if final_state.get("is_complete") else "in_progress",
                "phase": final_state.get("phase", "unknown"),
                "findings_count": len(final_state.get("findings", [])),
                "events_count": len(final_state.get("events", [])),
                "budget_used": final_state.get("budget_used", 0.0),
                "findings": final_state.get("findings", [])[:10],  # Limit to first 10
                "summary": {
                    "total_findings": len(final_state.get("findings", [])),
                    "critical_risks": len(final_state.get("critical_risks", [])),
                    "active_conflicts": len(final_state.get("active_conflicts", [])),
                    "resolved_conflicts": len(final_state.get("resolved_conflicts", []))
                }
            }
            
            return func.HttpResponse(**json_response(results))
            
        except asyncio.TimeoutError:
            return func.HttpResponse(
                **json_response({
                    "error": "Assessment timed out",
                    "assessment_id": assessment_id,
                    "message": "Assessment is running but exceeded timeout. Check status later."
                }, status=504)
            )
        except Exception as e:
            return func.HttpResponse(
                **json_response({
                    "error": "Assessment failed",
                    "assessment_id": assessment_id,
                    "details": str(e)
                }, status=500)
            )
            
    except Exception as e:
        return func.HttpResponse(
            **json_response({
                "error": "Failed to start assessment",
                "details": str(e)
            }, status=500)
        )


def _get_assessment_status(tenant_id: str, assessment_id: str) -> func.HttpResponse:
    """Get assessment status and results"""
    if not ORCHESTRATOR_AVAILABLE:
        return func.HttpResponse(
            **json_response({"error": "Orchestrator not available"}, status=503)
        )
    
    try:
        # Load state from Cosmos DB
        state_manager = StateManager()
        state = state_manager.load_state(assessment_id)
        
        if not state:
            return func.HttpResponse(
                **json_response({
                    "error": "Assessment not found",
                    "assessment_id": assessment_id
                }, status=404)
            )
        
        # Verify tenant matches
        if state.get("tenant_id") != tenant_id:
            return func.HttpResponse(
                **json_response({"error": "Access denied"}, status=403)
            )
        
        # Return status
        results = {
            "assessment_id": assessment_id,
            "tenant_id": tenant_id,
            "status": "completed" if state.get("is_complete") else "in_progress",
            "phase": state.get("phase", "unknown"),
            "findings_count": len(state.get("findings", [])),
            "events_count": len(state.get("events", [])),
            "budget_used": state.get("budget_used", 0.0),
            "summary": {
                "total_findings": len(state.get("findings", [])),
                "critical_risks": len(state.get("critical_risks", [])),
                "active_conflicts": len(state.get("active_conflicts", [])),
                "resolved_conflicts": len(state.get("resolved_conflicts", []))
            },
            "updated_at": str(state.get("updated_at", ""))
        }
        
        return func.HttpResponse(**json_response(results))
        
    except Exception as e:
        return func.HttpResponse(
            **json_response({
                "error": "Failed to get assessment status",
                "details": str(e)
            }, status=500)
        )


def _list_assessments(tenant_id: str) -> func.HttpResponse:
    """List all assessments for a tenant"""
    if not ORCHESTRATOR_AVAILABLE:
        return func.HttpResponse(
            **json_response({"error": "Orchestrator not available"}, status=503)
        )
    
    try:
        # List assessments from Cosmos DB
        state_manager = StateManager()
        
        # Check if CosmosStatePersistence is available
        if hasattr(state_manager, 'cosmos_persistence') and state_manager.cosmos_persistence:
            assessments = state_manager.cosmos_persistence.list_assessments(tenant_id)
            
            # Format results
            results = []
            for assessment in assessments:
                results.append({
                    "assessment_id": assessment.get("assessment_id"),
                    "tenant_id": assessment.get("tenant_id"),
                    "status": "completed" if assessment.get("is_complete") else "in_progress",
                    "phase": assessment.get("phase", "unknown"),
                    "updated_at": str(assessment.get("updated_at", ""))
                })
            
            return func.HttpResponse(**json_response({"assessments": results}))
        else:
            return func.HttpResponse(
                **json_response({
                    "error": "Cosmos DB persistence not configured",
                    "message": "Cannot list assessments without Cosmos DB"
                }, status=503)
            )
            
    except Exception as e:
        return func.HttpResponse(
            **json_response({
                "error": "Failed to list assessments",
                "details": str(e)
            }, status=500)
        )

