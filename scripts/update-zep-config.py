#!/usr/bin/env python3
import subprocess
import sys

# Get DSN from Key Vault
result = subprocess.run([
    'az', 'keyvault', 'secret', 'show',
    '--vault-name', 'ctxecokv',
    '--name', 'zep-postgres-dsn',
    '--query', 'value',
    '-o', 'tsv'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error getting DSN: {result.stderr}")
    sys.exit(1)

dsn = result.stdout.strip()

# Create updated config with DSN
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
    dsn: {dsn}

llm:
  service: openai
  azure_openai_endpoint: https://zimax-gw.azure-api.net/zimax/openai/v1
  azure_openai:
    llm_deployment: gpt-5-chat
    embedding_deployment: text-embedding-ada-002
"""

print("Updated config:")
print(config_yaml[:200] + "...")

# Update secret
result = subprocess.run([
    'az', 'containerapp', 'secret', 'set',
    '--name', 'ctxeco-zep',
    '--resource-group', 'ctxeco-rg',
    '--secrets', f'zep-config-yaml={config_yaml}'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"\nError updating secret: {result.stderr[:500]}")
    sys.exit(1)

print("\n✅ Secret updated successfully!")
print("Restarting container...")

# Restart
import time
result = subprocess.run([
    'az', 'containerapp', 'update',
    '--name', 'ctxeco-zep',
    '--resource-group', 'ctxeco-rg',
    '--set-env-vars', f'CONFIG_UPDATE={int(time.time())}'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error restarting: {result.stderr[:300]}")
    sys.exit(1)

print("✅ Container restarting...")
