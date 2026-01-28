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


def is_valid_mcp_server(obs: Dict[str, Any], repo_url: Optional[str], endpoint: Optional[str], docs_url: Optional[str], name: str) -> tuple[bool, str]:
    """
    Validate that an observation represents a real MCP server.
    Returns (is_valid, reason).
    """
    # Must have at least one of: repo_url, endpoint, or docs_url
    if not repo_url and not endpoint and not docs_url:
        return False, "missing_all_urls"
    
    # Name must not be "Unknown" or empty
    if not name or name.lower().strip() in ("unknown", ""):
        return False, "invalid_name"
    
    # Must have some identifying information
    if not repo_url and not endpoint and not docs_url:
        return False, "no_identifiers"
    
    return True, "valid"


def dedupe_servers(
    db, raw_observations: List[Dict[str, Any]], review_log: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]:
    """
    Deduplicate servers using heuristics. ID precedence: repoUrl > endpoint host > docs URL > name+source.
    Logs to review_log when skipping (duplicate or ambiguous) for T-071 acceptance.
    Also validates that servers are real MCPs with required data.
    """
    log = review_log if review_log is not None else []
    canonical_servers = []
    seen_ids = set()
    seen_urls = {}  # Map normalized URL -> server_id for content-based deduplication
    
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
        
        # Normalize URLs for content-based deduplication
        normalized_repo = normalize_url(repo_url) if repo_url else None
        normalized_endpoint = normalize_url(endpoint) if endpoint else None
        normalized_docs = normalize_url(docs_url) if docs_url else None
        
        # Log extraction for first few observations
        if idx < 5:
            print(f"  Observation {idx+1}: name={name}, repo_url={bool(repo_url)}, endpoint={bool(endpoint)}, docs_url={bool(docs_url)}")

        # Validate that this is a real MCP server
        is_valid, reason = is_valid_mcp_server(obs, repo_url, endpoint, docs_url, name)
        if not is_valid:
            log.append(("invalid", None, name, reason))
            if idx < 10:
                print(f"    Skipped: invalid MCP server ({reason}): {name}")
            continue

        # Check for content-based duplicates (same normalized URLs)
        duplicate_id = None
        if normalized_repo and normalized_repo in seen_urls:
            duplicate_id = seen_urls[normalized_repo]
        elif normalized_endpoint and normalized_endpoint in seen_urls:
            duplicate_id = seen_urls[normalized_endpoint]
        elif normalized_docs and normalized_docs in seen_urls:
            duplicate_id = seen_urls[normalized_docs]
        
        if duplicate_id:
            log.append(("duplicate_content", duplicate_id, name))
            if idx < 10:
                print(f"    Skipped: duplicate content (matches {duplicate_id}): {name}")
            continue

        server_id = generate_server_id(repo_url, endpoint, docs_url, name, source)
        
        if idx < 5:
            print(f"    Generated server_id: {server_id}")

        # Check database for existing server_id
        with db.cursor() as cur:
            cur.execute("SELECT server_id FROM mcp_servers WHERE server_id = %s", (server_id,))
            if cur.fetchone():
                log.append(("duplicate", server_id, name))
                if idx < 10:
                    print(f"    Skipped: duplicate server_id {server_id}")
                continue
        
        # Check for same server_id in current batch
        if server_id in seen_ids:
            log.append(("ambiguous_same_batch", server_id, name))
            if idx < 10:
                print(f"    Skipped: ambiguous (same batch) server_id {server_id}")
            continue
        
        seen_ids.add(server_id)
        
        # Track normalized URLs for content-based deduplication
        if normalized_repo:
            seen_urls[normalized_repo] = server_id
        if normalized_endpoint:
            seen_urls[normalized_endpoint] = server_id
        if normalized_docs:
            seen_urls[normalized_docs] = server_id

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


