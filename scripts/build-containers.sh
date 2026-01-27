#!/bin/bash
# Build Docker containers locally

set -e

echo "🐳 Building Docker Containers"
echo "=============================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Docker: $(docker --version)"
echo ""

# Build Public API
echo "Building Public API container..."
cd apps/public-api

docker build -t secai-radar-public-api:local \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "local") \
  .

if [ $? -eq 0 ]; then
    echo "✅ Public API container built: secai-radar-public-api:local"
else
    echo "❌ Public API container build failed"
    exit 1
fi

cd ../..

echo ""

# Build Registry API
echo "Building Registry API container..."
cd apps/registry-api

docker build -t secai-radar-registry-api:local \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "local") \
  .

if [ $? -eq 0 ]; then
    echo "✅ Registry API container built: secai-radar-registry-api:local"
else
    echo "❌ Registry API container build failed"
    exit 1
fi

cd ../..

echo ""

# Build Publisher worker (optional - used in pipeline)
echo "Building Publisher worker container..."
cd apps/workers/publisher

docker build -t secai-radar-publisher:local . 2>/dev/null && echo "✅ Publisher container built: secai-radar-publisher:local" || echo "⚠️  Publisher build skipped or failed (optional)"

cd ../../..

echo ""
echo "✅ Container build phase complete."
echo ""
echo "To run API containers:"
echo ""
echo "Public API:"
echo "  docker run -p 8000:8000 \\"
echo "    -e DATABASE_URL='postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar' \\"
echo "    secai-radar-public-api:local"
echo ""
echo "Registry API:"
echo "  docker run -p 8001:8001 \\"
echo "    -e DATABASE_URL='postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar' \\"
echo "    secai-radar-registry-api:local"
echo ""
echo "To test:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8001/health"
