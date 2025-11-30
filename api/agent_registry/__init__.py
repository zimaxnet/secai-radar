"""
Agent Registry API Endpoint

Provides HTTP API for managing the agent registry:
- List and search agents
- Get agent details
- Register new agents
- Update agent status
- Manage collections (quarantine, custom collections)
"""

import azure.functions as func
from typing import Dict, Any, Optional
import json

from shared.utils import json_response
from shared.registry_service import get_registry_service, AgentStatus


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle agent registry requests.
    
    Endpoints:
    - GET /api/registry/agents - List all agents (with optional filters)
    - GET /api/registry/agents/{agentId} - Get agent details
    - POST /api/registry/agents - Register a new agent
    - PUT /api/registry/agents/{agentId}/status - Update agent status
    - PUT /api/registry/agents/{agentId}/collections - Add/remove from collection
    - POST /api/registry/agents/{agentId}/quarantine - Quarantine agent
    - DELETE /api/registry/agents/{agentId}/quarantine - Unquarantine agent
    """
    registry = get_registry_service()
    
    # Parse route parameters
    agent_id = req.route_params.get("agentId")
    action = req.route_params.get("action")
    
    # Handle OPTIONS for CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(**json_response({}))
    
    try:
        if req.method == "GET":
            if agent_id:
                return _get_agent(registry, agent_id)
            else:
                return _list_agents(registry, req)
        
        elif req.method == "POST":
            if action == "quarantine" and agent_id:
                return _quarantine_agent(registry, agent_id)
            else:
                return _register_agent(registry, req)
        
        elif req.method == "PUT":
            if action == "status" and agent_id:
                return _update_status(registry, agent_id, req)
            elif action == "collections" and agent_id:
                return _update_collections(registry, agent_id, req)
            else:
                return func.HttpResponse(**json_response({"error": "Invalid endpoint"}, status=400))
        
        elif req.method == "DELETE":
            if action == "quarantine" and agent_id:
                return _unquarantine_agent(registry, agent_id)
            else:
                return func.HttpResponse(**json_response({"error": "Invalid endpoint"}, status=400))
        
        else:
            return func.HttpResponse(**json_response({"error": "Method not allowed"}, status=405))
    
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Internal server error",
            "details": str(e)
        }, status=500))


def _list_agents(registry, req: func.HttpRequest) -> func.HttpResponse:
    """List agents with optional filters"""
    # Parse query parameters
    status = req.params.get("status")
    collection = req.params.get("collection")
    blueprint = req.params.get("blueprint")
    capability = req.params.get("capability")
    
    agents = registry.list_agents(
        status=status,
        collection=collection,
        blueprint=blueprint,
        capability=capability
    )
    
    # Convert to dict for JSON serialization
    agents_data = []
    for agent in agents:
        agent_dict = {
            "agent_id": agent.agent_id,
            "entra_agent_id": agent.entra_agent_id,
            "name": agent.name,
            "role": agent.role,
            "status": agent.status,
            "blueprint": agent.blueprint,
            "capabilities": agent.capabilities,
            "collections": agent.collections,
            "last_active_at": agent.last_active_at.isoformat() if agent.last_active_at else None,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat(),
            "metadata": agent.metadata
        }
        agents_data.append(agent_dict)
    
    return func.HttpResponse(**json_response({
        "agents": agents_data,
        "count": len(agents_data)
    }))


def _get_agent(registry, agent_id: str) -> func.HttpResponse:
    """Get agent details"""
    agent = registry.get_agent(agent_id)
    
    if not agent:
        return func.HttpResponse(**json_response({
            "error": "Agent not found",
            "agent_id": agent_id
        }, status=404))
    
    agent_dict = {
        "agent_id": agent.agent_id,
        "entra_agent_id": agent.entra_agent_id,
        "name": agent.name,
        "role": agent.role,
        "status": agent.status,
        "blueprint": agent.blueprint,
        "capabilities": agent.capabilities,
        "collections": agent.collections,
        "last_active_at": agent.last_active_at.isoformat() if agent.last_active_at else None,
        "created_at": agent.created_at.isoformat(),
        "updated_at": agent.updated_at.isoformat(),
        "metadata": agent.metadata
    }
    
    return func.HttpResponse(**json_response(agent_dict))


def _register_agent(registry, req: func.HttpRequest) -> func.HttpResponse:
    """Register a new agent"""
    body = req.get_json() or {}
    
    required_fields = ["agent_id", "name", "role", "blueprint", "capabilities"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(**json_response({
                "error": f"Missing required field: {field}"
            }, status=400))
    
    try:
        entry = registry.register_agent(
            agent_id=body["agent_id"],
            entra_agent_id=body.get("entra_agent_id"),
            name=body["name"],
            role=body["role"],
            blueprint=body["blueprint"],
            capabilities=body["capabilities"],
            collections=body.get("collections"),
            metadata=body.get("metadata")
        )
        
        return func.HttpResponse(**json_response({
            "agent_id": entry.agent_id,
            "entra_agent_id": entry.entra_agent_id,
            "status": entry.status,
            "message": "Agent registered successfully"
        }, status=201))
    
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Failed to register agent",
            "details": str(e)
        }, status=500))


def _update_status(registry, agent_id: str, req: func.HttpRequest) -> func.HttpResponse:
    """Update agent status"""
    body = req.get_json() or {}
    status = body.get("status")
    
    if not status:
        return func.HttpResponse(**json_response({
            "error": "Missing required field: status"
        }, status=400))
    
    # Validate status
    valid_statuses = [s.value for s in AgentStatus]
    if status not in valid_statuses:
        return func.HttpResponse(**json_response({
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }, status=400))
    
    success = registry.update_agent_status(agent_id, status)
    
    if not success:
        return func.HttpResponse(**json_response({
            "error": "Failed to update agent status",
            "agent_id": agent_id
        }, status=500))
    
    return func.HttpResponse(**json_response({
        "agent_id": agent_id,
        "status": status,
        "message": "Status updated successfully"
    }))


def _update_collections(registry, agent_id: str, req: func.HttpRequest) -> func.HttpResponse:
    """Add or remove agent from collections"""
    body = req.get_json() or {}
    action = body.get("action")  # "add" or "remove"
    collection_name = body.get("collection_name")
    
    if not action or not collection_name:
        return func.HttpResponse(**json_response({
            "error": "Missing required fields: action, collection_name"
        }, status=400))
    
    if action == "add":
        success = registry.add_to_collection(agent_id, collection_name)
    elif action == "remove":
        success = registry.remove_from_collection(agent_id, collection_name)
    else:
        return func.HttpResponse(**json_response({
            "error": "Invalid action. Must be 'add' or 'remove'"
        }, status=400))
    
    if not success:
        return func.HttpResponse(**json_response({
            "error": f"Failed to {action} collection",
            "agent_id": agent_id
        }, status=500))
    
    return func.HttpResponse(**json_response({
        "agent_id": agent_id,
        "action": action,
        "collection_name": collection_name,
        "message": f"Collection {action}ed successfully"
    }))


def _quarantine_agent(registry, agent_id: str) -> func.HttpResponse:
    """Quarantine an agent"""
    success = registry.quarantine_agent(agent_id)
    
    if not success:
        return func.HttpResponse(**json_response({
            "error": "Failed to quarantine agent",
            "agent_id": agent_id
        }, status=500))
    
    return func.HttpResponse(**json_response({
        "agent_id": agent_id,
        "status": "quarantined",
        "message": "Agent quarantined successfully"
    }))


def _unquarantine_agent(registry, agent_id: str) -> func.HttpResponse:
    """Unquarantine an agent"""
    success = registry.unquarantine_agent(agent_id)
    
    if not success:
        return func.HttpResponse(**json_response({
            "error": "Failed to unquarantine agent",
            "agent_id": agent_id
        }, status=500))
    
    return func.HttpResponse(**json_response({
        "agent_id": agent_id,
        "status": "active",
        "message": "Agent unquarantined successfully"
    }))

