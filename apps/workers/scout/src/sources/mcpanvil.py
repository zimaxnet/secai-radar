"""
MCPAnvil adapter
Fetches and normalizes server data from mcpanvil.com/api/v1/
"""

import requests
from typing import List, Dict, Any, Optional


MCPANVIL_BASE_URL = "https://mcpanvil.com/api/v1"


def fetch_mcpanvil_servers(use_index: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch servers from MCPAnvil
    
    Args:
        use_index: If True, use lightweight /index.json. If False, use /all.json
    
    Returns:
        List of normalized server objects matching Curator contract
    """
    normalized_servers = []
    
    try:
        endpoint = f"{MCPANVIL_BASE_URL}/index.json" if use_index else f"{MCPANVIL_BASE_URL}/all.json"
        
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # MCPAnvil response format TBD - will need schema inspection
        # Assumed structure: list of server objects or object with "servers" key
        servers_list = data if isinstance(data, list) else data.get("servers", [])
        
        for server_item in servers_list:
            normalized = _normalize_mcpanvil_server(server_item)
            if normalized:
                normalized_servers.append(normalized)
        
        return normalized_servers
    except Exception as e:
        print(f"Error fetching from MCPAnvil: {e}")
        return []


def _normalize_mcpanvil_server(server_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize MCPAnvil server item to Curator contract format.
    
    Schema inspection needed - this is a placeholder mapping.
    Adjust field names based on actual MCPAnvil API response.
    """
    if not isinstance(server_item, dict):
        return None
    
    # Placeholder field mapping - update after schema inspection
    # Common field names to check: name, server_name, title, id
    name = (
        server_item.get("name") or
        server_item.get("server_name") or
        server_item.get("title") or
        server_item.get("id") or
        "Unknown"
    )
    
    # Placeholder mappings - adjust based on actual API response
    normalized = {
        "name": name,
        "repo_url": (
            server_item.get("repo_url") or
            server_item.get("repository") or
            server_item.get("github") or
            server_item.get("source")
        ),
        "endpoint": (
            server_item.get("endpoint") or
            server_item.get("url") or
            server_item.get("remote_url")
        ),
        "docs_url": (
            server_item.get("docs_url") or
            server_item.get("documentation") or
            server_item.get("docs") or
            server_item.get("readme")
        ),
        "description": server_item.get("description") or server_item.get("desc"),
        "publisher": server_item.get("publisher") or server_item.get("author") or server_item.get("owner"),
        # Store full item for potential enrichment
        "_mcpanvil_item": server_item,
    }
    
    # Remove None values
    normalized = {k: v for k, v in normalized.items() if v is not None}
    
    return normalized if normalized.get("name") else None
