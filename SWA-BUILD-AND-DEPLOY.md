# Static Web App Build and Deploy Guide

## Overview

Build and deploy the Static Web App (frontend) first, then build containers for the APIs.

## Step 1: Build Static Web App Locally ✅

### Quick Build

```bash
cd apps/public-web
npm install  # First time only
npm run build
```

### Verify Build

```bash
# Check output
ls -la apps/public-web/dist/

# Preview locally
npm run preview
```

Open http://localhost:4173 to test.

### Build Script

```bash
./scripts/build-local.sh
```

This builds everything including containers.

## Step 2: Update Azure Static Web App Configuration

### Option A: Use Script

```bash
./scripts/update-swa-config.sh
```

### Option B: Azure Portal

1. Go to: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
2. **Configuration** → **Build Configuration**
3. Update:
   - **App location:** `apps/public-web`
   - **Output location:** `dist`
   - **API location:** (empty)

### Option C: Azure CLI

```bash
az staticwebapp update \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --app-location "apps/public-web" \
  --output-location "dist" \
  --api-location ""
```

## Step 3: Build Containers Locally

### Build All Containers

```bash
./scripts/build-containers.sh
```

### Or Build Individually

**Public API:**
```bash
cd apps/public-api
docker build -t secai-radar-public-api:local .
```

**Registry API:**
```bash
cd apps/registry-api
docker build -t secai-radar-registry-api:local .
```

## Step 4: Test Containers Locally

### Test Public API

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar" \
  secai-radar-public-api:local
```

Test:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/public/health
```

### Test Registry API

```bash
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar" \
  secai-radar-registry-api:local
```

Test:
```bash
curl http://localhost:8001/health
```

## Step 5: Deploy Static Web App

### Automatic (GitHub Actions)

Push to `main` branch - GitHub Actions will:
1. Build the web app
2. Deploy to Azure Static Web Apps

### Manual Deploy

```bash
# Build first
cd apps/public-web
npm run build

# Deploy using Azure CLI
az staticwebapp deploy \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --app-location "apps/public-web" \
  --output-location "dist" \
  --source .
```

## Step 6: Configure Frontend to Use API

### For Local Development

Create `apps/public-web/.env.local`:
```
VITE_API_BASE=http://localhost:8000/api
```

### For Production

Set GitHub secret:
- `VITE_API_BASE` = `https://<your-api-url>/api`

Or update in Azure Portal → Static Web App → Configuration → Application settings

## Troubleshooting

### Build Fails: TypeScript Errors

```bash
cd apps/public-web
npm install
npm run build
```

Check `tsconfig.json` and fix type errors.

### Build Fails: Missing Dependencies

```bash
cd apps/public-web
rm -rf node_modules package-lock.json
npm install
```

### Container Build Fails

```bash
# Check Docker is running
docker ps

# Check Dockerfile syntax
docker build --no-cache -t test-build apps/public-api
```

### Deployment Fails

1. Check Azure Static Web App configuration matches
2. Verify `AZURE_STATIC_WEB_APPS_API_TOKEN` secret is set
3. Check GitHub Actions logs

## Build Outputs

### Static Web App
- **Location:** `apps/public-web/dist/`
- **Contents:** HTML, JS, CSS, assets
- **Size:** Check with `du -sh apps/public-web/dist/`

### Containers
- **Public API:** `secai-radar-public-api:local`
- **Registry API:** `secai-radar-registry-api:local`
- **Size:** Check with `docker images | grep secai-radar`

## Next Steps After Build

1. ✅ **Static Web App built** → Deploy to Azure
2. ✅ **Containers built** → Test locally, then push to ACR
3. **Run migrations** → Set up database schema
4. **Deploy APIs** → Deploy containers to Container Apps
5. **Test end-to-end** → Verify everything works

## Resources

- **Azure Portal (SWA):** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
- **Local Build Guide:** `LOCAL-BUILD-GUIDE.md`