def extract_provider_from_repo_url(repo_url: Optional[str]) -> Optional[tuple[str, str]]:
    """
    Extract provider name and domain from repository URL.
    Returns (provider_name, primary_domain) or None.
    For GitHub/GitLab, uses username as provider name and creates unique domain.
    """
    if not repo_url:
        return None
    
    # GitHub: github.com/username/repo or github.com/org/repo
    if 'github.com' in repo_url.lower():
        match = re.search(r'github\.com[:/]([^/]+)', repo_url, re.IGNORECASE)
        if match:
            username = match.group(1)
            # Use username as provider name, and create unique domain
            # Format: username.github.com (unique per username)
            return (username, f"{username}.github.com")
    
    # GitLab: gitlab.com/username/repo
    if 'gitlab.com' in repo_url.lower():
        match = re.search(r'gitlab\.com[:/]([^/]+)', repo_url, re.IGNORECASE)
        if match:
            username = match.group(1)
            return (username, f"{username}.gitlab.com")
    
    # Bitbucket: bitbucket.org/username/repo
    if 'bitbucket.org' in repo_url.lower():
        match = re.search(r'bitbucket\.org[:/]([^/]+)', repo_url, re.IGNORECASE)
        if match:
            username = match.group(1)
            return (username, f"{username}.bitbucket.org")
    
    # Generic: Extract domain from URL
    try:
        parsed = urlparse(repo_url)
        domain = parsed.netloc or parsed.path.split('/')[0] if parsed.path else None
        if domain and '.' in domain:
            # Use domain as provider name
            return (domain, domain)
    except:
        pass
    
    return None


def extract_category(server_name: str, description: Optional[str] = None) -> str:
    """
    Extract category from server name or description.
    Returns category string or "Tools" as default.
    """
    name_lower = server_name.lower()
    desc_lower = (description or "").lower()
    combined = f"{name_lower} {desc_lower}"
    
    # Pattern-based extraction
    if any(keyword in combined for keyword in ['database', 'db', 'sql', 'postgres', 'mysql', 'mongodb', 'redis']):
        return "Database"
    if any(keyword in combined for keyword in ['api', 'rest', 'graphql', 'rpc']):
        return "API"
    if any(keyword in combined for keyword in ['file', 'storage', 's3', 'blob', 'bucket']):
        return "Storage"
    if any(keyword in combined for keyword in ['email', 'mail', 'smtp', 'sendgrid']):
        return "Communication"
    if any(keyword in combined for keyword in ['auth', 'oauth', 'oidc', 'sso', 'login']):
        return "Authentication"
    if any(keyword in combined for keyword in ['ai', 'llm', 'gpt', 'openai', 'anthropic', 'model']):
        return "AI/ML"
    if any(keyword in combined for keyword in ['code', 'git', 'github', 'gitlab', 'repo', 'repository']):
        return "Development"
    if any(keyword in combined for keyword in ['slack', 'discord', 'teams', 'chat', 'message']):
        return "Communication"
    
    # Default to Tools
    return "Tools"


