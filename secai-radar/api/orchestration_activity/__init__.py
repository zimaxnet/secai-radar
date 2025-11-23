"""Durable Functions activity for executing AI steps with cost tracking."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from shared.ai_service import get_ai_service
from shared.utils import table_client


def _record_usage(
    tenant_id: str | None,
    workflow: str,
    operation: str,
    usage: Dict[str, Any],
    expected_tokens: int,
) -> None:
    try:
        table = table_client("AiUsage")
    except Exception as exc:
        logging.warning("AI usage table unavailable: %s", exc)
        return

    total_tokens = int(usage.get("total_tokens", expected_tokens))
    model_name = usage.get("model") or os.getenv("AZURE_OPENAI_DEPLOYMENT", "unknown")

    entity = {
        "PartitionKey": tenant_id or "GLOBAL",
        "RowKey": f"{workflow}-{uuid4().hex}",
        "Workflow": workflow,
        "Operation": operation,
        "Model": model_name,
        "Tokens": total_tokens,
        "ExpectedTokens": expected_tokens,
        "Timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        table.upsert_entity(entity)
    except Exception as exc:
        logging.warning("Unable to record AI usage telemetry: %s", exc)


def _classify_evidence(ai_payload: Dict[str, Any]) -> Dict[str, Any]:
    ai_service = get_ai_service()
    description = ai_payload.get("description") or ai_payload.get("text", "")
    if not description:
        raise ValueError("Evidence description is required for classification.")

    file_name = ai_payload.get("fileName")
    classification, usage = ai_service.classify_evidence(
        evidence_description=description,
        file_name=file_name,
        include_usage=True,
    )

    return {
        "payload": {
            "classification": classification,
            "fileName": file_name,
            "evidenceId": ai_payload.get("id"),
        },
        "usage": {
            "total_tokens": (usage or {}).get("total_tokens", 0),
            **(usage or {}),
        },
    }


def _generate_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenantId")
    summary = payload.get("summary")
    gaps = payload.get("gaps", [])

    if not summary:
        raise ValueError("Report summary data is required for report generation.")

    ai_service = get_ai_service()
    text, usage = ai_service.generate_report_summary(
        tenant_id=tenant_id,
        summary_data=summary,
        gaps_summary=gaps,
        include_usage=True,
    )

    return {
        "payload": {
            "executiveSummary": text,
        },
        "usage": {
            "total_tokens": (usage or {}).get("total_tokens", 0),
            **(usage or {}),
        },
    }


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    operation = context.get("operation")
    workflow = context.get("workflow", "unknown")
    tenant_id = context.get("tenantId")
    expected_tokens = int(context.get("expected_tokens", 0))

    if not operation:
        raise ValueError("Activity payload requires an 'operation'.")

    if operation == "classify_evidence":
        item = context.get("item") or {}
        result = _classify_evidence(item)
    elif operation == "generate_report":
        payload = context.get("payload") or {}
        result = _generate_report(payload)
    else:
        raise ValueError(f"Unsupported AI operation '{operation}'.")

    usage = result.get("usage", {})
    if usage.get("total_tokens") == 0 and expected_tokens:
        usage["total_tokens"] = expected_tokens

    _record_usage(tenant_id, workflow, operation, usage, expected_tokens)

    return {
        "operation": operation,
        "usage": usage,
        "result": result.get("payload"),
    }
