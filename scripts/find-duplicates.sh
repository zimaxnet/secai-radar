#!/bin/bash
# Find duplicate servers in the database, especially for "filesystem anthropic"

set -e
cd "$(dirname "$0")/.."

if [ -z "${DATABASE_URL}" ]; then
  KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
  if command -v az &>/dev/null && az account show &>/dev/null 2>&1; then
    DATABASE_URL=$(az keyvault secret show --vault-name "$KV_NAME" --name database-url --query value -o tsv 2>/dev/null || true)
  fi
fi

if [ -z "${DATABASE_URL}" ]; then
  echo "DATABASE_URL is not set. Set it or use Azure CLI + Key Vault (secai-radar-kv / database-url)."
  exit 1
fi

export DATABASE_URL

VENV="${PWD}/apps/public-api/.venv"
PYTHON="${VENV}/bin/python"

if [ ! -d "$VENV" ]; then
  echo "Virtual environment not found at $VENV"
  exit 1
fi

echo "=== Finding duplicate servers ==="
echo ""

"$PYTHON" << 'PYTHON_SCRIPT'
import os
import psycopg2
from urllib.parse import urlparse
from collections import defaultdict

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

try:
    with conn.cursor() as cur:
        # Get all servers
        cur.execute("""
            SELECT server_id, server_name, server_slug, repo_url, docs_url, 
                   status, first_seen_at, provider_id
            FROM mcp_servers
            ORDER BY server_name, first_seen_at
        """)
        servers = cur.fetchall()
        
        print(f"Total servers in database: {len(servers)}\n")
        
        # Group by normalized name
        name_groups = defaultdict(list)
        for row in servers:
            server_id, server_name, server_slug, repo_url, docs_url, status, first_seen_at, provider_id = row
            normalized_name = server_name.lower().strip() if server_name else ""
            name_groups[normalized_name].append({
                "server_id": server_id,
                "server_name": server_name,
                "server_slug": server_slug,
                "repo_url": repo_url,
                "docs_url": docs_url,
                "status": status,
                "first_seen_at": first_seen_at,
                "provider_id": provider_id
            })
        
        # Find duplicates by name
        print("=== Duplicates by Name ===")
        name_duplicates = {k: v for k, v in name_groups.items() if len(v) > 1 and k}
        if name_duplicates:
            for name, servers_list in sorted(name_duplicates.items()):
                print(f"\n'{name}' ({len(servers_list)} entries):")
                for s in servers_list:
                    print(f"  - {s['server_id']}: {s['server_name']} (status: {s['status']}, repo: {s['repo_url'] or 'none'}, docs: {s['docs_url'] or 'none'})")
        else:
            print("No duplicates found by name")
        
        # Group by normalized repo_url
        repo_groups = defaultdict(list)
        for row in servers:
            server_id, server_name, server_slug, repo_url, docs_url, status, first_seen_at, provider_id = row
            if repo_url:
                # Normalize: lowercase, remove query params
                normalized = repo_url.lower().split('?')[0].split('#')[0].rstrip('/')
                repo_groups[normalized].append({
                    "server_id": server_id,
                    "server_name": server_name,
                    "repo_url": repo_url
                })
        
        # Find duplicates by repo_url
        print("\n=== Duplicates by Repo URL ===")
        repo_duplicates = {k: v for k, v in repo_groups.items() if len(v) > 1}
        if repo_duplicates:
            for url, servers_list in sorted(repo_duplicates.items()):
                print(f"\n'{url}' ({len(servers_list)} entries):")
                for s in servers_list:
                    print(f"  - {s['server_id']}: {s['server_name']}")
        else:
            print("No duplicates found by repo URL")
        
        # Group by normalized docs_url
        docs_groups = defaultdict(list)
        for row in servers:
            server_id, server_name, server_slug, repo_url, docs_url, status, first_seen_at, provider_id = row
            if docs_url:
                normalized = docs_url.lower().split('?')[0].split('#')[0].rstrip('/')
                docs_groups[normalized].append({
                    "server_id": server_id,
                    "server_name": server_name,
                    "docs_url": docs_url
                })
        
        # Find duplicates by docs_url
        print("\n=== Duplicates by Docs URL ===")
        docs_duplicates = {k: v for k, v in docs_groups.items() if len(v) > 1}
        if docs_duplicates:
            for url, servers_list in sorted(docs_duplicates.items()):
                print(f"\n'{url}' ({len(servers_list)} entries):")
                for s in servers_list:
                    print(f"  - {s['server_id']}: {s['server_name']}")
        else:
            print("No duplicates found by docs URL")
        
        # Check for "filesystem anthropic" specifically
        print("\n=== 'filesystem anthropic' entries ===")
        anthropic_servers = [s for s in servers if 'anthropic' in s[1].lower() and 'filesystem' in s[1].lower()]
        if anthropic_servers:
            print(f"Found {len(anthropic_servers)} entries:")
            for row in anthropic_servers:
                server_id, server_name, server_slug, repo_url, docs_url, status, first_seen_at, provider_id = row
                print(f"  - {server_id}: '{server_name}' (status: {status})")
                print(f"    repo_url: {repo_url or 'none'}")
                print(f"    docs_url: {docs_url or 'none'}")
                print(f"    first_seen_at: {first_seen_at}")
        else:
            print("No 'filesystem anthropic' entries found")
        
        # Check active servers in rankings
        print("\n=== Active servers in latest_scores ===")
        cur.execute("""
            SELECT s.server_id, s.server_name, s.repo_url, s.docs_url, s.status
            FROM mcp_servers s
            JOIN latest_scores ls ON s.server_id = ls.server_id
            WHERE s.status = 'Active'
            ORDER BY s.server_name
        """)
        active_scored = cur.fetchall()
        print(f"Total active servers with scores: {len(active_scored)}")
        
        # Check for duplicates in active scored
        active_name_groups = defaultdict(list)
        for row in active_scored:
            server_id, server_name, repo_url, docs_url, status = row
            normalized_name = server_name.lower().strip() if server_name else ""
            active_name_groups[normalized_name].append({
                "server_id": server_id,
                "server_name": server_name,
                "repo_url": repo_url,
                "docs_url": docs_url
            })
        
        active_duplicates = {k: v for k, v in active_name_groups.items() if len(v) > 1}
        if active_duplicates:
            print(f"\nActive servers with duplicate names in rankings: {len(active_duplicates)} groups")
            for name, servers_list in sorted(active_duplicates.items()):
                print(f"\n'{name}' ({len(servers_list)} entries):")
                for s in servers_list:
                    print(f"  - {s['server_id']}: {s['server_name']}")
                    print(f"    repo: {s['repo_url'] or 'none'}, docs: {s['docs_url'] or 'none'}")
        else:
            print("No duplicate names in active scored servers")

finally:
    conn.close()
PYTHON_SCRIPT

echo ""
echo "=== Done ==="
