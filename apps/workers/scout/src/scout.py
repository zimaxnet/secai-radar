"""
Scout Worker - Discovery ingestor
Finds MCP servers from multiple sources
"""

import os
import requests
import hashlib
import psycopg2
from datetime import datetime
from typing import List, Dict, Any
import json
import sys

# Add sources directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sources'))

from sources.registry import fetch_registry_servers
from sources.mcpanvil import fetch_mcpanvil_servers

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)

# Tier 1 sources
TIER1_SOURCES = [
    "https://registry.modelcontextprotocol.io/v0.1/servers",  # Official Registry API
    # Add more sources as needed
]


def fetch_source(source_url: str) -> List[Dict[str, Any]]:
    """
    Fetch raw observations from a source
    
    Returns:
        List of raw observation dictionaries
    """
    try:
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        
        # Parse response (format depends on source)
        # Support top-level list or object with "servers" / "items" key
        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get('servers') or data.get('items') or []
        return []
    except Exception as e:
        print(f"Error fetching {source_url}: {e}")
        return []


def hash_raw_content(content: str) -> str:
    """Generate hash for raw content"""
    return hashlib.sha256(content.encode()).hexdigest()


def store_raw_observation(db, source_url: str, observation: Dict[str, Any]) -> str:
    """
    Store raw observation (append-only)
    
    Returns:
        observation_id
    """
    content_str = json.dumps(observation, sort_keys=True)
    content_hash = hash_raw_content(content_str)
    observation_id = content_hash[:16]  # Use first 16 chars as ID
    
    with db.cursor() as cur:
        # Check if already exists
        cur.execute("""
            SELECT observation_id FROM raw_observations 
            WHERE content_hash = %s
        """, (content_hash,))
        
        if cur.fetchone():
            return observation_id  # Already exists
        
        # Insert new observation
        cur.execute("""
            INSERT INTO raw_observations (
                observation_id, source_url, content_json, content_hash, retrieved_at
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            observation_id,
            source_url,
            content_str,
            content_hash,
            datetime.utcnow()
        ))
        db.commit()
    
    return observation_id


def run_scout():
    """
    Main scout function - fetch from all Tier 1 sources and store
    """
    conn = psycopg2.connect(DATABASE_URL)
    
    total_observations = 0
    errors = []
    
    try:
        for source_url in TIER1_SOURCES:
            print(f"Fetching from: {source_url}")
            
            # Detect source type and use appropriate adapter
            if "registry.modelcontextprotocol.io" in source_url:
                # Use Official Registry adapter
                try:
                    observations = fetch_registry_servers(limit=100, use_latest_version=False)
                    print(f"  Fetched {len(observations)} servers from Official Registry")
                except Exception as e:
                    error_msg = f"Registry adapter error: {e}"
                    print(f"  {error_msg}")
                    errors.append(error_msg)
                    continue
            elif "mcpanvil.com" in source_url:
                # Use MCPAnvil adapter
                try:
                    observations = fetch_mcpanvil_servers(use_index=False)
                    print(f"  Fetched {len(observations)} servers from MCPAnvil")
                except Exception as e:
                    error_msg = f"MCPAnvil adapter error: {e}"
                    print(f"  {error_msg}")
                    errors.append(error_msg)
                    continue
            else:
                # Use generic fetch_source for simple JSON APIs
                observations = fetch_source(source_url)
            
            # Store each observation
            for obs in observations:
                # If obs has _full_server_json, keep it for evidence extraction
                # The normalized fields are already in obs for Curator
                observation_to_store = obs
                
                try:
                    store_raw_observation(conn, source_url, observation_to_store)
                    total_observations += 1
                except Exception as e:
                    error_msg = f"Error storing observation: {e}"
                    print(f"  {error_msg}")
                    errors.append(error_msg)
        
        print(f"Scout completed: {total_observations} observations stored")
        result = {
            "success": True,
            "observationsStored": total_observations,
            "sourcesProcessed": len(TIER1_SOURCES),
            "completedAt": datetime.utcnow().isoformat()
        }
        if errors:
            result["errors"] = errors[:20]  # Limit error output
        return result
    except Exception as e:
        print(f"Scout error: {e}")
        return {
            "success": False,
            "error": str(e),
            "completedAt": datetime.utcnow().isoformat()
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = run_scout()
    print(json.dumps(result, indent=2))
