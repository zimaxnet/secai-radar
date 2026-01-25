# Deployment Next Steps

## Current Status ✅

All implementation phases (0-4) are complete. The codebase is ready for deployment and testing.

## Immediate Next Steps

### 1. Update Azure Static Web App Configuration ⚠️

**Issue:** The Azure Static Web App is still configured to deploy from `web/` directory, but we've moved to `apps/public-web/`.

**Action Required:**
1. Update Azure Portal Static Web App settings:
   - Go to: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
   - Navigate to **Configuration** → **Build Configuration**
   - Update:
     - **App location:** `apps/public-web`
     - **Output location:** `dist`
     - **API location:** (leave empty - API is separate Container App)

2. Or use Azure CLI:
```bash
az staticwebapp update \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --app-location "apps/public-web" \
  --output-location "dist" \
  --api-location ""
```

Or use the provided script:
```bash
./scripts/update-swa-config.sh
```

### 2. Database Setup 🗄️ (Using Existing PostgreSQL) ✅

**We're using the existing PostgreSQL server in `ctxeco-rg`.**

**Server Details:**
- **FQDN:** `ctxeco-db.postgres.database.azure.com`
- **Admin User:** `ctxecoadmin`
- **Version:** PostgreSQL 16
- **State:** Ready

**Quick Setup:**
```bash
# 1. Create database
az postgres flexible-server db create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --database-name secairadar

# 2. Configure firewall (allow Azure services)
az postgres flexible-server firewall-rule create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# 3. Run migrations (set DATABASE_URL first)
cd apps/public-api
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
python scripts/migrate.py

# 4. Seed sample data (optional)
python scripts/seed.py
```

**Or use helper scripts:**
```bash
./scripts/get-postgres-connection.sh      # Get connection details
./scripts/configure-postgres-firewall.sh  # Configure firewall
./scripts/setup-existing-database.sh     # Create database
```

**See:** `DATABASE-SETUP-EXISTING.md` or `QUICK-START-DATABASE.md` for complete guide.

### 3. Deploy Infrastructure (Without PostgreSQL) 🏗️

Since we're using existing PostgreSQL, deploy infrastructure without database:

```bash
cd infra
az deployment group create \
  --resource-group secai-radar-rg \
  --template-file mcp-infrastructure-existing-db.bicep \
  --parameters @parameters/dev-existing-db.bicepparam
```

This will create:
- Storage Account (evidence, assets, exports)
- Key Vault
- Container Apps Environment
- Container Registry
- Log Analytics Workspace

### 4. Deploy Public API (Container App) 🚀

**Prerequisites:**
- Azure Container Apps Environment created
- Azure Container Registry (ACR) available
- Database connection configured

**Steps:**
1. Build and push container image:
```bash
cd apps/public-api
az acr build --registry <ACR_NAME> --image secai-radar-public-api:latest .
```

2. Deploy to Container Apps:
```bash
az containerapp create \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --environment <CONTAINER_APPS_ENV> \
  --image <ACR_NAME>.azurecr.io/secai-radar-public-api:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL="postgresql://<user>:<pass>@<fqdn>:5432/secairadar"
```

### 5. Configure Environment Variables 🔐

**GitHub Secrets Required:**
- `AZURE_STATIC_WEB_APPS_API_TOKEN` - Already configured
- `VITE_API_BASE` - Set to public API URL (e.g., `https://secai-radar-public-api.<region>.azurecontainerapps.io/api`)
- `DATABASE_URL` - PostgreSQL connection string (store securely, don't commit)

**Azure Container App Settings:**
- `DATABASE_URL` - PostgreSQL connection string
- `METHODOLOGY_VERSION` - Set to `v1.0`

### 6. Test Deployment 🧪

**Checklist:**
- [ ] Static Web App deploys successfully
- [ ] Public API health endpoint responds: `GET /health`
- [ ] Frontend can connect to API
- [ ] Database migrations completed
- [ ] Sample data seeded

### 7. Configure Custom Domain 🌐

**Already Configured:**
- `secairadar.cloud` - Ready for Static Web App

**To Verify:**
1. Check Azure Portal → Static Web App → Custom domains
2. Verify DNS records are correct
3. Test: `https://secairadar.cloud/mcp`

### 8. Set Up Daily Pipeline ⏰

**GitHub Actions Workflow:**
- Already created: `.github/workflows/daily-pipeline.yml`
- Schedule: Daily at 02:30 UTC

**First Run:**
- Manually trigger via GitHub Actions UI
- Monitor logs for each worker stage
- Verify data appears in database

## Testing Checklist

### Phase 0: Foundation
- [ ] Monorepo builds successfully (`npm run build` from root)
- [ ] CI pipeline passes (lint, typecheck, test)
- [ ] Infrastructure Bicep validates

### Phase 1: Public MVP
- [ ] Database schema created
- [ ] All 10 API endpoints respond
- [ ] Frontend pages load with real data
- [ ] RSS/JSON feeds generate correctly
- [ ] ETag caching works

### Phase 2: Automation Pipeline
- [ ] Scoring library tests pass
- [ ] All 7 workers can run independently
- [ ] Daily pipeline workflow executes
- [ ] Data flows through pipeline correctly

### Phase 3: Private Registry
- [ ] Entra ID authentication works
- [ ] RBAC enforces roles correctly
- [ ] Registry API endpoints respond
- [ ] Workspace isolation works

### Phase 4: Graph Explorer
- [ ] Graph builder generates snapshots
- [ ] Graph API endpoint returns data
- [ ] Graph UI renders correctly

## Troubleshooting

### Build Failures
- Check Node.js version (should be 22)
- Verify `package-lock.json` exists in `apps/public-web/`
- Check for TypeScript errors: `npm run typecheck`

### Deployment Failures
- Verify `AZURE_STATIC_WEB_APPS_API_TOKEN` secret is set
- Check Azure Portal for deployment logs
- Verify app_location path matches Azure configuration

### API Connection Issues
- Verify `VITE_API_BASE` environment variable
- Check CORS settings in API
- Verify API is deployed and accessible

### Database Issues
- Verify connection string format
- Check firewall rules allow Container Apps
- Verify database exists and migrations ran
- **Note:** Using existing PostgreSQL in `ctxeco-rg`

## Success Criteria

✅ **Ready for Production When:**
- All tests pass
- All API endpoints respond < 500ms
- Frontend loads and displays real data
- Daily pipeline runs successfully
- No critical security issues
- Monitoring and alerts configured

## Resources

- **Azure Portal (Static Web App):** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
- **Azure Portal (PostgreSQL):** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview
- **GitHub Repo:** https://github.com/zimaxnet/secai-radar
- **Implementation Plan:** `verified_mcp_implementation_plan_2face199.plan.md`
- **Getting Started:** `GETTING-STARTED.md`
- **Database Setup:** `DATABASE-SETUP-EXISTING.md`
