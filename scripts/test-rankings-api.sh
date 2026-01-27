#!/bin/bash
# Test script to call the rankings API and verify it returns data

set -e
cd "$(dirname "$0")/.."

API_BASE="${API_BASE_URL:-http://localhost:8000}"

echo "=== Testing Rankings API ==="
echo "API Base: $API_BASE"
echo ""

echo "1. Testing GET /api/v1/public/mcp/rankings"
echo "   " + "-" * 60

response=$(curl -s "${API_BASE}/api/v1/public/mcp/rankings?pageSize=10" || echo "ERROR")

if [ "$response" = "ERROR" ]; then
    echo "   ❌ Failed to connect to API"
    echo "   Make sure the API server is running:"
    echo "     cd apps/public-api && python -m uvicorn src.main:app --reload"
    exit 1
fi

# Check if response is valid JSON
if ! echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
    echo "   ❌ API returned invalid JSON:"
    echo "$response" | head -20
    exit 1
fi

# Extract key fields
items_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('items', [])))" 2>/dev/null || echo "0")
total=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('meta', {}).get('total', 0))" 2>/dev/null || echo "0")

echo "   Items in response: $items_count"
echo "   Total count: $total"

if [ "$items_count" = "0" ] && [ "$total" = "0" ]; then
    echo "   ⚠️  API returned empty results"
    echo ""
    echo "   Full response:"
    echo "$response" | python3 -m json.tool | head -30
    echo ""
    echo "   Check:"
    echo "   1. Run diagnostic: ./scripts/diagnose-rankings.sh"
    echo "   2. Verify latest_scores has data"
    echo "   3. Check API logs for errors"
else
    echo "   ✓ API returned $items_count items (total: $total)"
    echo ""
    echo "   Sample items:"
    echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data.get('data', {}).get('items', [])[:3]
for item in items:
    print(f\"     - {item.get('serverName', 'Unknown')} (Score: {item.get('trustScore', 0)}, Tier: {item.get('tier', '?')})\")
" 2>/dev/null || echo "     (Could not parse items)"
fi

echo ""
echo "=== Test Complete ==="
