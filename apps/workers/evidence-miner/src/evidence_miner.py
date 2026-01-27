"""
Evidence Miner Worker (T-072) - Basic docs/repo extraction.
Captures Docs/Repo evidence when available; extracts AuthModel, HostingCustody, ToolAgency.
Stores evidence_items and evidence_claims with sourceEvidenceId (evidence_id) and capturedAt.
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import requests

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar",
)
PARSER_VERSION = "evidence-miner-1.0"
# Minimum claim types per T-072
CLAIM_TYPES = ("AuthModel", "HostingCustody", "ToolAgency")


def _hash16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _content_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _fetch_url(url: str) -> Tuple[Optional[bytes], Optional[str]]:
    """Fetch URL; return (body, error)."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return (r.content, None)
    except Exception as e:
        return (None, str(e))


def _extract_claims(source_url: str, content: bytes, evidence_type: str) -> List[Dict[str, Any]]:
    """
    Extract minimum claims: AuthModel, HostingCustody (if present), ToolAgency hints.
    Returns list of {claim_type, value_json, confidence}.
    """
    text = (content[:20000] or b"").decode("utf-8", errors="replace").lower()
    url_lower = source_url.lower()
    claims: List[Dict[str, Any]] = []

    # AuthModel
    if re.search(r"oauth|oidc|openid", text) or "oauth" in url_lower:
        claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "OAuthOIDC"}), "confidence": 2})
    elif re.search(r"api[_-]?key|apikey", text):
        claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "APIKey"}), "confidence": 2})
    elif re.search(r"pat|personal access token", text):
        claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "PAT"}), "confidence": 2})
    elif re.search(r"mtls|mTLS|mutual TLS", text):
        claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "mTLS"}), "confidence": 2})
    else:
        claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "Unknown"}), "confidence": 1})

    # HostingCustody (if present)
    if "github.com" in url_lower or "github.com" in text:
        claims.append({
            "claim_type": "HostingCustody",
            "value_json": json.dumps({"value": "third_party", "hint": "github"}),
            "confidence": 2,
        })
    elif re.search(r"self[- ]?host|on[- ]?prem|enterprise", text):
        claims.append({
            "claim_type": "HostingCustody",
            "value_json": json.dumps({"value": "customer_controlled", "hint": "self-host"}),
            "confidence": 2,
        })

    # ToolAgency hints (stored as ToolCapabilities per schema)
    if re.search(r"read[- ]?only|readonly", text):
        claims.append({"claim_type": "ToolCapabilities", "value_json": json.dumps({"value": "ReadOnly"}), "confidence": 2})
    elif re.search(r"read[- ]?write|readwrite|read/write", text):
        claims.append({"claim_type": "ToolCapabilities", "value_json": json.dumps({"value": "ReadWrite"}), "confidence": 2})
    elif re.search(r"destructive|delete|write.*storage", text):
        claims.append({
            "claim_type": "ToolCapabilities",
            "value_json": json.dumps({"value": "DestructivePresent"}),
            "confidence": 2,
        })
    else:
        claims.append({"claim_type": "ToolCapabilities", "value_json": json.dumps({"value": "Unknown"}), "confidence": 1})

    return claims


def _already_has_evidence(cur, server_id: str, source_url: str) -> bool:
    cur.execute(
        "SELECT 1 FROM evidence_items WHERE server_id = %s AND source_url = %s LIMIT 1",
        (server_id, source_url),
    )
    return cur.fetchone() is not None


def _ensure_evidence_and_claims(
    cur,
    server_id: str,
    evidence_type: str,
    source_url: str,
    content: bytes,
    now: datetime,
) -> Optional[str]:
    """
    Insert evidence_items and evidence_claims. Returns evidence_id or None on skip/error.
    """
    content_hash = _content_hash(content)
    evidence_id = _hash16(f"{server_id}|{source_url}|{content_hash}")
    try:
        cur.execute(
            """
            INSERT INTO evidence_items (
                evidence_id, server_id, type, url, captured_at, confidence, content_hash, source_url, parser_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (evidence_id) DO NOTHING
            """,
            (
                evidence_id,
                server_id,
                evidence_type,
                source_url,
                now,
                2,
                content_hash,
                source_url,
                PARSER_VERSION,
            ),
        )
        if cur.rowcount == 0:
            return None  # already existed
    except Exception:
        return None

    for c in _extract_claims(source_url, content, evidence_type):
        claim_id = _hash16(f"{evidence_id}|{c['claim_type']}")
        cur.execute(
            """
            INSERT INTO evidence_claims (claim_id, evidence_id, claim_type, value_json, confidence, source_url, captured_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (claim_id) DO NOTHING
            """,
            (
                claim_id,
                evidence_id,
                c["claim_type"],
                c["value_json"],
                c["confidence"],
                source_url,
                now,
            ),
        )
    return evidence_id


def run_evidence_miner() -> Dict[str, Any]:
    conn = psycopg2.connect(DATABASE_URL)
    now = datetime.now(timezone.utc)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT server_id, server_name, repo_url, docs_url
                FROM mcp_servers
                WHERE repo_url IS NOT NULL OR docs_url IS NOT NULL
                """
            )
            servers = cur.fetchall()
        evidence_created = 0
        errors: List[str] = []
        for row in servers:
            server_id, server_name, repo_url, docs_url = row
            for label, url in [("Docs", docs_url), ("Repo", repo_url)]:
                if not url or not url.strip():
                    continue
                with conn.cursor() as cur:
                    if _already_has_evidence(cur, server_id, url):
                        continue
                body, err = _fetch_url(url)
                if err:
                    errors.append(f"{server_id} {label} {url}: {err}")
                    continue
                if not body:
                    continue
                with conn.cursor() as cur:
                    eid = _ensure_evidence_and_claims(cur, server_id, label, url, body, now)
                    if eid:
                        evidence_created += 1
        conn.commit()
        return {
            "success": True,
            "evidenceItemsCreated": evidence_created,
            "serversProcessed": len(servers),
            "errors": errors[:20],
            "completedAt": now.isoformat(),
        }
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "error": str(e),
            "completedAt": now.isoformat(),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = run_evidence_miner()
    print(json.dumps(result, indent=2))
