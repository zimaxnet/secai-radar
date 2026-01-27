"""
Curator Worker - Normalizer + Canonicalizer
Resolves duplicates and creates stable IDs
"""

import os
import psycopg2
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import json

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def normalize_name(name: str) -> str:
    """Normalize provider/server name"""
    # Remove common prefixes/suffixes, lowercase, strip
    normalized = name.lower().strip()
    normalized = re.sub(r'[^a-z0-9\s-]', '', normalized)
    normalized = re.sub(r'\s+', '-', normalized)
    return normalized


def normalize_url(url: str) -> Optional[str]:
    """Normalize URL (remove tracking params, normalize scheme)"""
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        # Remove common tracking params
        # Keep only essential parts
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return normalized.rstrip('/')
    except:
        return None


def generate_provider_id(legal_name: str, primary_domain: str) -> str:
    """Generate canonical provider ID"""
    normalized = f"{normalize_name(legal_name)}|{normalize_url(primary_domain) or ''}"
    hash_val = int(hashlib.sha256(normalized.encode()).hexdigest()[:16], 16)
    return format(hash_val, '016x')


def generate_server_id(repo_url: Optional[str], endpoint: Optional[str], docs_url: Optional[str], name: str, source: str) -> str:
    """
    Generate canonical server ID with precedence (T-071):
    repoUrl > endpoint host > docs URL > name+source
    """
    if repo_url:
        normalized = normalize_url(repo_url) or ""
    elif endpoint:
        parsed = urlparse(endpoint)
        normalized = parsed.netloc or ""
    elif docs_url:
        normalized = normalize_url(docs_url) or ""
    else:
        normalized = f"{normalize_name(name)}|{source}"
    hash_val = int(hashlib.sha256(normalized.encode()).hexdigest()[:16], 16)
    return format(hash_val, '016x')


def extract_deployment_type(obs: Dict[str, Any]) -> str:
    """
    Determine deployment_type from observation.
    Checks for remotes[] and packages[] in _full_server_json or direct fields.
    """
    # Check if we have full server.json
    full_server_json = obs.get("_full_server_json")
    if full_server_json:
        has_remotes = bool(full_server_json.get("remotes"))
        has_packages = bool(full_server_json.get("packages"))
        if has_remotes and has_packages:
            return "Hybrid"
        elif has_remotes:
            return "Remote"
        elif has_packages:
            return "Local"
    
    # Fallback: check endpoint and package fields
    has_endpoint = bool(obs.get("endpoint") or obs.get("url"))
    has_package = bool(obs.get("package"))
    if has_endpoint and has_package:
        return "Hybrid"
    elif has_endpoint:
        return "Remote"
    elif has_package:
        return "Local"
    
    return "Unknown"


