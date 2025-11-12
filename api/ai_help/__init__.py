"""Contextual AI help endpoint."""

from __future__ import annotations

import json
from typing import Any, Dict

import azure.functions as func

from shared.ai_service import get_ai_service
from shared.utils import json_response

SYSTEM_PROMPT = (
    "You are SecAI Radar's in-app assistant. Provide concise, actionable guidance about the "
    "current screen, explaining concepts such as hard gaps, coverage calculations, and workflows. "
    "Base responses on provided context; if unsure, suggest where the user can find the answer."
)


def build_prompt(question: str, context: Dict[str, Any]) -> list[Dict[str, str]]:
    context_text = json.dumps(context, indent=2)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Context about the page the user is viewing:\n"
                f"{context_text}\n\n"
                f"User question: {question}\n"
                "Explain the answer in under 180 words, using bullet points where helpful."
            ),
        },
    ]


def main(req: func.HttpRequest) -> func.HttpResponse:
    tenant_id = req.route_params.get("tenantId")
    if not tenant_id:
        return func.HttpResponse(**json_response({"error": "tenantId is required"}, status=400))

    try:
        payload = req.get_json()
    except ValueError:
        payload = {}

    question = (payload.get("question") or "").strip()
    context = payload.get("context") or {}

    if not question:
        return func.HttpResponse(**json_response({"error": "question is required"}, status=400))

    try:
        ai_service = get_ai_service()
        messages = build_prompt(question, context)
        completion = ai_service.chat_completion(messages=messages, stream=False, temperature=0.4, max_tokens=512)
        answer = completion.choices[0].message.content if completion.choices else "No answer available."

        return func.HttpResponse(
            **json_response(
                {
                    "answer": answer,
                    "tenantId": tenant_id,
                    "context": context,
                }
            )
        )
    except Exception as exc:  # pylint: disable=broad-except
        return func.HttpResponse(
            **json_response(
                {
                    "error": "AI help unavailable",
                    "details": str(exc),
                },
                status=500,
            )
        )
