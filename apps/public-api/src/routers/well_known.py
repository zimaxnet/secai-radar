"""
Well-known discovery endpoints for AI agent consumption.

Serves /llms.txt (Markdown) and /.well-known/trust-scores.json (JSON)
so that AI agents can auto-discover SecAI Radar trust data.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse
from datetime import datetime, timezone

from src.constants.attestation import (
    build_decay_parameters,
    REFRESH_CADENCE_HOURS,
)

router = APIRouter(tags=["discovery"])

METHODOLOGY_VERSION = "v1.0"
BASE_URL = "https://secairadar.cloud"


# Serve at both root paths AND API-prefixed paths
# Root paths work when hitting the API directly
# API-prefixed paths work through the Azure SWA proxy
@router.get("/llms.txt", response_class=PlainTextResponse)
@router.get("/api/v1/public/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """
    LLMs.txt — Markdown cheat-sheet for AI agents.
    Follows the llmstxt.org specification.
    """
    now = datetime.now(timezone.utc).isoformat()
    content = f"""# SecAI Radar

> Trust verification oracle for MCP servers and AI Agents.
> Algorithmically scored. Truth-decayed. Agent-parsable.

## What this is

SecAI Radar independently assesses the trustworthiness of Model Context Protocol (MCP) servers and AI Agents using a six-domain scoring methodology (Authentication, Authorization, Data Protection, Audit, Operational Security, Compliance). Scores are derived from real repository metadata, documentation claims, and GitHub popularity signals — not self-reported.

## Scoring methodology

Each integration is scored across six domains (D1–D6) on a 0–5 scale, weighted into a composite trust score. An exponential truth decay function (`score × e^(-λt)`) is applied based on evidence freshness class:
- **Class A** (Immutable Truth): λ = 0.01 — on-chain, SBOM, signed attestations
- **Class B** (Ephemeral Stream): λ = 0.50 — API responses, live config
- **Class C** (Operational Pulse): λ = 0.90 — GitHub stars, docs crawls

Scores refresh every {REFRESH_CADENCE_HOURS} hours.

## API endpoints (JSON)

- [MCP Rankings]({BASE_URL}/api/v1/public/mcp/rankings?pageSize=100)
- [Agent Rankings]({BASE_URL}/api/v1/public/agents/rankings?pageSize=100)
- [Discovery Manifest]({BASE_URL}/.well-known/trust-scores.json)
- [MCP Server Detail]({BASE_URL}/api/v1/public/mcp/{{idOrSlug}})
- [Agent Detail]({BASE_URL}/api/v1/public/agents/{{idOrSlug}})
- [Daily Brief]({BASE_URL}/api/v1/public/daily-brief/{{YYYY-MM-DD}})

## For agents

All ranking endpoints return structured JSON with:
- `@context` for JSON-LD framing
- `attestation` envelope with assessor identity and methodology version
- `decayParameters` with the full decay formula and per-class λ rates
- `domainScores` (d1–d6) per item for granular trust inspection
- `integrityDigest` (SHA-256) for tamper detection

Generated at: {now}
"""
    return PlainTextResponse(content=content, media_type="text/markdown")


@router.get("/.well-known/trust-scores.json", response_class=JSONResponse)
@router.get("/api/v1/public/discovery", response_class=JSONResponse)
async def well_known_trust_scores():
    """
    Machine-readable discovery manifest for AI agents.
    Inspired by agents.json / .well-known conventions.
    """
    now = datetime.now(timezone.utc).isoformat()
    return JSONResponse(content={
        "@context": "https://schema.org",
        "@type": "WebAPI",
        "name": "SecAI Radar Trust Scores API",
        "description": "Independent trust verification for MCP servers and AI Agents",
        "url": BASE_URL,
        "provider": {
            "@type": "Organization",
            "name": "SecAI Radar",
            "url": BASE_URL,
        },
        "version": METHODOLOGY_VERSION,
        "endpoints": {
            "mcpRankings": {
                "url": f"{BASE_URL}/api/v1/public/mcp/rankings",
                "method": "GET",
                "parameters": {
                    "page": "int (default 1)",
                    "pageSize": "int (1-100, default 20)",
                    "q": "string (search query)",
                    "category": "string (filter by category)",
                    "tier": "A|B|C|D",
                    "sort": "trustScore|evidenceConfidence|lastAssessedAt",
                },
                "responseFormat": "application/json",
            },
            "agentRankings": {
                "url": f"{BASE_URL}/api/v1/public/agents/rankings",
                "method": "GET",
                "parameters": {
                    "page": "int (default 1)",
                    "pageSize": "int (1-100, default 20)",
                },
                "responseFormat": "application/json",
            },
            "mcpDetail": {
                "url": f"{BASE_URL}/api/v1/public/mcp/{{idOrSlug}}",
                "method": "GET",
                "responseFormat": "application/json",
            },
            "agentDetail": {
                "url": f"{BASE_URL}/api/v1/public/agents/{{idOrSlug}}",
                "method": "GET",
                "responseFormat": "application/json",
            },
        },
        "scoringMethodology": {
            "version": METHODOLOGY_VERSION,
            "domains": {
                "d1": "Authentication & Identity Verification",
                "d2": "Authorization & Scope Controls",
                "d3": "Data Protection & Hosting Custody",
                "d4": "Audit Trail & Observability",
                "d5": "Operational Security (GitHub popularity, maintenance recency)",
                "d6": "Compliance (SBOM, IR Policy, Vulnerability Disclosure, Code Signing)",
            },
            "scalePerDomain": "0.0 – 5.0",
            "compositeScale": "0.0 – 100.0",
            "tiers": {
                "A": "≥ 80 (High Trust)",
                "B": "≥ 60 (Moderate Trust)",
                "C": "≥ 40 (Low Trust)",
                "D": "< 40 (Insufficient Evidence)",
            },
        },
        "decayParameters": build_decay_parameters(),
        "generatedAt": now,
    })
