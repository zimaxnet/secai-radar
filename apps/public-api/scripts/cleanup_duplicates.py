#!/usr/bin/env python3
"""
Cleanup duplicate MCP servers based on content similarity.
Marks duplicates as 'Deprecated' status, keeping the best one.

Criteria for "best" server:
1. Has repo_url (highest priority)
2. Has docs_url
3. Oldest first_seen_at (most established)
4. Most complete metadata
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../workers/curator/src'))

from curator import normalize_url

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def normalize_url_for_dedup(url: str) -> str:
    """Normalize URL for duplicate detection"""
    if not url:
        return ""
    normalized = normalize_url(url)
    return normalized.lower().strip() if normalized else ""


def find_duplicate_groups(db) -> Dict[str, List[Tuple[str, Dict]]]:
    """
    Find groups of duplicate servers based on normalized URLs.
    Returns: {normalized_url: [(server_id, server_data), ...]}
    """
    with db.cursor() as cur:
        cur.execute("""
            SELECT server_id, server_name, repo_url, docs_url, 
                   first_seen_at, status, metadata_json
            FROM mcp_servers
            WHERE status IN ('Active', 'Unknown')
            ORDER BY first_seen_at ASC
        """)
        servers = cur.fetchall()
    
    # Group by normalized URLs
    repo_groups: Dict[str, List[Tuple[str, Dict]]] = defaultdict(list)
    docs_groups: Dict[str, List[Tuple[str, Dict]]] = defaultdict(list)
    
    for row in servers:
        server_id, server_name, repo_url, docs_url, first_seen_at, status, metadata_json = row
        
        server_data = {
            "server_id": server_id,
            "server_name": server_name,
            "repo_url": repo_url,
            "docs_url": docs_url,
            "first_seen_at": first_seen_at,
            "status": status,
            "metadata_json": metadata_json,
        }
        
        # Group by normalized repo_url
        if repo_url:
            normalized_repo = normalize_url_for_dedup(repo_url)
            if normalized_repo:
                repo_groups[normalized_repo].append((server_id, server_data))
        
        # Group by normalized docs_url
        if docs_url:
            normalized_docs = normalize_url_for_dedup(docs_url)
            if normalized_docs:
                docs_groups[normalized_docs].append((server_id, server_data))
    
    # Merge groups: if two servers share repo_url OR docs_url, they're duplicates
    all_groups: Dict[str, List[Tuple[str, Dict]]] = {}
    
    # Process repo groups
    for normalized_url, servers in repo_groups.items():
        if len(servers) > 1:
            all_groups[normalized_url] = servers
    
    # Process docs groups and merge with repo groups if server_id overlaps
    for normalized_url, servers in docs_groups.items():
        if len(servers) > 1:
            # Check if any server_id already in a group
            existing_group_key = None
            for group_key, group_servers in all_groups.items():
                for server_id, _ in servers:
                    if any(sid == server_id for sid, _ in group_servers):
                        existing_group_key = group_key
                        break
                if existing_group_key:
                    break
            
            if existing_group_key:
                # Merge into existing group
                existing_server_ids = {sid for sid, _ in all_groups[existing_group_key]}
                for server_id, server_data in servers:
                    if server_id not in existing_server_ids:
                        all_groups[existing_group_key].append((server_id, server_data))
            else:
                all_groups[normalized_url] = servers
    
    return all_groups


def select_best_server(servers: List[Tuple[str, Dict]]) -> str:
    """
    Select the best server from a group of duplicates.
    Returns server_id of the best one.
    """
    if len(servers) == 1:
        return servers[0][0]
    
    # Score each server
    scored = []
    for server_id, server_data in servers:
        score = 0
        
        # Has repo_url: +100
        if server_data["repo_url"]:
            score += 100
        
        # Has docs_url: +50
        if server_data["docs_url"]:
            score += 50
        
        # Status is Active: +10
        if server_data["status"] == "Active":
            score += 10
        
        # Older first_seen_at: +1 per day (approximate)
        # We'll use position in sorted list as proxy
        
        scored.append((score, server_id, server_data))
    
    # Sort by score (desc), then by first_seen_at (asc - older is better)
    scored.sort(key=lambda x: (-x[0], x[2]["first_seen_at"] or ""))
    
    return scored[0][1]  # Return server_id of best one


def mark_duplicates_as_deprecated(db, duplicate_groups: Dict[str, List[Tuple[str, Dict]]]) -> int:
    """
    Mark duplicate servers as 'Deprecated', keeping the best one.
    Returns number of servers marked as deprecated.
    """
    deprecated_count = 0
    kept_server_ids: Set[str] = set()
    deprecated_server_ids: Set[str] = set()
    
    # Process each duplicate group
    for normalized_url, servers in duplicate_groups.items():
        if len(servers) <= 1:
            continue
        
        best_server_id = select_best_server(servers)
        kept_server_ids.add(best_server_id)
        
        # Mark others as deprecated
        for server_id, server_data in servers:
            if server_id != best_server_id:
                deprecated_server_ids.add(server_id)
                deprecated_count += 1
    
    # Update database
    if deprecated_server_ids:
        with db.cursor() as cur:
            server_ids_list = list(deprecated_server_ids)
            placeholders = ','.join(['%s'] * len(server_ids_list))
            cur.execute(f"""
                UPDATE mcp_servers
                SET status = 'Deprecated',
                    updated_at = NOW()
                WHERE server_id IN ({placeholders})
            """, server_ids_list)
            db.commit()
        
        print(f"  Kept {len(kept_server_ids)} best servers")
        print(f"  Marked {deprecated_count} duplicate servers as 'Deprecated'")
    
    return deprecated_count


def main():
    """Main cleanup function"""
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        print("Finding duplicate servers...")
        duplicate_groups = find_duplicate_groups(conn)
        
        total_duplicates = sum(len(servers) for servers in duplicate_groups.values() if len(servers) > 1)
        total_groups = len([g for g in duplicate_groups.values() if len(g) > 1])
        
        print(f"Found {total_groups} duplicate groups with {total_duplicates} total servers")
        
        if total_groups == 0:
            print("No duplicates found. Cleanup complete.")
            return
        
        print("Marking duplicates as 'Deprecated'...")
        deprecated_count = mark_duplicates_as_deprecated(conn, duplicate_groups)
        
        print(f"\nCleanup complete: {deprecated_count} servers marked as 'Deprecated'")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during cleanup: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
