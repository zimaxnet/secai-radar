# Local Build Guide

## Overview

Build and test all applications locally before deploying to Azure.

## Prerequisites

- **Node.js 20+** and npm
- **Python 3.11+** and pip
- **Docker** (for container builds)

## Quick Start

### Build Everything

```bash
./scripts/build-local.sh
```

This will:
1. ✅ Check prerequisites
2. ✅ Build Public Web App (TypeScript + Vite)
3. ✅ Build Public API container
4. ✅ Build Registry API container

## Step-by-Step

### 1. Build Public Web App (Static Web App)

```bash
cd apps/public-web

# Install dependencies (first time)
npm install

# Type check
npm run typecheck  # if available

# Build
npm run build

# Preview locally
npm run preview
```

**Output:** `apps/public-web/dist/` directory

**Test:** Open http://localhost:4173 (or port shown)

### 2. Build Public API Container

```bash
cd apps/public-api

# Build Docker image
docker build -t secai-radar-public-api:local .

# Run locally
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar" \
  secai-radar-public-api:local
```

**Test:** 
- Health: http://localhost:8000/health
- API: http://localhost:8000/api/v1/public/health

### 3. Build Registry API Container

```bash
cd apps/registry-api

# Build Docker image
docker build -t secai-radar-registry-api:local .

# Run locally
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar" \
  secai-radar-registry-api:local
```

**Test:** http://localhost:8001/health

## Testing Locally

### Test Static Web App Build

```bash
./scripts/test-local-build.sh
```

This will:
- Verify build output exists
- Start preview server
- Open in browser

### Test API Locally

```bash
# Terminal 1: Run API
cd apps/public-api
docker run -p 8000:8000 \
  -e DATABASE_URL="<connection-string>" \
  secai-radar-public-api:local

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/public/health
```

### Test Frontend with Local API

1. Set API URL in frontend:
```bash
cd apps/public-web
export VITE_API_BASE="http://localhost:8000/api"
npm run dev
```

2. Or update `apps/public-web/.env.local`:
```
VITE_API_BASE=http://localhost:8000/api
```

## Build Outputs

### Public Web
- **Location:** `apps/public-web/dist/`
- **Contents:** Static HTML, JS, CSS files
- **Deploy:** Upload to Azure Static Web Apps

### Public API
- **Image:** `secai-radar-public-api:local`
- **Port:** 8000
- **Deploy:** Push to ACR, deploy to Container Apps

### Registry API
- **Image:** `secai-radar-registry-api:local`
- **Port:** 8001
- **Deploy:** Push to ACR, deploy to Container Apps

## Troubleshooting

### Node.js Build Issues
```bash
# Clear cache and reinstall
cd apps/public-web
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Python/Docker Issues
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check Docker
docker --version
docker ps  # Should work without errors
```

### TypeScript Errors
```bash
cd apps/public-web
npm run typecheck  # Check for type errors
```

### Missing Dependencies
```bash
# Install all workspace dependencies
npm install

# Or in specific app
cd apps/public-web
npm install
```

## Next Steps After Local Build

1. ✅ **Test locally** - Verify everything works
2. **Update Azure Static Web App** - Point to `apps/public-web`
3. **Deploy containers** - Push to ACR and deploy
4. **Configure environment** - Set DATABASE_URL, etc.

## Development Workflow

### Frontend Development
```bash
cd apps/public-web
npm run dev  # Hot reload development server
```

### API Development
```bash
cd apps/public-api
# Install dependencies
pip install -r requirements.txt

# Run locally (not in container)
uvicorn main:app --reload --port 8000
```

### Full Stack Development
```bash
# Terminal 1: Frontend
cd apps/public-web
VITE_API_BASE=http://localhost:8000/api npm run dev

# Terminal 2: Backend
cd apps/public-api
uvicorn main:app --reload --port 8000
```

## Build Scripts

- `scripts/build-local.sh` - Build everything
- `scripts/test-local-build.sh` - Test web build
- `scripts/update-swa-config.sh` - Update Azure config

## Resources

- **Vite Docs:** https://vite.dev/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Docker Docs:** https://docs.docker.com/
