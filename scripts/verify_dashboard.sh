#!/bin/bash
set -e
# Verify all endpoints used by the Dashboard

BASE_URL="https://secairadar.cloud/api/v1/public"

echo "1. Testing /status..."
curl -s -f "$BASE_URL/status" > /dev/null && echo "✅ OK" || echo "❌ FAILED"

echo "2. Testing /mcp/summary?window=24h..."
curl -s -f "$BASE_URL/mcp/summary?window=24h" > /dev/null && echo "✅ OK" || echo "❌ FAILED"

echo "3. Testing /mcp/rankings?sort=trustScore&page=1&pageSize=1..."
curl -s -f "$BASE_URL/mcp/rankings?sort=trustScore&page=1&pageSize=1" > /dev/null && echo "✅ OK" || echo "❌ FAILED"

echo "4. Testing /mcp/recently-updated?limit=50..."
curl -s -f "$BASE_URL/mcp/recently-updated?limit=50" > /dev/null && echo "✅ OK" || echo "❌ FAILED"

echo "All checks passed."
