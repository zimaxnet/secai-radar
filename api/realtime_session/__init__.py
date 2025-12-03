import json
import logging
os_env = __import__("os")

import azure.functions as func
import httpx


from shared.key_vault import get_secret_from_key_vault_or_env

API_VERSION = os_env.getenv("AZURE_OPENAI_REALTIME_API_VERSION", "2024-10-01-preview")


def _cors_headers() -> dict[str, str]:
    return {
        "Access-Control-Allow-Origin": os_env.getenv("REALTIME_PROXY_ALLOWED_ORIGIN", "*"),
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


async def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=_cors_headers())

    if req.method != "POST":
        return func.HttpResponse(status_code=405, headers=_cors_headers())

    try:
        payload = req.get_json()
    except ValueError:
        payload = {}

    sdp_offer: str | None = payload.get("sdpOffer") or payload.get("sdp_offer")
    if not sdp_offer:
        return func.HttpResponse(
            json.dumps({"error": "sdpOffer is required"}),
            status_code=400,
            mimetype="application/json",
            headers=_cors_headers(),
        )

    endpoint = get_secret_from_key_vault_or_env("azure-openai-realtime-endpoint", "AZURE_OPENAI_REALTIME_ENDPOINT")
    api_key = get_secret_from_key_vault_or_env("azure-openai-realtime-key", "AZURE_OPENAI_REALTIME_KEY")
    deployment = payload.get("deployment") or os_env.getenv("AZURE_OPENAI_REALTIME_DEPLOYMENT", "gpt-realtime")

    if not endpoint or not api_key:
        logging.error("Realtime endpoint/key not configured")
        return func.HttpResponse(
            json.dumps({"error": "Realtime endpoint or key not configured"}),
            status_code=500,
            mimetype="application/json",
            headers=_cors_headers(),
        )

    url = f"{endpoint}?api-version={API_VERSION}&deployment={deployment}"
    headers = {
        "Content-Type": "application/sdp",
        "Accept": "application/sdp",
        "api-key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            upstream_response = await client.post(url, content=sdp_offer.encode("utf-8"), headers=headers)
    except httpx.RequestError as exc:  # type: ignore[name-defined]
        logging.exception("Call to Azure OpenAI realtime endpoint failed")
        return func.HttpResponse(
            json.dumps({"error": "Failed to reach realtime endpoint", "details": str(exc)}),
            status_code=502,
            mimetype="application/json",
            headers=_cors_headers(),
        )

    if upstream_response.status_code >= 400:
        logging.error(
            "Realtime handshake failed with status %s", upstream_response.status_code
        )
        return func.HttpResponse(
            upstream_response.text,
            status_code=upstream_response.status_code,
            mimetype="text/plain",
            headers=_cors_headers(),
        )

    return func.HttpResponse(
        upstream_response.text,
        status_code=200,
        mimetype="application/sdp",
        headers=_cors_headers(),
    )
