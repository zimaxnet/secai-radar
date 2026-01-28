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
from urllib.parse import urlparse

import psycopg2
import requests

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar",
)
PARSER_VERSION = "evidence-miner-2.0"
# Claim types supported
CLAIM_TYPES = (
    "AuthModel", "HostingCustody", "ToolAgency", "ToolCapabilities", "ToolList",
    "TokenTTL", "Scopes", "AuditLogging", "DataRetention", "DataDeletion", 
    "Residency", "Encryption", "SBOM", "Signing", "VulnDisclosure", "IRPolicy"
)


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


def _extract_github_repo_info(repo_url: str) -> Optional[Tuple[str, str]]:
    """
    Extract owner and repo from GitHub URL.
    Returns (owner, repo) or None if not a GitHub URL.
    """
    if not repo_url:
        return None
    
    # Handle various GitHub URL formats
    patterns = [
        r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$",
        r"git@github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, repo_url.lower())
        if match:
            return (match.group(1), match.group(2).rstrip('/'))
    
    return None


def _fetch_github_popularity(owner: str, repo: str) -> Optional[Dict[str, Any]]:
    """
    Fetch GitHub repository popularity signals.
    Returns dict with stars, forks, watchers, updated_at, or None on error.
    """
    # GitHub API: GET /repos/{owner}/{repo}
    # No auth required for public repos (rate limit: 60/hour per IP)
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        # Use Accept header for GitHub API v3
        headers = {"Accept": "application/vnd.github.v3+json"}
        r = requests.get(api_url, headers=headers, timeout=10)
        
        if r.status_code == 404:
            return None  # Repo not found or private
        r.raise_for_status()
        
        data = r.json()
        return {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "watchers": data.get("watchers_count", 0),
            "updated_at": data.get("updated_at"),
            "created_at": data.get("created_at"),
            "language": data.get("language"),
            "open_issues": data.get("open_issues_count", 0),
        }
    except Exception as e:
        print(f"Error fetching GitHub popularity for {owner}/{repo}: {e}")
        return None


def _update_server_popularity_signals(db, server_id: str, signals: Dict[str, Any]) -> None:
    """
    Update popularity signals in server's metadata_json.
    Merges new signals with existing metadata.
    """
    with db.cursor() as cur:
        # Get current metadata
        cur.execute("""
            SELECT metadata_json
            FROM mcp_servers
            WHERE server_id = %s
        """, (server_id,))
        row = cur.fetchone()
        
        # metadata_json from PostgreSQL JSONB is already a dict, not a string
        if row and row[0]:
            if isinstance(row[0], str):
                current_metadata = json.loads(row[0])
            else:
                current_metadata = row[0]  # Already a dict
        else:
            current_metadata = {}
        
        # Merge popularity signals
        if "popularity_signals" not in current_metadata:
            current_metadata["popularity_signals"] = {}
        
        current_metadata["popularity_signals"].update(signals)
        current_metadata["popularity_signals"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Update metadata_json
        cur.execute("""
            UPDATE mcp_servers
            SET metadata_json = %s
            WHERE server_id = %s
        """, (json.dumps(current_metadata), server_id))
        db.commit()


def _extract_claims_from_server_json(server_json: Dict[str, Any], source_url: str) -> List[Dict[str, Any]]:
    """
    Extract claims from Official Registry server.json format.
    Returns list of {claim_type, value_json, confidence}.
    """
    claims: List[Dict[str, Any]] = []
    
    # Auth hints from server.json
    auth = server_json.get("auth")
    if auth:
        if isinstance(auth, dict):
            auth_type = auth.get("type", "").lower()
            if "oauth" in auth_type or "oidc" in auth_type:
                claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "OAuthOIDC"}), "confidence": 3})
            elif "api" in auth_type and "key" in auth_type:
                claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "APIKey"}), "confidence": 3})
            elif "pat" in auth_type or "token" in auth_type:
                claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "PAT"}), "confidence": 3})
            elif "mtls" in auth_type or "mTLS" in auth_type:
                claims.append({"claim_type": "AuthModel", "value_json": json.dumps({"value": "mTLS"}), "confidence": 3})
            
            # TokenTTL and Scopes
            if "ttl" in auth or "expires" in auth or "lifetime" in auth:
                ttl_value = auth.get("ttl") or auth.get("expires") or auth.get("lifetime")
                claims.append({"claim_type": "TokenTTL", "value_json": json.dumps({"value": str(ttl_value)}), "confidence": 3})
            if "scopes" in auth:
                scopes = auth.get("scopes", [])
                claims.append({"claim_type": "Scopes", "value_json": json.dumps({"value": scopes}), "confidence": 3})
    
    # ToolList and ToolCapabilities from capabilities
    capabilities = server_json.get("capabilities")
    if capabilities:
        if isinstance(capabilities, dict):
            tools = capabilities.get("tools")
            if tools and isinstance(tools, list):
                tool_names = [t.get("name", "") if isinstance(t, dict) else str(t) for t in tools]
                claims.append({"claim_type": "ToolList", "value_json": json.dumps({"value": tool_names}), "confidence": 3})
    
    # Remotes[] and packages[] for deployment info
    remotes = server_json.get("remotes", [])
    packages = server_json.get("packages", [])
    if remotes:
        claims.append({
            "claim_type": "HostingCustody",
            "value_json": json.dumps({"value": "remote", "remotes": len(remotes)}),
            "confidence": 3,
        })
    
    return claims


