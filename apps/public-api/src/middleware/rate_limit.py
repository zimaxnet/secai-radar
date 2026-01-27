"""
Public rate limiting (T-130). Thresholds per docs/implementation/RATE-LIMITING-AND-WAF.md.
In-memory per-IP, per-endpoint-group. Optional: block empty User-Agent.
"""

import time
from typing import Tuple

from fastapi import Request
from fastapi.responses import JSONResponse


# Limits per IP per minute (req/min)
LIMIT_FEED = 10
LIMIT_HEALTH = 20
LIMIT_HEALTH_STATUS = 20
LIMIT_HEAVY = 50   # search / rankings
LIMIT_GENERAL = 100

WINDOW_SEC = 60
RETRY_AFTER_SEC = 60

# (ip, group) -> (count, window_start_ts)
_store: dict[Tuple[str, str], Tuple[int, float]] = {}
# Optional: set to True to block requests with no User-Agent
REJECT_EMPTY_USER_AGENT = False


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


def _limit_group(path: str) -> str:
    if "/feed.xml" in path or "/feed.json" in path or path.rstrip("/").endswith("feed.xml") or path.rstrip("/").endswith("feed.json"):
        return "feed"
    if path == "/health" or path == "/api/v1/public/health" or path == "/api/v1/public/status":
        return "health"
    if "/rankings" in path or "rankings" in (path.split("/") or [])[-1]:
        return "heavy"
    return "general"


def _limit_for_group(group: str) -> int:
    if group == "feed":
        return LIMIT_FEED
    if group == "health":
        return LIMIT_HEALTH
    if group == "heavy":
        return LIMIT_HEAVY
    return LIMIT_GENERAL


def _check_and_inc(ip: str, group: str) -> Tuple[bool, int]:
    """Returns (allowed, retry_after_sec)."""
    now = time.time()
    key = (ip, group)
    if key in _store:
        count, start = _store[key]
        if now - start >= WINDOW_SEC:
            _store[key] = (1, now)
            return True, RETRY_AFTER_SEC
        count += 1
        _store[key] = (count, start)
        limit = _limit_for_group(group)
        if count > limit:
            return False, max(1, int(start + WINDOW_SEC - now))
        return True, RETRY_AFTER_SEC
    _store[key] = (1, now)
    return True, RETRY_AFTER_SEC


def _cleanup_old():
    """Drop expired windows to avoid unbounded growth."""
    now = time.time()
    to_del = [k for k, (_, start) in _store.items() if now - start >= WINDOW_SEC]
    for k in to_del:
        del _store[k]


async def rate_limit_middleware(request: Request, call_next):
    """Enforce per-IP, per-endpoint-group rate limits and optional User-Agent check."""
    if REJECT_EMPTY_USER_AGENT:
        ua = request.headers.get("User-Agent") or ""
        if not ua.strip():
            return JSONResponse(
                status_code=400,
                content={"detail": "User-Agent required"},
            )
    path = request.url.path or ""
    ip = _client_ip(request)
    group = _limit_group(path)
    _cleanup_old()
    allowed, retry = _check_and_inc(ip, group)  # type: ignore
    allowed, retry = _check_and_inc(ip, group)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers={"Retry-After": str(retry)},
        )
    return await call_next(request)
