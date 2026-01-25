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

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)

# Tier 1 sources
TIER1_SOURCES = [
    "https://modelcontextprotocol.io/servers",  # Official registry
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
        # For MVP, return placeholder structure
        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else []
        
        return data if isinstance(data, list) else []
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
    
    try:
        for source_url in TIER1_SOURCES:
            print(f"Fetching from: {source_url}")
            observations = fetch_source(source_url)
            
            for obs in observations:
                store_raw_observation(conn, source_url, obs)
                total_observations += 1
        
        print(f"Scout completed: {total_observations} observations stored")
        return {
            "success": True,
            "observationsStored": total_observations,
            "sourcesProcessed": len(TIER1_SOURCES),
            "completedAt": datetime.utcnow().isoformat()
        }
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
