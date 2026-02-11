#!/usr/bin/env python3
"""Fix Zep v0.27.2 PostgreSQL configuration with proper field structure."""
import subprocess
import sys
import json

def get_secret(vault, name):
    """Retrieve secret from Key Vault."""
    result = subprocess.run([
        'az', 'keyvault', 'secret', 'show',
        '--vault-name', vault,
        '--name', name,
        '--query', 'value',
        '-o', 'tsv'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error getting {name}: {result.stderr[:200]}")
        sys.exit(1)
    
    return result.stdout.strip()

def main():
    """Main function."""
    print("🔧 Fixing Zep PostgreSQL configuration...")
    
    # Get credentials
    password = get_secret('ctxecokv', 'postgres-password')
    
    # Create config with properly formatted PostgreSQL section
    # Zep v0.27.2 expects individual fields, not DSN
    config_yaml = f"""server:
  host: 0.0.0.0
  port: 8000
  web_enabled: false

log:
  level: debug

auth:
  required: false

store:
  type: postgres
  postgres:
    user: ctxecoadmin
    password: "{password}"
    host: ctxeco-db.postgres.database.azure.com
    port: 5432
    database: zep
    read_timeout: 0
    write_timeout: 0
    max_open_connections: 0

llm:
  service: openai
  azure_openai:
    llm_deployment: gpt-5-chat
    embedding_deployment: text-embedding-ada-002
    api_base: https://zimax-gw.azure-api.net/zimax/openai
"""

    print("✓ Config generated")
    print("\nConfig preview (first 300 chars):")
    print(config_yaml[:300] + "...")
    
    # Update secret in container app
    print("\n📝 Updating zep-config-yaml secret...")
    result = subprocess.run([
        'az', 'containerapp', 'secret', 'set',
        '--name', 'ctxeco-zep',
        '--resource-group', 'ctxeco-rg',
        '--secrets', f'zep-config-yaml={config_yaml}'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error updating secret: {result.stderr[:300]}")
        sys.exit(1)
    
    print("✅ Secret updated")
    
    # Restart container
    print("\n🔄 Restarting container...")
    result = subprocess.run([
        'az', 'containerapp', 'update',
        '--name', 'ctxeco-zep',
        '--resource-group', 'ctxeco-rg',
        '--image', 'ghcr.io/getzep/zep:latest'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error restarting: {result.stderr[:300]}")
        sys.exit(1)
    
    print("✅ Container restarting...")
    print("\n⏳ Wait 30 seconds for container to start, then check logs:")
    print("   az containerapp logs show --name ctxeco-zep --resource-group ctxeco-rg --tail 50")

if __name__ == '__main__':
    main()
