# Next Steps - Updated

## ✅ Completed

1. **All Implementation Phases (0-4)** - Complete
2. **Database Created** - `secairadar` on `ctxeco-db` ✅
3. **Static Web App Builds** - Successfully building ✅
4. **Container Dockerfiles** - Created and ready ✅

## 🎯 Immediate Next Steps

### 1. Build Containers Locally (10 minutes)

```bash
# Build both containers
./scripts/build-containers.sh

# Or individually
cd apps/public-api && docker build -t secai-radar-public-api:local .
cd apps/registry-api && docker build -t secai-radar-registry-api:local .
```

### 2. Test Containers Locally (5 minutes)

```bash
# Test Public API
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar" \
  secai-radar-public-api:local

# In another terminal, test
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/public/health
```

### 3. Update Azure Static Web App (5 minutes)

```bash
./scripts/update-swa-config.sh
```

Or manually in Azure Portal:
- App location: `apps/public-web`
- Output location: `dist`

### 4. Run Database Migrations (5 minutes)

```bash
# Set DATABASE_URL first
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"

# Run migrations
cd apps/public-api
python scripts/migrate.py
```

### 5. Deploy Infrastructure (30 minutes)

```bash
cd infra
az deployment group create \
  --resource-group secai-radar-rg \
  --template-file mcp-infrastructure-existing-db.bicep \
  --parameters @parameters/dev-existing-db.bicepparam
```

### 6. Push Containers to ACR (10 minutes)

```bash
# After infrastructure is deployed, get ACR name
ACR_NAME=$(az acr list --resource-group secai-radar-rg --query "[0].name" -o tsv)

# Build and push
cd apps/public-api
az acr build --registry $ACR_NAME --image secai-radar-public-api:latest .

cd ../registry-api
az acr build --registry $ACR_NAME --image secai-radar-registry-api:latest .
```

### 7. Deploy to Container Apps (15 minutes)

```bash
# Get environment name
ENV_NAME=$(az containerapp env list --resource-group secai-radar-rg --query "[0].name" -o tsv)

# Deploy Public API
az containerapp create \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --environment $ENV_NAME \
  --image $ACR_NAME.azurecr.io/secai-radar-public-api:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
```

## Current Status

- ✅ **Code:** All implemented
- ✅ **Database:** Created and ready
- ✅ **Static Web App:** Builds successfully
- ✅ **Containers:** Dockerfiles ready
- ⏳ **Azure Config:** Needs update (app_location)
- ⏳ **Migrations:** Need to run
- ⏳ **Infrastructure:** Needs deployment
- ⏳ **Containers:** Need to build and deploy

## Quick Reference

**Build SWA:**
```bash
cd apps/public-web && npm run build
```

**Build Containers:**
```bash
./scripts/build-containers.sh
```

**Update Azure:**
```bash
./scripts/update-swa-config.sh
```

**Database:**
- Server: `ctxeco-db.postgres.database.azure.com`
- Database: `secairadar`
- User: `ctxecoadmin`

## Documentation

- **Build Guide:** `LOCAL-BUILD-GUIDE.md`
- **SWA Deploy:** `SWA-BUILD-AND-DEPLOY.md`
- **Database Setup:** `DATABASE-READY.md`
- **Full Deployment:** `DEPLOYMENT-NEXT-STEPS.md`