def _extract_claims(source_url: str, content: bytes, evidence_type: str) -> List[Dict[str, Any]]:
    """
    Extract claims from docs/repo content.
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

    # HostingCustody
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

    # ToolCapabilities
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

    # Additional claim types
    # TokenTTL
    ttl_match = re.search(r"token.*ttl|ttl.*token|expires.*(\d+)|lifetime.*(\d+)", text)
    if ttl_match:
        ttl_value = ttl_match.group(1) or ttl_match.group(2) or "unknown"
        claims.append({"claim_type": "TokenTTL", "value_json": json.dumps({"value": ttl_value}), "confidence": 2})
    
    # Scopes
    if re.search(r"scope|permission|access.*control", text):
        # Extract scope-like patterns
        scope_matches = re.findall(r"scope[:\s]+([a-z_]+)", text)
        if scope_matches:
            claims.append({"claim_type": "Scopes", "value_json": json.dumps({"value": scope_matches[:10]}), "confidence": 2})
    
    # AuditLogging
    if re.search(r"audit|log.*access|access.*log", text):
        claims.append({"claim_type": "AuditLogging", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # DataRetention
    if re.search(r"retention|data.*retain|keep.*data", text):
        claims.append({"claim_type": "DataRetention", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # DataDeletion
    if re.search(r"delete.*data|data.*delete|remove.*data", text):
        claims.append({"claim_type": "DataDeletion", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # Residency
    if re.search(r"residency|data.*location|geographic", text):
        claims.append({"claim_type": "Residency", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # Encryption
    if re.search(r"encrypt|tls|ssl|cipher", text):
        claims.append({"claim_type": "Encryption", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # SBOM
    if re.search(r"sbom|software.*bill|bom", text):
        claims.append({"claim_type": "SBOM", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # Signing
    if re.search(r"sign|signature|signed", text):
        claims.append({"claim_type": "Signing", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # VulnDisclosure
    if re.search(r"vulnerability|security.*advisory|disclosure", text):
        claims.append({"claim_type": "VulnDisclosure", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})
    
    # IRPolicy
    if re.search(r"incident.*response|ir.*policy|security.*incident", text):
        claims.append({"claim_type": "IRPolicy", "value_json": json.dumps({"value": "mentioned"}), "confidence": 2})

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


def _extract_from_server_json(cur, server_id: str, server_json: Dict[str, Any], now: datetime) -> Optional[str]:
    """
    Extract evidence from server.json stored in raw_observations.
    Creates Config-type evidence item with claims from server.json.
    """
    source_url = "registry://server.json"  # Virtual source URL
    content_str = json.dumps(server_json, sort_keys=True)
    content_hash = _content_hash(content_str.encode())
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
                "Config",
                source_url,
                now,
                3,  # High confidence for official registry data
                content_hash,
                source_url,
                PARSER_VERSION,
            ),
        )
        if cur.rowcount == 0:
            return None  # already existed
        
        # Extract claims from server.json
        claims = _extract_claims_from_server_json(server_json, source_url)
        for c in claims:
            claim_id = _hash16(f"{evidence_id}|{c['claim_type']}")
            cur.execute(
                """
                INSERT INTO evidence_claims (claim_id, evidence_id, claim_type, value_json, confidence, source_url, captured_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (claim_id) DO UPDATE SET
                    value_json = EXCLUDED.value_json,
                    confidence = EXCLUDED.confidence
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
    except Exception as e:
        print(f"Error extracting from server.json for {server_id}: {e}")
        return None


def run_evidence_miner() -> Dict[str, Any]:
    conn = psycopg2.connect(DATABASE_URL)
    now = datetime.now(timezone.utc)
    try:
        # First, extract from server.json in raw_observations (Official Registry)
        # Match servers to raw_observations by checking metadata_json source_provenance
        with conn.cursor() as cur:
            # Get servers from Official Registry
            cur.execute("""
                SELECT server_id, server_name, repo_url, metadata_json
                FROM mcp_servers
                WHERE metadata_json->>'source_provenance' = 'Official Registry'
                OR (metadata_json IS NULL AND repo_url IS NOT NULL)
            """)
            registry_servers = cur.fetchall()
        
        evidence_from_json = 0
        popularity_signals_from_registry = 0
        
        print(f"Found {len(registry_servers)} servers from Official Registry")
        
        # First pass: Collect popularity signals from GitHub for registry servers
        for row in registry_servers:
            if len(row) < 4:
                continue
            server_id, server_name, repo_url, metadata_json_str = row[0], row[1], row[2], row[3]
            
            # Collect popularity signals from GitHub if repo_url available
            if repo_url:
                repo_info = _extract_github_repo_info(repo_url)
                if repo_info:
                    owner, repo = repo_info
                    # Check if we already have recent popularity signals
                    # metadata_json from PostgreSQL JSONB is already a dict, not a string
                    if metadata_json_str is None:
                        metadata = {}
                    elif isinstance(metadata_json_str, str):
                        metadata = json.loads(metadata_json_str)
                    else:
                        metadata = metadata_json_str  # Already a dict
                    popularity = metadata.get("popularity_signals", {})
                    last_updated = popularity.get("last_updated")
                    
                    should_fetch = True
                    if last_updated:
                        try:
                            last_update_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                            hours_old = (now - last_update_dt.replace(tzinfo=timezone.utc)).total_seconds() / 3600
                            if hours_old < 24:
                                should_fetch = False
                        except:
                            pass
                    
                    if should_fetch:
                        github_signals = _fetch_github_popularity(owner, repo)
                        if github_signals:
                            _update_server_popularity_signals(conn, server_id, {"github": github_signals})
                            popularity_signals_from_registry += 1
        
        # Second pass: Extract evidence from server.json
        for row in registry_servers:
            if len(row) < 4:
                continue
            server_id, server_name, repo_url, metadata_json_str = row[0], row[1], row[2], row[3]
            try:
                # Find matching raw_observation with _full_server_json
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT content_json
                        FROM raw_observations
                        WHERE source_url LIKE '%registry.modelcontextprotocol.io%'
                        AND processed_at IS NOT NULL
                        AND content_json::jsonb ? '_full_server_json'
                        AND (
                            content_json::jsonb->>'name' = %s
                            OR content_json::jsonb->>'repo_url' = %s
                            OR (content_json::jsonb->>'_full_server_json')::jsonb->>'name' = %s
                        )
                        LIMIT 1
                    """, (server_name, repo_url, server_name))
                    row = cur.fetchone()
                    if not row:
                        continue
                    
                    content_json = json.loads(row[0])
                    full_server_json = content_json.get("_full_server_json")
                    if full_server_json:
                        eid = _extract_from_server_json(cur, server_id, full_server_json, now)
                        if eid:
                            evidence_from_json += 1
                            print(f"  Extracted evidence from server.json for {server_name} (server_id: {server_id})")
                        else:
                            print(f"  Skipped {server_name}: evidence already exists or error")
                    else:
                        print(f"  No _full_server_json found for {server_name}")
            except Exception as e:
                print(f"Error processing server.json for {server_id}: {e}")
        
        # Then, extract from docs/repo URLs and collect popularity signals
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT server_id, server_name, repo_url, docs_url, metadata_json
                FROM mcp_servers
                WHERE repo_url IS NOT NULL OR docs_url IS NOT NULL
                """
            )
            servers = cur.fetchall()
        evidence_created = 0
        popularity_signals_collected = 0
        errors: List[str] = []
        for row in servers:
            server_id, server_name, repo_url, docs_url, metadata_json_str = row
            
            # Collect popularity signals from GitHub (if repo_url is GitHub)
            if repo_url:
                repo_info = _extract_github_repo_info(repo_url)
                if repo_info:
                    owner, repo = repo_info
                    # Check if we already have recent popularity signals (avoid rate limits)
                    # metadata_json from PostgreSQL JSONB is already a dict, not a string
                    if metadata_json_str is None:
                        metadata = {}
                    elif isinstance(metadata_json_str, str):
                        metadata = json.loads(metadata_json_str)
                    else:
                        metadata = metadata_json_str  # Already a dict
                    popularity = metadata.get("popularity_signals", {})
                    last_updated = popularity.get("last_updated")
                    
                    # Only fetch if we don't have recent data (older than 24 hours)
                    should_fetch = True
                    if last_updated:
                        try:
                            last_update_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                            hours_old = (now - last_update_dt.replace(tzinfo=timezone.utc)).total_seconds() / 3600
                            if hours_old < 24:
                                should_fetch = False
                        except:
                            pass
                    
                    if should_fetch:
                        github_signals = _fetch_github_popularity(owner, repo)
                        if github_signals:
                            _update_server_popularity_signals(conn, server_id, {"github": github_signals})
                            popularity_signals_collected += 1
            
            # Extract evidence from docs/repo URLs
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
            "evidenceItemsCreated": evidence_created + evidence_from_json,
            "evidenceFromServerJson": evidence_from_json,
            "evidenceFromUrls": evidence_created,
            "popularitySignalsCollected": popularity_signals_collected + popularity_signals_from_registry,
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
