"""HTTP endpoint returning AI usage and cost guard metrics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

import azure.functions as func

from shared.utils import json_response, table_client


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _aggregate(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_tokens = sum(int(e.get("Tokens", 0)) for e in entries)
    total_runs = len(entries)
    last_run = max(( _parse_timestamp(e.get("Timestamp")) for e in entries ), default=None)

    by_model: Dict[str, int] = defaultdict(int)
    by_day: Dict[str, int] = defaultdict(int)

    for e in entries:
        model = e.get("Model", "unknown")
        by_model[model] += int(e.get("Tokens", 0))

        ts = _parse_timestamp(e.get("Timestamp"))
        if ts:
            by_day[ts.date().isoformat()] += int(e.get("Tokens", 0))

    recent_entries: List[Dict[str, Any]] = []
    for entry in entries[:20]:
        parsed_ts = _parse_timestamp(entry.get("Timestamp"))
        recent_entries.append({
            "timestamp": parsed_ts.isoformat() if parsed_ts else None,
            "workflow": entry.get("Workflow"),
            "operation": entry.get("Operation"),
            "tokens": int(entry.get("Tokens", 0)),
            "model": entry.get("Model"),
        })

    return {
        "totalTokens": total_tokens,
        "totalRuns": total_runs,
        "lastRun": last_run.isoformat() if last_run else None,
        "tokensByModel": dict(by_model),
        "tokensByDay": dict(by_day),
        "recent": recent_entries,
    }


def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId") or "GLOBAL"

    try:
        table = table_client("AiUsage")
    except Exception as exc:
        return func.HttpResponse(
            **json_response(
                {
                    "error": "AI usage datastore unavailable",
                    "details": str(exc),
                },
                status=503,
            )
        )

    query = f"PartitionKey eq '{tenant_id}'"
    entries: List[Dict[str, Any]] = []
    pager = table.query_entities(query, results_per_page=50)
    for entity in pager:  # type: ignore[assignment]
        entries.append(entity)
        if len(entries) >= 50:
            break

    entries.sort(key=lambda e: str(e.get("Timestamp", "")), reverse=True)

    summary = _aggregate(entries)
    summary.update({
        "tenantId": tenant_id,
        "hasData": bool(entries),
    })

    return func.HttpResponse(**json_response(summary))
