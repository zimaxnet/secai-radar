"""Durable Functions orchestrator for AI workflows with budget guardrails."""

from __future__ import annotations

from typing import Any, Dict, List

import azure.durable_functions as df

from shared.workflow_loader import WorkflowNotFoundError, load_workflow


def _validate_budget(max_calls: int, calls: int, max_tokens: int, tokens: int) -> None:
    if calls > max_calls:
        raise ValueError("AI workflow exceeded call budget.")
    if tokens > max_tokens:
        raise ValueError("AI workflow exceeded token budget.")


def _compute_expected(step: Dict[str, Any], defaults: Dict[str, Any]) -> int:
    if "expected_tokens" in step:
        return int(step["expected_tokens"])
    if step.get("type") == "fanout":
        return int(defaults.get("expected_tokens_per_item", 0))
    return int(defaults.get("expected_tokens", 0))


async def orchestrator_function(context: df.DurableOrchestrationContext) -> Dict[str, Any]:
    payload: Dict[str, Any] = context.get_input() or {}
    workflow_name = payload.get("workflow")
    if not workflow_name:
        raise ValueError("Missing 'workflow' in orchestration payload.")

    try:
        workflow = load_workflow(workflow_name)
    except WorkflowNotFoundError as exc:
        raise ValueError(str(exc)) from exc

    budget = workflow.get("budget", {})
    max_tokens = int(payload.get("maxTokens", budget.get("max_tokens", 4096)))
    max_calls = int(payload.get("maxCalls", budget.get("max_calls", 10)))

    tokens_used = 0
    calls_made = 0
    results: List[Dict[str, Any]] = []

    steps = workflow.get("steps", [])
    defaults = workflow.get("defaults", {})

    for step in steps:
        step_type = step.get("type", "activity")
        expected_tokens = _compute_expected(step, defaults)

        if step_type == "fanout":
            source_key = step.get("source")
            items = payload.get(source_key or "items", [])
            if not isinstance(items, list):
                raise ValueError("Fanout steps require 'items' list in payload.")

            for item in items:
                if calls_made + 1 > max_calls:
                    raise ValueError("AI workflow exceeded call budget.")
                if tokens_used + expected_tokens > max_tokens:
                    raise ValueError("AI workflow exceeded token budget.")

                activity_payload = {
                    "operation": step.get("operation"),
                    "item": item,
                    "tenantId": payload.get("tenantId"),
                    "workflow": workflow_name,
                    "expected_tokens": expected_tokens,
                    "metadata": payload.get("metadata", {}),
                }

                result = await context.call_activity(step["activity"], activity_payload)
                usage_tokens = int(result.get("usage", {}).get("total_tokens", expected_tokens))

                tokens_used += usage_tokens
                calls_made += 1
                _validate_budget(max_calls, calls_made, max_tokens, tokens_used)
                results.append(result)
        else:
            if calls_made + 1 > max_calls:
                raise ValueError("AI workflow exceeded call budget.")
            if tokens_used + expected_tokens > max_tokens:
                raise ValueError("AI workflow exceeded token budget.")

            activity_payload = {
                "operation": step.get("operation"),
                "payload": payload,
                "tenantId": payload.get("tenantId"),
                "workflow": workflow_name,
                "expected_tokens": expected_tokens,
            }

            result = await context.call_activity(step["activity"], activity_payload)
            usage_tokens = int(result.get("usage", {}).get("total_tokens", expected_tokens))

            tokens_used += usage_tokens
            calls_made += 1
            _validate_budget(max_calls, calls_made, max_tokens, tokens_used)
            results.append(result)

    return {
        "status": "completed",
        "workflow": workflow_name,
        "results": results,
        "budget": {
            "max_tokens": max_tokens,
            "tokens_used": tokens_used,
            "max_calls": max_calls,
            "calls_used": calls_made,
        },
    }


main = df.Orchestrator.create(orchestrator_function)
