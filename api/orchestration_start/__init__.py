"""HTTP starter for AI durable workflows with budget guardrails."""

from __future__ import annotations

import json
from datetime import timedelta

import azure.durable_functions as df
import azure.functions as func


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)

    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Request body must be valid JSON."}),
            status_code=400,
            mimetype="application/json",
        )

    if not isinstance(payload, dict) or "workflow" not in payload:
        return func.HttpResponse(
            json.dumps({"error": "Payload must include a 'workflow' property."}),
            status_code=400,
            mimetype="application/json",
        )

    tenant_id = req.route_params.get("tenantId")
    if tenant_id and not payload.get("tenantId"):
        payload["tenantId"] = tenant_id

    instance_id = await client.start_new("orchestration", None, payload)

    timeout_seconds = int(req.params.get("timeout", "15"))
    timeout_seconds = max(5, min(timeout_seconds, 60))

    response = await client.wait_for_completion_or_create_check_status_response(
        req,
        instance_id,
        timeout=timedelta(seconds=timeout_seconds),
    )

    return response
