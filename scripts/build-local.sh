#!/bin/bash
# Build all applications locally for testing

set -e

echo "🏗️  Building SecAI Radar Applications Locally"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo "✅ npm: $NPM_VERSION"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ Python: $PYTHON_VERSION"

# Check Docker (for containers)
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ Docker: $DOCKER_VERSION"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker not found. Container builds will be skipped.${NC}"
    DOCKER_AVAILABLE=false
fi

echo ""

# Build Public Web App
echo -e "${BLUE}Building Public Web App...${NC}"
cd apps/public-web

# Always ensure dependencies are installed
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Building web app (TypeScript + Vite)..."
npm run build

if [ -d "dist" ]; then
    echo -e "${GREEN}✅ Public Web App built successfully${NC}"
    echo "   Output: apps/public-web/dist/"
else
    echo "❌ Build failed - dist/ directory not found"
    exit 1
fi

cd ../..

echo ""

# Build Public API Container
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${BLUE}Building Public API Container...${NC}"
    cd apps/public-api
    
    echo "Building Docker image..."
    docker build -t secai-radar-public-api:local .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Public API container built successfully${NC}"
        echo "   Image: secai-radar-public-api:local"
        echo ""
        echo "To run locally:"
        echo "  docker run -p 8000:8000 -e DATABASE_URL='<connection-string>' secai-radar-public-api:local"
    else
        echo "❌ Container build failed"
        exit 1
    fi
    
    cd ../..
    
    echo ""
    
    # Build Registry API Container
    echo -e "${BLUE}Building Registry API Container...${NC}"
    cd apps/registry-api
    
    echo "Building Docker image..."
    docker build -t secai-radar-registry-api:local .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Registry API container built successfully${NC}"
        echo "   Image: secai-radar-registry-api:local"
        echo ""
        echo "To run locally:"
        echo "  docker run -p 8001:8001 -e DATABASE_URL='<connection-string>' secai-radar-registry-api:local"
    else
        echo "❌ Container build failed"
        exit 1
    fi
    
    cd ../..
else
    echo -e "${YELLOW}Skipping container builds (Docker not available)${NC}"
fi

echo ""
echo -e "${GREEN}✅ All builds complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Test Static Web App: cd apps/public-web && npm run preview"
echo "  2. Test Public API: docker run -p 8000:8000 secai-radar-public-api:local"
echo "  3. Update Azure Static Web App configuration"
echo "  4. Deploy to Azure"
