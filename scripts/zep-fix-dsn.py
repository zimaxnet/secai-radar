#!/usr/bin/env python3
"""Fix Zep v0.27.2 (latest) config with DSN format."""
import subprocess
import sys
import urllib.parse

# Get password
result = subprocess.run([
    'az', 'keyvault', 'secret', 'show',
    '--vault-name', 'ctxecokv',
    '--name', 'postgres-password',
    '--query', 'value',
    '-o', 'tsv'
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error getting password")
    sys.exit(1)

password = result.stdout.strip()
encoded_password = urllib.parse.quote(password, safe='')

# v0.27.2 needs DSN in config file, with URL-encoded password
dsn = f"postgresql://ctxecoadmin:{encoded_password}@ctxeco-db.postgres.database.azure.com:5432/zep?sslmode=require"

config = f"""server:
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
    dsn: {dsn}
"""

print("📝 Updating config with URL-encoded DSN...")
result = subprocess.run([
    'az', 'containerapp', 'secret', 'set',
    '--name', 'ctxeco-zep',
    '--resource-group', 'ctxeco-rg',
    '--secrets', f'zep-config-yaml={config}'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ Error: {result.stderr[:300]}")
    sys.exit(1)

print("✅ Config updated")

print("\n🔄 Restarting container...")
result = subprocess.run([
    'az', 'containerapp', 'update',
    '--name', 'ctxeco-zep',
    '--resource-group', 'ctxeco-rg',
    '--set-env-vars', 'RESTART_VERSION=5'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ Error: {result.stderr[:200]}")
    sys.exit(1)

print("✅ Container restarting...")
print("\n⏳ Check logs in 30 seconds:")
print("   az containerapp logs show --name ctxeco-zep --resource-group ctxeco-rg --tail 50")
