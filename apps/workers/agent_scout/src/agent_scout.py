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
from sources.awesome import fetch_awesome_copilot_agents

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)

# Tier 1 sources for Agents
TIER1_SOURCES = [
    "https://api.github.com/repos/copilot-extensions/awesome-copilot/readme", # Awesome Copilot list
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
                observation_id, source_url, content_json, content_hash, retrieved_at, observation_type
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            observation_id,
            source_url,
            content_str,
            content_hash,
            datetime.utcnow(),
            'agent'
        ))
        db.commit()
    
    return observation_id


def run_scout():
    """
    Main scout function - fetch from all Tier 1 sources and store
    """
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        print("Database connection established")
    except Exception as e:
        print(f"Database connection error: {e}")
        return {
            "success": False,
            "error": f"Database connection failed: {e}",
            "completedAt": datetime.utcnow().isoformat()
        }
    
    total_observations = 0
    errors = []
    
    try:
        for source_url in TIER1_SOURCES:
            print(f"Fetching from: {source_url}")
            
            if "awesome-copilot" in source_url:
                try:
                    print("  Calling fetch_awesome_copilot_agents()...")
                    observations = fetch_awesome_copilot_agents()
                    print(f"  Fetched {len(observations)} agents from awesome-copilot")
                except Exception as e:
                    error_msg = f"Awesome adapter error: {e}"
                    print(f"  {error_msg}")
                    errors.append(error_msg)
                    continue
            else:
                # Use generic fetch_source for simple JSON APIs
                observations = fetch_source(source_url)
            
            # Store each observation
            print(f"  Storing {len(observations)} observations...")
            for idx, obs in enumerate(observations):
                # If obs has _full_server_json, keep it for evidence extraction
                # The normalized fields are already in obs for Curator
                observation_to_store = obs
                
                try:
                    store_raw_observation(conn, source_url, observation_to_store)
                    total_observations += 1
                    if (idx + 1) % 10 == 0:
                        print(f"    Stored {idx + 1}/{len(observations)} observations...")
                except Exception as e:
                    error_msg = f"Error storing observation: {e}"
                    print(f"  {error_msg}")
                    errors.append(error_msg)
                    
        # Process queue
        print(f"Fetching from submission queue...")
        with conn.cursor() as cur:
            cur.execute("SELECT submission_id, repo_url FROM submissions_queue WHERE status = 'pending' AND integration_type = 'agent'")
            rows = cur.fetchall()
            print(f"  Found {len(rows)} pending agent submissions.")
            for row in rows:
                sub_id, repo_url = row
                try:
                    # In a real system, you would fetch repo metadata here.
                    # For now, we stub it into an observation format.
                    obs = {
                        "name": repo_url.split('/')[-1] if '/' in repo_url else repo_url,
                        "github_url": repo_url,
                        "source": "submission_queue"
                    }
                    store_raw_observation(conn, repo_url, obs)
                    total_observations += 1
                    
                    # Mark processed
                    cur.execute("UPDATE submissions_queue SET status = 'completed', processed_at = %s WHERE submission_id = %s", (datetime.utcnow(), sub_id))
                    conn.commit()
                except Exception as e:
                    error_msg = f"Error processing submission {sub_id}: {e}"
                    print(f"  {error_msg}")
                    cur.execute("UPDATE submissions_queue SET status = 'failed', error_message = %s, processed_at = %s WHERE submission_id = %s", (str(e), datetime.utcnow(), sub_id))
                    conn.commit()
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
