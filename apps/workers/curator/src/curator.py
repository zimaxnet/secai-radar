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


async def generate_provider_id(legal_name: str, primary_domain: str) -> str:
    """Generate canonical provider ID"""
    normalized = f"{normalize_name(legal_name)}|{normalize_url(primary_domain) or ''}"
    # Use simple hash for MVP (port from TypeScript)
    hash_val = int(hashlib.sha256(normalized.encode()).hexdigest()[:16], 16)
    return format(hash_val, '016x')


async def generate_server_id(repo_url: Optional[str], endpoint: Optional[str], docs_url: Optional[str], name: str, source: str) -> str:
    """
    Generate canonical server ID with precedence:
    repoUrl > endpoint host > docs URL > name+source
    """
    # Precedence order
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


def dedupe_servers(db, raw_observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate servers using heuristics
    
    Returns:
        List of canonical server records
    """
    canonical_servers = []
    
    for obs in raw_observations:
        # Extract server info
        repo_url = obs.get('repo_url') or obs.get('repository')
        endpoint = obs.get('endpoint') or obs.get('url')
        docs_url = obs.get('docs_url') or obs.get('documentation')
        name = obs.get('name') or obs.get('server_name', 'Unknown')
        source = obs.get('source_url', 'unknown')
        
        # Generate canonical ID
        server_id = generate_server_id(repo_url, endpoint, docs_url, name, source)
        
        # Check if already exists
        with db.cursor() as cur:
            cur.execute("SELECT server_id FROM mcp_servers WHERE server_id = %s", (server_id,))
            if cur.fetchone():
                continue  # Already exists
        
        # Create canonical record
        canonical_servers.append({
            "server_id": server_id,
            "server_name": name,
            "server_slug": normalize_name(name),
            "repo_url": repo_url,
            "docs_url": docs_url,
            "source": source,
        })
    
    return canonical_servers


def store_canonical_servers(db, servers: List[Dict[str, Any]], provider_id: str):
    """Store canonical server records"""
    with db.cursor() as cur:
        for server in servers:
            cur.execute("""
                INSERT INTO mcp_servers (
                    server_id, server_slug, server_name, provider_id,
                    repo_url, docs_url, first_seen_at, last_seen_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (server_id) 
                DO UPDATE SET 
                    last_seen_at = EXCLUDED.last_seen_at,
                    repo_url = COALESCE(EXCLUDED.repo_url, mcp_servers.repo_url),
                    docs_url = COALESCE(EXCLUDED.docs_url, mcp_servers.docs_url)
            """, (
                server["server_id"],
                server["server_slug"],
                server["server_name"],
                provider_id,
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
        
        # Parse observations
        observations = [json.loads(obs[2]) for obs in raw_obs]
        
        # Deduplicate and canonicalize
        # For MVP, use a default provider_id
        default_provider_id = "0000000000000000"  # TODO: Get/create actual provider
        
        canonical_servers = dedupe_servers(conn, observations)
        
        # Store canonical records
        store_canonical_servers(conn, canonical_servers, default_provider_id)
        
        # Mark observations as processed
        with conn.cursor() as cur:
            obs_ids = [obs[0] for obs in raw_obs]
            cur.execute("""
                UPDATE raw_observations
                SET processed_at = %s
                WHERE observation_id = ANY(%s)
            """, (datetime.utcnow(), obs_ids))
            conn.commit()
        
        return {
            "success": True,
            "observationsProcessed": len(raw_obs),
            "canonicalServersCreated": len(canonical_servers),
            "processedAt": datetime.utcnow().isoformat()
        }
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
