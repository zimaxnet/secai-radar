"""
Agent Evaluations API Endpoint

Provides HTTP API for running agent evaluations and retrieving evaluation results.
"""

import azure.functions as func
from typing import Dict, Any
from datetime import datetime

from shared.utils import json_response
from shared.evaluators import get_evaluator_service


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handle agent evaluation requests.
    
    Endpoints:
    - POST /api/evaluations/evaluate - Run comprehensive evaluation
    - POST /api/evaluations/groundedness - Evaluate groundedness
    - POST /api/evaluations/task-adherence - Evaluate task adherence
    - POST /api/evaluations/tool-accuracy - Evaluate tool accuracy
    - POST /api/evaluations/relevance - Evaluate relevance
    """
    evaluator = get_evaluator_service()
    
    # Handle OPTIONS for CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(**json_response({}))
    
    if req.method != "POST":
        return func.HttpResponse(**json_response({
            "error": "Method not allowed"
        }, status=405))
    
    try:
        body = req.get_json() or {}
        route = req.route_params.get("evaluationType", "evaluate")
        
        if route == "evaluate":
            return _run_comprehensive_evaluation(evaluator, body)
        elif route == "groundedness":
            return _evaluate_groundedness(evaluator, body)
        elif route == "task-adherence":
            return _evaluate_task_adherence(evaluator, body)
        elif route == "tool-accuracy":
            return _evaluate_tool_accuracy(evaluator, body)
        elif route == "relevance":
            return _evaluate_relevance(evaluator, body)
        else:
            return func.HttpResponse(**json_response({
                "error": "Invalid evaluation type"
            }, status=400))
    
    except Exception as e:
        return func.HttpResponse(**json_response({
            "error": "Internal server error",
            "details": str(e)
        }, status=500))


def _run_comprehensive_evaluation(evaluator, body: Dict[str, Any]) -> func.HttpResponse:
    """Run comprehensive evaluation"""
    required_fields = ["agent_id", "response"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(**json_response({
                "error": f"Missing required field: {field}"
            }, status=400))
    
    scores = evaluator.run_comprehensive_evaluation(
        agent_id=body["agent_id"],
        response=body["response"],
        context=body.get("context"),
        task_instruction=body.get("task_instruction"),
        query=body.get("query"),
        tool_calls=body.get("tool_calls")
    )
    
    return func.HttpResponse(**json_response({
        "agent_id": body["agent_id"],
        "scores": scores,
        "timestamp": datetime.utcnow().isoformat()
    }))


def _evaluate_groundedness(evaluator, body: Dict[str, Any]) -> func.HttpResponse:
    """Evaluate groundedness"""
    required_fields = ["response", "context"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(**json_response({
                "error": f"Missing required field: {field}"
            }, status=400))
    
    score = evaluator.evaluate_groundedness(
        response=body["response"],
        context=body["context"],
        agent_id=body.get("agent_id")
    )
    
    return func.HttpResponse(**json_response({
        "agent_id": body.get("agent_id"),
        "evaluation_type": "groundedness",
        "score": score
    }))


def _evaluate_task_adherence(evaluator, body: Dict[str, Any]) -> func.HttpResponse:
    """Evaluate task adherence"""
    required_fields = ["response", "task_instruction"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(**json_response({
                "error": f"Missing required field: {field}"
            }, status=400))
    
    score = evaluator.evaluate_task_adherence(
        response=body["response"],
        task_instruction=body["task_instruction"],
        agent_id=body.get("agent_id")
    )
    
    return func.HttpResponse(**json_response({
        "agent_id": body.get("agent_id"),
        "evaluation_type": "task_adherence",
        "score": score
    }))


def _evaluate_tool_accuracy(evaluator, body: Dict[str, Any]) -> func.HttpResponse:
    """Evaluate tool accuracy"""
    required_fields = ["tool_calls"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(**json_response({
                "error": f"Missing required field: {field}"
            }, status=400))
    
    score = evaluator.evaluate_tool_accuracy(
        tool_calls=body["tool_calls"],
        expected_behavior=body.get("expected_behavior"),
        actual_results=body.get("actual_results"),
        agent_id=body.get("agent_id")
    )
    
    return func.HttpResponse(**json_response({
        "agent_id": body.get("agent_id"),
        "evaluation_type": "tool_accuracy",
        "score": score
    }))


def _evaluate_relevance(evaluator, body: Dict[str, Any]) -> func.HttpResponse:
    """Evaluate relevance"""
    required_fields = ["response", "query"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(**json_response({
                "error": f"Missing required field: {field}"
            }, status=400))
    
    score = evaluator.evaluate_relevance(
        response=body["response"],
        query=body["query"],
        agent_id=body.get("agent_id")
    )
    
    return func.HttpResponse(**json_response({
        "agent_id": body.get("agent_id"),
        "evaluation_type": "relevance",
        "score": score
    }))

