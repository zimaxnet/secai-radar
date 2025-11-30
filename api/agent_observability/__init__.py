"""
Agent Observability API Endpoint

Provides HTTP API for retrieving agent observability metrics and traces.
"""

import azure.functions as func
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from shared.utils import json_response
from shared.observability import get_observability_service


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle agent observability requests.
    
    Endpoints:
    - GET /api/observability/metrics - Get observability metrics
    """
    # Handle OPTIONS for CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(**json_response({}))
    
    if req.method != "GET":
        return func.HttpResponse(**json_response({
            "error": "Method not allowed"
        }, status=405))
    
    try:
        agent_id = req.params.get("agent_id")
        time_range = req.params.get("time_range", "24h")
        
        # Parse time range
        if time_range == "1h":
            start_time = datetime.utcnow() - timedelta(hours=1)
        elif time_range == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        elif time_range == "30d":
            start_time = datetime.utcnow() - timedelta(days=30)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        
        # Get metrics (mock data for now - in production, query Application Insights)
        metrics = _get_metrics(agent_id, start_time)
        
        return func.HttpResponse(**json_response(metrics))
    
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Internal server error",
            "details": str(e)
        }, status=500))


def _get_metrics(agent_id: Optional[str], start_time: datetime) -> Dict[str, Any]:
    """
    Get observability metrics.
    
    In production, this would query Application Insights or other telemetry store.
    For now, return mock data.
    """
    # Generate mock time series data
    now = datetime.utcnow()
    time_points = []
    current = start_time
    
    while current <= now:
        time_points.append({
            "time": current.isoformat(),
            "avg_ms": 150 + (hash(str(current)) % 100),  # Mock response time
            "p95_ms": 250 + (hash(str(current)) % 150)
        })
        current += timedelta(minutes=15)
    
    # Mock token usage by agent
    activity_data = []
    if agent_id:
        activity_data.append({
            "agent_id": agent_id,
            "actions": 100 + (hash(agent_id) % 200)
        })
    else:
        # All agents
        for agent in ["aris_thorne", "leo_vance", "ravi_patel", "kenji_sato", "elena_bridges", "marcus_sterling"]:
            activity_data.append({
                "agent_id": agent,
                "actions": 50 + (hash(agent) % 150)
            })
    
    # Mock token usage
    token_usage = []
    for agent in activity_data:
        token_usage.append({
            "agent_id": agent["agent_id"],
            "tokens": 1000 + (hash(agent["agent_id"]) % 5000)
        })
    
    # Mock evaluation scores
    evaluation_scores = []
    for point in time_points[:10]:  # Sample 10 points
        evaluation_scores.append({
            "time": point["time"],
            "groundedness": 0.7 + (hash(point["time"]) % 30) / 100,
            "task_adherence": 0.8 + (hash(point["time"]) % 20) / 100,
            "tool_accuracy": 0.85 + (hash(point["time"]) % 15) / 100
        })
    
    # Summary
    summary = {
        "avg_response_time_ms": 175.5,
        "total_tokens": sum(t["tokens"] for t in token_usage),
        "avg_groundedness": 0.82,
        "total_tool_calls": sum(a["actions"] for a in activity_data)
    }
    
    return {
        "response_time": time_points,
        "activity": activity_data,
        "token_usage": token_usage,
        "evaluation_scores": evaluation_scores,
        "summary": summary
    }