def extract_metadata(obs: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Extract metadata from observation for storage in metadata_json.
    Includes: publisher, description, transport, package, source_provenance
    """
    metadata = {}
    
    # Extract from observation fields
    if obs.get("publisher"):
        metadata["publisher"] = obs["publisher"]
    if obs.get("description"):
        metadata["description"] = obs["description"]
    if obs.get("transport"):
        metadata["transport"] = obs["transport"]
    if obs.get("package"):
        metadata["package"] = obs["package"]
    
    # Determine source_provenance
    source_lower = source.lower()
    if "registry.modelcontextprotocol.io" in source_lower:
        metadata["source_provenance"] = "Official Registry"
    elif "mcpanvil.com" in source_lower or "mcpanvil" in source_lower:
        metadata["source_provenance"] = "MCPAnvil"
    else:
        metadata["source_provenance"] = "Other"
    
    # Store full server.json reference if available (for evidence extraction)
    if obs.get("_full_server_json"):
        metadata["_full_server_json"] = obs["_full_server_json"]
    
    return metadata


def dedupe_servers(
    db, raw_observations: List[Dict[str, Any]], review_log: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]:
    """
    Deduplicate servers using heuristics. ID precedence: repoUrl > endpoint host > docs URL > name+source.
    Logs to review_log when skipping (duplicate or ambiguous) for T-071 acceptance.
    """
    log = review_log if review_log is not None else []
    canonical_servers = []
    seen_ids = set()

    for obs in raw_observations:
        repo_url = obs.get("repo_url") or obs.get("repository")
        endpoint = obs.get("endpoint") or obs.get("url")
        docs_url = obs.get("docs_url") or obs.get("documentation")
        name = obs.get("name") or obs.get("server_name", "Unknown")
        source = obs.get("source_url", "unknown")

        server_id = generate_server_id(repo_url, endpoint, docs_url, name, source)

        with db.cursor() as cur:
            cur.execute("SELECT server_id FROM mcp_servers WHERE server_id = %s", (server_id,))
            if cur.fetchone():
                log.append(("duplicate", server_id, name))
                continue
        if server_id in seen_ids:
            log.append(("ambiguous_same_batch", server_id, name))
            continue
        seen_ids.add(server_id)

        # Extract metadata and deployment_type
        metadata = extract_metadata(obs, source)
        deployment_type = extract_deployment_type(obs)

        canonical_servers.append({
            "server_id": server_id,
            "server_name": name,
            "server_slug": normalize_name(name),
            "repo_url": repo_url,
            "docs_url": docs_url,
            "source": source,
            "deployment_type": deployment_type,
            "metadata": metadata,
        })
    return canonical_servers


def store_canonical_servers(db, servers: List[Dict[str, Any]], provider_id: str):
    """Store canonical server records. Required mcp_servers columns use Unknown defaults."""
    with db.cursor() as cur:
        # Check if metadata_json column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'mcp_servers' AND column_name = 'metadata_json'
        """)
        has_metadata_json = cur.fetchone() is not None
        
        for server in servers:
            metadata_json = json.dumps(server.get("metadata", {}))
            deployment_type = server.get("deployment_type", "Unknown")
            
            if has_metadata_json:
                cur.execute("""
                    INSERT INTO mcp_servers (
                        server_id, server_slug, server_name, provider_id,
                        deployment_type, auth_model, tool_agency,
                        repo_url, docs_url, metadata_json, first_seen_at, last_seen_at
                    ) VALUES (%s, %s, %s, %s, %s, 'Unknown', 'Unknown', %s, %s, %s, %s, %s)
                    ON CONFLICT (server_id)
                    DO UPDATE SET
                        last_seen_at = EXCLUDED.last_seen_at,
                        deployment_type = COALESCE(EXCLUDED.deployment_type, mcp_servers.deployment_type),
                        repo_url = COALESCE(EXCLUDED.repo_url, mcp_servers.repo_url),
                        docs_url = COALESCE(EXCLUDED.docs_url, mcp_servers.docs_url),
                        metadata_json = CASE 
                            WHEN EXCLUDED.metadata_json != '{}'::jsonb 
                            THEN EXCLUDED.metadata_json 
                            ELSE mcp_servers.metadata_json 
                        END
                """, (
                    server["server_id"],
                    server["server_slug"],
                    server["server_name"],
                    provider_id,
                    deployment_type,
                    server.get("repo_url"),
                    server.get("docs_url"),
                    metadata_json,
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
            else:
                # Fallback for databases without metadata_json column
                cur.execute("""
                    INSERT INTO mcp_servers (
                        server_id, server_slug, server_name, provider_id,
                        deployment_type, auth_model, tool_agency,
                        repo_url, docs_url, first_seen_at, last_seen_at
                    ) VALUES (%s, %s, %s, %s, %s, 'Unknown', 'Unknown', %s, %s, %s, %s)
                    ON CONFLICT (server_id)
                    DO UPDATE SET
                        last_seen_at = EXCLUDED.last_seen_at,
                        deployment_type = COALESCE(EXCLUDED.deployment_type, mcp_servers.deployment_type),
                        repo_url = COALESCE(EXCLUDED.repo_url, mcp_servers.repo_url),
                        docs_url = COALESCE(EXCLUDED.docs_url, mcp_servers.docs_url)
                """, (
                    server["server_id"],
                    server["server_slug"],
                    server["server_name"],
                    provider_id,
                    deployment_type,
                    server.get("repo_url"),
                    server.get("docs_url"),
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
        db.commit()


def run_curator():
    """
    Main curator function - process raw observations and create canonical records
    """
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        # Get unprocessed raw observations
        with conn.cursor() as cur:
            cur.execute("""
                SELECT observation_id, source_url, content_json, retrieved_at
                FROM raw_observations
                WHERE processed_at IS NULL
                ORDER BY retrieved_at ASC
                LIMIT 1000
            """)
            raw_obs = cur.fetchall()
        
        if not raw_obs:
            return {
                "success": True,
                "message": "No new observations to process",
                "processedAt": datetime.utcnow().isoformat()
            }
        
        # Parse observations and attach source_url (column, not in content_json)
        observations = [dict(json.loads(obs[2]), source_url=obs[1]) for obs in raw_obs]
        
        # Ensure default provider exists for canonical records
        default_provider_id = "0000000000000000"
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO providers (provider_id, provider_name, primary_domain, provider_type)
                VALUES (%s, 'Unknown', 'unknown.local', 'Community')
                ON CONFLICT (provider_id) DO NOTHING
            """, (default_provider_id,))
            conn.commit()
        
        review_log: List[tuple] = []
        canonical_servers = dedupe_servers(conn, observations, review_log)
        if review_log:
            print("Review queue:", [{"reason": r[0], "server_id": r[1], "name": r[2]} for r in review_log])

        store_canonical_servers(conn, canonical_servers, default_provider_id)

        with conn.cursor() as cur:
            obs_ids = [obs[0] for obs in raw_obs]
            cur.execute("""
                UPDATE raw_observations
                SET processed_at = %s
                WHERE observation_id = ANY(%s)
            """, (datetime.utcnow(), obs_ids))
            conn.commit()

        out: Dict[str, Any] = {
            "success": True,
            "observationsProcessed": len(raw_obs),
            "canonicalServersCreated": len(canonical_servers),
            "processedAt": datetime.utcnow().isoformat(),
        }
        if review_log:
            out["reviewQueueCount"] = len(review_log)
        return out
    except Exception as e:
        conn.rollback()
        print(f"Curator error: {e}")
        return {
            "success": False,
            "error": str(e),
            "processedAt": datetime.utcnow().isoformat()
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = run_curator()
    print(json.dumps(result, indent=2))
