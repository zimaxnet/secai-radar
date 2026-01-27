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


def extract_from_full_server_json(obs: Dict[str, Any], field: str, default: Any = None) -> Any:
    """
    Extract field from _full_server_json with fallback to top-level.
    Handles nested paths like 'repository.url' or 'remotes[0].url'.
    """
    # First try top-level
    if field in obs and obs[field]:
        return obs[field]
    
    # Then try _full_server_json
    full_json = obs.get("_full_server_json")
    if not full_json or not isinstance(full_json, dict):
        return default
    
    # Handle simple field
    if field in full_json and full_json[field]:
        return full_json[field]
    
    # Handle nested paths (e.g., 'repository.url')
    if '.' in field:
        parts = field.split('.')
        value = full_json
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default
            if value is None:
                return default
        return value if value else default
    
    return default


def extract_metadata(obs: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Extract metadata from observation for storage in metadata_json.
    Includes: publisher, description, transport, package, source_provenance
    """
    metadata = {}
    full_json = obs.get("_full_server_json", {})
    
    # Extract publisher - try multiple sources
    publisher = (obs.get("publisher") or 
                 full_json.get("publisher") if isinstance(full_json, dict) else None)
    if publisher:
        metadata["publisher"] = publisher
    
    # Extract description
    description = (obs.get("description") or 
                  full_json.get("description") if isinstance(full_json, dict) else None)
    if description:
        metadata["description"] = description
    
    # Extract transport - from remotes[0].type or transport field
    transport = obs.get("transport")
    if not transport and isinstance(full_json, dict):
        remotes = full_json.get("remotes", [])
        if remotes and isinstance(remotes, list) and len(remotes) > 0:
            first_remote = remotes[0]
            if isinstance(first_remote, dict):
                transport = first_remote.get("type")
                if not transport and "transport" in first_remote:
                    transport_obj = first_remote["transport"]
                    if isinstance(transport_obj, dict):
                        transport = transport_obj.get("type")
    if transport:
        metadata["transport"] = transport
    
    # Extract package info
    package = obs.get("package")
    if not package and isinstance(full_json, dict):
        packages = full_json.get("packages", [])
        if packages and isinstance(packages, list) and len(packages) > 0:
            first_package = packages[0]
            if isinstance(first_package, dict):
                package = {
                    "registry": first_package.get("registryType") or first_package.get("registry"),
                    "type": first_package.get("type"),
                    "identifier": first_package.get("identifier"),
                    "version": first_package.get("version") or full_json.get("version"),
                }
    if package:
        metadata["package"] = package
    
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
    
    print(f"Processing {len(raw_observations)} observations...")

    for idx, obs in enumerate(raw_observations):
        # Extract name with fallback to _full_server_json
        name = (obs.get("name") or 
                obs.get("server_name") or 
                (obs.get("_full_server_json", {}).get("name") if isinstance(obs.get("_full_server_json"), dict) else None) or
                "Unknown")
        
        # Handle empty strings - treat as None
        if name == "":
            full_json = obs.get("_full_server_json", {})
            if isinstance(full_json, dict):
                name = full_json.get("name") or "Unknown"
            else:
                name = "Unknown"
        
        source = obs.get("source_url", "unknown")
        
        # Extract repo_url with fallback to _full_server_json
        repo_url = (obs.get("repo_url") or 
                   obs.get("repository") or
                   extract_from_full_server_json(obs, "repo_url"))
        
        # If repo_url is a dict (from _full_server_json.repository), extract url
        if isinstance(repo_url, dict):
            repo_url = repo_url.get("url")
        
        # Extract endpoint from remotes[0].url if not in top-level
        endpoint = (obs.get("endpoint") or 
                   obs.get("url"))
        if not endpoint:
            full_json = obs.get("_full_server_json", {})
            if isinstance(full_json, dict):
                remotes = full_json.get("remotes", [])
                if remotes and isinstance(remotes, list) and len(remotes) > 0:
                    first_remote = remotes[0]
                    if isinstance(first_remote, dict):
                        endpoint = first_remote.get("url")
        
        # Extract docs_url with fallback
        docs_url = (obs.get("docs_url") or 
                   obs.get("documentation") or
                   extract_from_full_server_json(obs, "docs_url"))
        
        # Log extraction for first few observations
        if idx < 5:
            print(f"  Observation {idx+1}: name={name}, repo_url={bool(repo_url)}, endpoint={bool(endpoint)}, docs_url={bool(docs_url)}")

        server_id = generate_server_id(repo_url, endpoint, docs_url, name, source)
        
        if idx < 5:
            print(f"    Generated server_id: {server_id}")

        with db.cursor() as cur:
            cur.execute("SELECT server_id FROM mcp_servers WHERE server_id = %s", (server_id,))
            if cur.fetchone():
                log.append(("duplicate", server_id, name))
                if idx < 10:
                    print(f"    Skipped: duplicate server_id {server_id}")
                continue
        if server_id in seen_ids:
            log.append(("ambiguous_same_batch", server_id, name))
            if idx < 10:
                print(f"    Skipped: ambiguous (same batch) server_id {server_id}")
            continue
        seen_ids.add(server_id)

        # Extract metadata and deployment_type
        metadata = extract_metadata(obs, source)
        deployment_type = extract_deployment_type(obs)
        
        if idx < 5:
            print(f"    Creating server: {name} (deployment: {deployment_type}, source: {metadata.get('source_provenance')})")

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
    
    print(f"Created {len(canonical_servers)} canonical servers from {len(raw_observations)} observations")
    if log:
        print(f"Skipped {len(log)} observations (duplicates/ambiguous)")
    
    return canonical_servers


def get_or_create_provider(db, publisher: Optional[str], metadata: Dict[str, Any]) -> str:
    """
    Get or create provider from publisher information.
    Returns provider_id (defaults to Unknown provider if publisher not available).
    """
    if not publisher:
        # Return default Unknown provider
        return "0000000000000000"
    
    # Try to extract domain from metadata or publisher string
    primary_domain = "unknown.local"
    
    # Try to extract domain from publisher (might be email or domain)
    if "@" in publisher:
        # Email format: extract domain
        primary_domain = publisher.split("@")[-1]
    elif "." in publisher and not publisher.startswith("http"):
        # Might be a domain
        primary_domain = publisher
    else:
        # Use publisher name as domain fallback (normalized)
        primary_domain = f"{normalize_name(publisher)}.local"
    
    # Generate provider ID
    provider_id = generate_provider_id(publisher, primary_domain)
    
    # Get or create provider
    with db.cursor() as cur:
        cur.execute("""
            SELECT provider_id FROM providers WHERE provider_id = %s
        """, (provider_id,))
        if cur.fetchone():
            return provider_id
        
        # Create new provider
        cur.execute("""
            INSERT INTO providers (provider_id, provider_name, primary_domain, provider_type)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (provider_id) DO NOTHING
        """, (provider_id, publisher, primary_domain, "Community"))
        db.commit()
    
    return provider_id


def store_canonical_servers(db, servers: List[Dict[str, Any]], default_provider_id: str):
    """Store canonical server records. Creates providers from publisher info when available."""
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
            metadata = server.get("metadata", {})
            
            # Get or create provider from publisher
            publisher = metadata.get("publisher")
            provider_id = get_or_create_provider(db, publisher, metadata) if publisher else default_provider_id
            
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
                    provider_id,  # Use proper provider_id
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
                    provider_id,  # Use proper provider_id
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
