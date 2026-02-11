#!/usr/bin/env python3
"""Update Zep config with proper PostgreSQL settings."""
import subprocess
import sys

# Get password from Key Vault
result = subprocess.run([
    'az', 'keyvault', 'secret', 'show',
    '--vault-name', 'ctxecokv',
    '--name', 'postgres-password',
    '--query', 'value',
    '-o', 'tsv'
], capture_output=True, text=True)

if result.returncode != 0:
    print("Error getting password")
    sys.exit(1)

password = result.stdout.strip()

# Minimal config - only PostgreSQL, let env vars handle LLM
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
    user: ctxecoadmin
    password: "{password}"
    host: ctxeco-db.postgres.database.azure.com
    port: 5432
    database: zep
    read_timeout: 0
    write_timeout: 0
    max_open_connections: 0
"""

# Update secret
result = subprocess.run([
    'az', 'containerapp', 'secret', 'set',
    '--name', 'ctxeco-zep',
    '--resource-group', 'ctxeco-rg',
    '--secrets', f'zep-config-yaml={config}'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error updating secret: {result.stderr[:200]}")
    sys.exit(1)

print("✅ Config updated")

# Restart
result = subprocess.run([
    'az', 'containerapp', 'update',
    '--name', 'ctxeco-zep',
    '--resource-group', 'ctxeco-rg',
    '--set-env-vars', 'RESTART_VERSION=3'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error restarting: {result.stderr[:200]}")
    sys.exit(1)

print("✅ Restarting container...")
