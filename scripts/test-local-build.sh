#!/bin/bash
# Test local builds before deployment

set -e

echo "🧪 Testing Local Builds"
echo "======================="
echo ""

# Test Public Web build
echo "Testing Public Web build..."
cd apps/public-web

if [ ! -d "dist" ]; then
    echo "❌ dist/ directory not found. Run build first: npm run build"
    exit 1
fi

# Check if index.html exists
if [ ! -f "dist/index.html" ]; then
    echo "❌ dist/index.html not found"
    exit 1
fi

echo "✅ Public Web build looks good"
echo "   Files in dist/: $(ls -1 dist/ | wc -l | tr -d ' ') files"

# Test preview server
echo ""
echo "Starting preview server on http://localhost:4173"
echo "Press Ctrl+C to stop"
echo ""

npm run preview &
PREVIEW_PID=$!

sleep 3

# Check if server is running
if curl -s http://localhost:4173 > /dev/null; then
    echo "✅ Preview server is running"
    echo ""
    echo "Open http://localhost:4173 in your browser"
    echo "Press Ctrl+C to stop the server"
    
    wait $PREVIEW_PID
else
    echo "❌ Preview server failed to start"
    kill $PREVIEW_PID 2>/dev/null || true
    exit 1
fi
