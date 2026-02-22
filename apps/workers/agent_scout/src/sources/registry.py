"""
Official MCP Registry adapter
Fetches and normalizes server.json from registry.modelcontextprotocol.io/v0.1/
"""

import requests
from typing import List, Dict, Any, Optional
import json


REGISTRY_BASE_URL = "https://registry.modelcontextprotocol.io/v0.1"


def fetch_registry_servers(limit: int = 100, use_latest_version: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch servers from Official MCP Registry
    
    Args:
        limit: Number of servers per page (default 100)
        use_latest_version: If True, fetch full server.json for each server (slower but complete)
                          If False, use list endpoint (faster but may have less detail)
    
    Returns:
        List of normalized server objects matching Curator contract
    """
    normalized_servers = []
    
    try:
        if use_latest_version:
            # Option B: Fetch list first, then get latest version for each
            list_url = f"{REGISTRY_BASE_URL}/servers?limit={limit}"
            cursor = None
            
            while True:
                url = list_url
                if cursor:
                    url = f"{url}&cursor={cursor}"
                
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                servers_list = data.get("servers", []) if isinstance(data, dict) else data
                if not servers_list:
                    break
                
                # Fetch latest version for each server
                for server_summary in servers_list:
                    server_name = server_summary.get("name") or server_summary.get("serverName")
                    if not server_name:
                        continue
                    
                    try:
                        version_url = f"{REGISTRY_BASE_URL}/servers/{server_name}/versions/latest"
                        version_response = requests.get(version_url, timeout=15)
                        version_response.raise_for_status()
                        server_json = version_response.json()
                        
                        normalized = _normalize_server_json(server_json, server_name)
                        if normalized:
                            normalized_servers.append(normalized)
                    except Exception as e:
                        print(f"Error fetching latest version for {server_name}: {e}")
                        continue
                
                # Check for pagination (Official Registry uses metadata.nextCursor)
                cursor = None
                if isinstance(data, dict):
                    metadata = data.get("metadata", {})
                    if isinstance(metadata, dict):
                        cursor = metadata.get("nextCursor")
                
                if not cursor:
                    break
        else:
            # Option A: Use list endpoint (faster)
            list_url = f"{REGISTRY_BASE_URL}/servers?limit={limit}"
            cursor = None
            page_count = 0
            
            while True:
                page_count += 1
                url = list_url
                if cursor:
                    url = f"{url}&cursor={cursor}"
                
                print(f"    Fetching page {page_count}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                servers_list = data.get("servers", []) if isinstance(data, dict) else data
                if not servers_list:
                    print(f"    No more servers on page {page_count}")
                    break
                
                print(f"    Processing {len(servers_list)} servers from page {page_count}...")
                for server_item in servers_list:
                    # Official Registry wraps server.json in a "server" key
                    # Extract the actual server.json from the wrapper
                    if isinstance(server_item, dict) and "server" in server_item:
                        actual_server_json = server_item["server"]
                    else:
                        actual_server_json = server_item
                    
                    normalized = _normalize_server_json(actual_server_json, actual_server_json.get("name") if isinstance(actual_server_json, dict) else None)
                    if normalized:
                        normalized_servers.append(normalized)
                
                # Check for pagination (Official Registry uses metadata.nextCursor)
                cursor = None
                if isinstance(data, dict):
                    metadata = data.get("metadata", {})
                    if isinstance(metadata, dict):
                        cursor = metadata.get("nextCursor")
                
                if not cursor:
                    print(f"    No more pages (processed {page_count} pages)")
                    break
        
        return normalized_servers
    except Exception as e:
        print(f"Error fetching from Official Registry: {e}")
        return []


def _normalize_server_json(server_json: Dict[str, Any], server_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Normalize server.json to Curator contract format
    
    Returns normalized dict with: name, repo_url, endpoint, docs_url, publisher, description, transport, package
    Also preserves full server_json for evidence extraction
    """
    if not isinstance(server_json, dict):
        return None
    
    name = server_json.get("name") or server_name or "Unknown"
    
    # Extract remotes[] for endpoint
    remotes = server_json.get("remotes", [])
    endpoint = None
    transport = None
    if remotes and isinstance(remotes, list) and len(remotes) > 0:
        first_remote = remotes[0]
        if isinstance(first_remote, dict):
            endpoint = first_remote.get("url")
            # transport can be in remotes[].type or remotes[].transport.type
            transport = first_remote.get("type")
            if not transport and "transport" in first_remote:
                transport_obj = first_remote["transport"]
                if isinstance(transport_obj, dict):
                    transport = transport_obj.get("type")
    
    # Extract repository from server.json (can be object with url or direct url string)
    repo_url_from_server = None
    if "repository" in server_json:
        repo_obj = server_json["repository"]
        if isinstance(repo_obj, dict):
            repo_url_from_server = repo_obj.get("url")
        elif isinstance(repo_obj, str):
            repo_url_from_server = repo_obj
    
    # Extract packages[] for repo_url fallback and package info
    packages = server_json.get("packages", [])
    repo_url_from_packages = None
    package_info = None
    if packages and isinstance(packages, list) and len(packages) > 0:
        first_package = packages[0]
        if isinstance(first_package, dict):
            # Try to extract repo from package metadata
            repo_url_from_packages = first_package.get("repository") or first_package.get("repo")
            package_info = {
                "registry": first_package.get("registryType") or first_package.get("registry"),
                "type": first_package.get("type"),
                "identifier": first_package.get("identifier"),
                "version": first_package.get("version") or server_json.get("version"),
            }
    
    # Build normalized object
    normalized = {
        "name": name,
        "repo_url": repo_url_from_server or repo_url_from_packages,
        "endpoint": endpoint,
        "docs_url": server_json.get("docs_url") or server_json.get("documentation"),
        "publisher": server_json.get("publisher"),
        "description": server_json.get("description"),
        "transport": transport,
        "package": package_info,
        # Store full server.json for evidence extraction
        "_full_server_json": server_json,
    }
    
    # Remove None values for cleaner storage
    normalized = {k: v for k, v in normalized.items() if v is not None}
    
    return normalized


def extract_deployment_type(server_json: Dict[str, Any]) -> str:
    """
    Determine deployment_type from server.json
    
    Returns: 'Remote', 'Local', 'Hybrid', or 'Unknown'
    """
    has_remotes = bool(server_json.get("remotes"))
    has_packages = bool(server_json.get("packages"))
    
    if has_remotes and has_packages:
        return "Hybrid"
    elif has_remotes:
        return "Remote"
    elif has_packages:
        return "Local"
    else:
        return "Unknown"
