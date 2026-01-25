# Ready for Deployment ✅

## Build Status

### ✅ Static Web App
- **Status:** Building successfully
- **Output:** `apps/public-web/dist/`
- **Size:** ~1.1 MB total (gzipped: ~315 KB)
- **Ready to deploy:** Yes

### ✅ Public API Container
- **Status:** Built successfully
- **Image:** `secai-radar-public-api:local`
- **Ready to push:** Yes

### ✅ Registry API Container
- **Status:** Ready to build
- **Image:** `secai-radar-registry-api:local` (after build)
- **Ready to push:** Yes (after build)

### ✅ Database
- **Status:** Created
- **Server:** `ctxeco-db.postgres.database.azure.com`
- **Database:** `secairadar`
- **User:** `ctxecoadmin`
- **Ready for migrations:** Yes

## Deployment Checklist

### Phase 1: Static Web App (5 minutes)

- [ ] Update Azure Static Web App configuration
  ```bash
  ./scripts/update-swa-config.sh
  ```
- [ ] Push to main branch (triggers auto-deploy)
- [ ] Verify deployment at `https://secairadar.cloud/mcp`

### Phase 2: Database Setup (10 minutes)

- [ ] Get admin password for `ctxecoadmin`
- [ ] Set DATABASE_URL environment variable
- [ ] Run migrations:
  ```bash
  cd apps/public-api
  export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
  python scripts/migrate.py
  ```
- [ ] Seed sample data (optional):
  ```bash
  python scripts/seed.py
  ```

### Phase 3: Infrastructure (30 minutes)

- [ ] Deploy infrastructure (without PostgreSQL):
  ```bash
  cd infra
  az deployment group create \
    --resource-group secai-radar-rg \
    --template-file mcp-infrastructure-existing-db.bicep \
    --parameters @parameters/dev-existing-db.bicepparam
  ```
- [ ] Get ACR name and Container Apps Environment name
- [ ] Configure GitHub secrets (DATABASE_URL, VITE_API_BASE)

### Phase 4: Container Deployment (20 minutes)

- [ ] Build and push Public API:
  ```bash
  ACR_NAME=<acr-name>
  cd apps/public-api
  az acr build --registry $ACR_NAME --image secai-radar-public-api:latest .
  ```
- [ ] Build and push Registry API:
  ```bash
  cd apps/registry-api
  az acr build --registry $ACR_NAME --image secai-radar-registry-api:latest .
  ```
- [ ] Deploy Public API to Container Apps
- [ ] Deploy Registry API to Container Apps

### Phase 5: Testing (15 minutes)

- [ ] Test Static Web App loads
- [ ] Test API health endpoints
- [ ] Test frontend connects to API
- [ ] Test database queries work
- [ ] Verify feeds (RSS, JSON)

## Quick Commands

### Build Everything
```bash
./scripts/build-local.sh        # Build web + containers
./scripts/build-containers.sh   # Build containers only
```

### Test Locally
```bash
# Web app
cd apps/public-web && npm run preview

# Public API
docker run -p 8000:8000 -e DATABASE_URL="<connection-string>" secai-radar-public-api:local

# Registry API
docker run -p 8001:8001 -e DATABASE_URL="<connection-string>" secai-radar-registry-api:local
```

### Update Azure
```bash
./scripts/update-swa-config.sh
```

## Current State

✅ **All code implemented and building**
✅ **Database ready**
✅ **Containers building successfully**
⏳ **Ready for Azure deployment**

## Next Action

**Start with Static Web App deployment:**
1. Update Azure Static Web App config (`./scripts/update-swa-config.sh`)
2. Push to main (triggers deployment)
3. Then proceed with database migrations and API deployment
