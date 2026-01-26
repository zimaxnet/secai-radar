#!/bin/bash
# Step 7: Test end-to-end – Public API + SWA
# Run from repo root. Requires curl.
#
# Public API base (Container App). Override with PUBLIC_API_BASE if needed.
PUBLIC_API_BASE="${PUBLIC_API_BASE:-https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io}"

set -e
echo "Testing Public API: $PUBLIC_API_BASE"
echo ""

# Health
echo -n "GET /health … "
code=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "$PUBLIC_API_BASE/health")
if [ "$code" = "200" ]; then echo "200 OK"; else echo "FAIL ($code)"; exit 1; fi

echo -n "GET /api/v1/public/health … "
code=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "$PUBLIC_API_BASE/api/v1/public/health")
if [ "$code" = "200" ]; then echo "200 OK"; else echo "FAIL ($code)"; exit 1; fi

# JSON feed
echo -n "GET /api/v1/public/mcp/feed.json … "
code=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "$PUBLIC_API_BASE/api/v1/public/mcp/feed.json")
if [ "$code" = "200" ]; then echo "200 OK"; else echo "FAIL ($code)"; exit 1; fi

echo ""
echo "API checks passed."
echo "Manual checks:"
echo "  - SWA: https://purple-moss-0942f9e10.3.azurestaticapps.net (default) or https://secairadar.cloud"
echo "  - MCP: .../mcp (Overview, Rankings, Server Detail, Daily Brief)"
echo "  - If default hostname works but secairadar.cloud does not, see docs/SWA-SITE-TROUBLESHOOTING.md"