def get_or_create_provider(db, publisher: Optional[str], metadata: Dict[str, Any], repo_url: Optional[str] = None) -> str:
    """
    Get or create provider from publisher information or repo_url.
    Returns provider_id (defaults to Unknown provider if neither available).
    """
    provider_name = None
    primary_domain = None
    
    # Try publisher first
    if publisher:
        # Try to extract domain from publisher (might be email or domain)
        if "@" in publisher:
            # Email format: extract domain
            primary_domain = publisher.split("@")[-1]
            provider_name = publisher.split("@")[0]
        elif "." in publisher and not publisher.startswith("http"):
            # Might be a domain
            primary_domain = publisher
            provider_name = publisher.split('.')[0] if '.' in publisher else publisher
        else:
            # Use publisher name as domain fallback (normalized)
            provider_name = publisher
            primary_domain = f"{normalize_name(publisher)}.local"
    
    # Try repo_url if publisher not available
    if not provider_name and repo_url:
        provider_info = extract_provider_from_repo_url(repo_url)
        if provider_info:
            provider_name, primary_domain = provider_info
    
    # If still no provider, return Unknown
    if not provider_name:
        return "0000000000000000"
    
    # Generate provider ID
    provider_id = generate_provider_id(provider_name, primary_domain)
    
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
        """, (provider_id, provider_name, primary_domain, "Community"))
        db.commit()
    
    return provider_id


def store_canonical_servers(db, servers: List[Dict[str, Any]], default_provider_id: str):
    """
    Store canonical server records. Creates providers from publisher info when available.
    Sets status to 'Unknown' if server lacks required data (repo_url, endpoint, or docs_url).
    """
    print(f"store_canonical_servers: Starting to store {len(servers)} servers...", flush=True)
    stored_count = 0
    error_count = 0
    try:
        with db.cursor() as cur:
            # Check if metadata_json column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'mcp_servers' AND column_name = 'metadata_json'
            """)
            has_metadata_json = cur.fetchone() is not None
            print(f"  Has metadata_json column: {has_metadata_json}", flush=True)
        
            for idx, server in enumerate(servers):
                try:
                    metadata_json = json.dumps(server.get("metadata", {}))
                    deployment_type = server.get("deployment_type", "Unknown")
                    metadata = server.get("metadata", {})
                    
                    # Get or create provider from publisher or repo_url
                    publisher = metadata.get("publisher")
                    repo_url = server.get("repo_url")
                    provider_id = get_or_create_provider(db, publisher, metadata, repo_url) if (publisher or repo_url) else default_provider_id
                    
                    # Extract category
                    server_name = server.get("server_name", "Unknown")
                    description = metadata.get("description") or (metadata.get("_full_server_json", {}).get("description") if isinstance(metadata.get("_full_server_json"), dict) else None)
                    category_primary = extract_category(server_name, description)
                    
                    # Determine status: 'Active' if has required data (repo_url, docs_url, or endpoint), 'Unknown' otherwise
                    docs_url = server.get("docs_url")
                    # Check for endpoint in metadata (from remotes[0].url)
                    endpoint = None
                    if isinstance(metadata, dict):
                        full_json = metadata.get("_full_server_json", {})
                        if isinstance(full_json, dict):
                            remotes = full_json.get("remotes", [])
                            if remotes and isinstance(remotes, list) and len(remotes) > 0:
                                first_remote = remotes[0]
                                if isinstance(first_remote, dict):
                                    endpoint = first_remote.get("url")
                    has_required_data = bool(repo_url or docs_url or endpoint)
                    status = 'Active' if has_required_data else 'Unknown'
                    
                    # Ensure unique server_slug by appending server_id suffix if needed
                    base_slug = server["server_slug"]
                    server_slug = base_slug
                    slug_attempts = 0
                    while slug_attempts < 10:  # Limit attempts to avoid infinite loop
                        try:
                            # Check if slug exists for a different server_id
                            cur.execute("SELECT server_id FROM mcp_servers WHERE server_slug = %s AND server_id != %s", 
                                      (server_slug, server["server_id"]))
                            if cur.fetchone():
                                # Slug exists for different server, append server_id suffix
                                server_slug = f"{base_slug}-{server['server_id'][:8]}"
                                slug_attempts += 1
                            else:
                                break
                        except:
                            break
                    
                    if has_metadata_json:
                        # Use INSERT with ON CONFLICT for server_id, and handle slug conflicts by making slug unique
                        cur.execute("""
                            INSERT INTO mcp_servers (
                                server_id, server_slug, server_name, provider_id, category_primary,
                                deployment_type, auth_model, tool_agency,
                                repo_url, docs_url, metadata_json, status, first_seen_at, last_seen_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, 'Unknown', 'Unknown', %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (server_id)
                            DO UPDATE SET
                                last_seen_at = EXCLUDED.last_seen_at,
                                deployment_type = COALESCE(EXCLUDED.deployment_type, mcp_servers.deployment_type),
                                repo_url = COALESCE(EXCLUDED.repo_url, mcp_servers.repo_url),
                                docs_url = COALESCE(EXCLUDED.docs_url, mcp_servers.docs_url),
                                status = EXCLUDED.status,
                                category_primary = COALESCE(EXCLUDED.category_primary, mcp_servers.category_primary),
                                provider_id = CASE 
                                    WHEN mcp_servers.provider_id = '0000000000000000' 
                                    THEN EXCLUDED.provider_id 
                                    ELSE mcp_servers.provider_id 
                                END,
                                metadata_json = CASE 
                                    WHEN EXCLUDED.metadata_json != '{}'::jsonb 
                                    THEN EXCLUDED.metadata_json 
                                    ELSE mcp_servers.metadata_json 
                                END
                        """, (
                            server["server_id"],
                            server_slug,
                            server["server_name"],
                            provider_id,  # Use proper provider_id
                            category_primary,  # Set category
                            deployment_type,
                            server.get("repo_url"),
                            server.get("docs_url"),
                            metadata_json,
                            status,
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))
                    else:
                        # Fallback for databases without metadata_json column
                        cur.execute("""
                            INSERT INTO mcp_servers (
                                server_id, server_slug, server_name, provider_id, category_primary,
                                deployment_type, auth_model, tool_agency,
                                repo_url, docs_url, status, first_seen_at, last_seen_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, 'Unknown', 'Unknown', %s, %s, %s, %s, %s)
                            ON CONFLICT (server_id)
                            DO UPDATE SET
                                last_seen_at = EXCLUDED.last_seen_at,
                                deployment_type = COALESCE(EXCLUDED.deployment_type, mcp_servers.deployment_type),
                                repo_url = COALESCE(EXCLUDED.repo_url, mcp_servers.repo_url),
                                docs_url = COALESCE(EXCLUDED.docs_url, mcp_servers.docs_url),
                                status = EXCLUDED.status,
                                category_primary = COALESCE(EXCLUDED.category_primary, mcp_servers.category_primary),
                                provider_id = CASE 
                                    WHEN mcp_servers.provider_id = '0000000000000000' 
                                    THEN EXCLUDED.provider_id 
                                    ELSE mcp_servers.provider_id 
                                END
                        """, (
                            server["server_id"],
                            server_slug,
                            server["server_name"],
                            provider_id,  # Use proper provider_id
                            category_primary,  # Set category
                            deployment_type,
                            server.get("repo_url"),
                            server.get("docs_url"),
                            status,
                            datetime.utcnow(),
                            datetime.utcnow()
                        ))
                    stored_count += 1
                    if stored_count % 50 == 0:
                        print(f"  Stored {stored_count}/{len(servers)} servers...", flush=True)
                except Exception as e:
                    error_count += 1
                    server_id = server.get("server_id", "unknown")
                    print(f"  ERROR storing server {server_id}: {e}", flush=True)
                    if error_count == 1:  # Print first error with full traceback
                        import traceback
                        print("  FIRST ERROR TRACEBACK:", flush=True)
                        traceback.print_exc()
                        # Rollback and create new cursor for remaining servers
                        db.rollback()
                        cur = db.cursor()
                        # Re-check metadata_json column
                        cur.execute("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = 'mcp_servers' AND column_name = 'metadata_json'
                        """)
                        has_metadata_json = cur.fetchone() is not None
                    elif error_count <= 5:
                        print(f"  (Additional error, transaction already aborted)", flush=True)
            
            print(f"store_canonical_servers: Committing {stored_count} servers to database (errors: {error_count})...", flush=True)
            db.commit()
            print(f"store_canonical_servers: Commit complete. Stored {stored_count} servers, {error_count} errors.", flush=True)
    except Exception as e:
        print(f"store_canonical_servers: FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        db.rollback()
        raise


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

        print(f"About to store {len(canonical_servers)} canonical servers...")
        store_canonical_servers(conn, canonical_servers, default_provider_id)
        print(f"Finished storing canonical servers. Checking database...")
        
        # Verify servers were stored
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM mcp_servers")
            total_after = cur.fetchone()[0]
            print(f"Total servers in database after store: {total_after}")

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
