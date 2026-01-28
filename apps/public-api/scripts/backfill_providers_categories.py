#!/usr/bin/env python3
"""
Backfill Providers and Categories Script

Fixes existing servers that have:
- provider_id = '0000000000000000' (Unknown)
- category_primary = NULL

Extracts provider from repo_url and category from server name/description.
"""

import os
import subprocess
import sys
import re
from urllib.parse import urlparse

import psycopg2

# Get database URL from Azure Key Vault or environment
def get_database_url():
    """Get DATABASE_URL from Azure Key Vault or environment variable."""
    if "DATABASE_URL" in os.environ:
        return os.environ["DATABASE_URL"]
    
    # Try Azure Key Vault
    try:
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", "secai-radar-kv", 
             "--name", "database-url", "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: DATABASE_URL not found in environment and Azure CLI not available.")
        print("Please set DATABASE_URL environment variable or ensure Azure CLI is installed and configured.")
        sys.exit(1)


def normalize_name(name: str) -> str:
    """Normalize provider/server name"""
    normalized = name.lower().strip()
    normalized = re.sub(r'[^a-z0-9\s-]', '', normalized)
    normalized = re.sub(r'\s+', '-', normalized)
    return normalized


def generate_provider_id(legal_name: str, primary_domain: str) -> str:
    """Generate canonical provider ID"""
    import hashlib
    normalized = f"{normalize_name(legal_name)}|{primary_domain.lower().strip()}"
    hash_val = int(hashlib.sha256(normalized.encode()).hexdigest()[:16], 16)
    return format(hash_val, '016x')


def extract_provider_from_repo_url(repo_url: str) -> tuple[str, str] | None:
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


def extract_category(server_name: str, description: str | None = None) -> str:
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


def get_or_create_provider(conn, repo_url: str) -> str | None:
    """
    Get or create provider from repo_url.
    Returns provider_id or None if cannot extract.
    """
    provider_info = extract_provider_from_repo_url(repo_url)
    if not provider_info:
        return None
    
    provider_name, primary_domain = provider_info
    provider_id = generate_provider_id(provider_name, primary_domain)
    
    with conn.cursor() as cur:
        # Check if provider exists
        cur.execute("SELECT provider_id FROM providers WHERE provider_id = %s", (provider_id,))
        if cur.fetchone():
            return provider_id
        
        # Create new provider
        cur.execute("""
            INSERT INTO providers (provider_id, provider_name, primary_domain, provider_type)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (provider_id) DO NOTHING
        """, (provider_id, provider_name, primary_domain, "Community"))
        conn.commit()
    
    return provider_id


def backfill_providers_categories():
    """Backfill providers and categories for existing servers."""
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    
    try:
        with conn.cursor() as cur:
            # Get servers that need fixing
            cur.execute("""
                SELECT server_id, server_name, repo_url, docs_url, metadata_json, category_primary
                FROM mcp_servers
                WHERE status = 'Active'
                AND (provider_id = '0000000000000000' OR category_primary IS NULL)
                ORDER BY server_id
            """)
            servers = cur.fetchall()
            
            print(f"Found {len(servers)} servers to fix")
            
            updated_providers = 0
            updated_categories = 0
            errors = 0
            
            for server_id, server_name, repo_url, docs_url, metadata_json, current_category in servers:
                try:
                    # Extract provider from repo_url
                    new_provider_id = None
                    if repo_url:
                        new_provider_id = get_or_create_provider(conn, repo_url)
                    
                    # Extract category
                    description = None
                    if metadata_json:
                        if isinstance(metadata_json, dict):
                            description = metadata_json.get("description") or (metadata_json.get("_full_server_json", {}).get("description") if isinstance(metadata_json.get("_full_server_json"), dict) else None)
                        elif isinstance(metadata_json, str):
                            import json
                            try:
                                meta_dict = json.loads(metadata_json)
                                description = meta_dict.get("description") or (meta_dict.get("_full_server_json", {}).get("description") if isinstance(meta_dict.get("_full_server_json"), dict) else None)
                            except:
                                pass
                    
                    new_category = extract_category(server_name, description)
                    
                    # Update server
                    updates = []
                    params = []
                    
                    if new_provider_id and new_provider_id != '0000000000000000':
                        updates.append("provider_id = %s")
                        params.append(new_provider_id)
                        updated_providers += 1
                    
                    if new_category and (not current_category or current_category != new_category):
                        updates.append("category_primary = %s")
                        params.append(new_category)
                        updated_categories += 1
                    
                    if updates:
                        params.append(server_id)
                        cur.execute(f"""
                            UPDATE mcp_servers
                            SET {', '.join(updates)}, updated_at = NOW()
                            WHERE server_id = %s
                        """, params)
                        conn.commit()
                        
                        if updated_providers % 50 == 0 or updated_categories % 50 == 0:
                            print(f"  Updated {updated_providers} providers, {updated_categories} categories...")
                
                except Exception as e:
                    errors += 1
                    if errors <= 10:
                        print(f"  Error updating {server_name}: {e}")
                    conn.rollback()
                    continue
            
            print(f"\nBackfill completed:")
            print(f"  Updated providers: {updated_providers}")
            print(f"  Updated categories: {updated_categories}")
            print(f"  Errors: {errors}")
            
            # Verify results
            cur.execute("""
                SELECT COUNT(*) 
                FROM mcp_servers 
                WHERE status = 'Active' AND provider_id = '0000000000000000'
            """)
            remaining_unknown = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) 
                FROM mcp_servers 
                WHERE status = 'Active' AND category_primary IS NULL
            """)
            remaining_null_category = cur.fetchone()[0]
            
            print(f"\nRemaining issues:")
            print(f"  Servers with Unknown provider: {remaining_unknown}")
            print(f"  Servers with NULL category: {remaining_null_category}")
                
    except Exception as e:
        conn.rollback()
        print(f"Error during backfill: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    backfill_providers_categories()
