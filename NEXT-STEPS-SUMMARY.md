# Next Steps Summary

## ✅ What's Been Completed

All implementation phases are complete:
- **Phase 0:** Monorepo, CI/CD, Infrastructure templates
- **Phase 1:** Database, Public API, Frontend, Publishing
- **Phase 2:** Scoring library, 7 workers, Pipeline
- **Phase 3:** Auth, RBAC, Registry API
- **Phase 4:** Graph builder, Graph API, Security

**167 files created** across the monorepo structure.

## 🎯 Immediate Next Steps

### 1. Update Azure Static Web App (5 minutes)

The Azure Static Web App still points to the old `web/` directory. Update it:

**Option A: Use Script**
```bash
./scripts/update-swa-config.sh
```

**Option B: Azure Portal**
1. Go to: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
2. Configuration → Build Configuration
3. Update:
   - App location: `apps/public-web`
   - Output location: `dist`
   - API location: (empty)

### 2. Database Setup (5 minutes) ✅ Ready

**Using existing PostgreSQL in `ctxeco-rg`:**

```bash
# Quick setup
az postgres flexible-server db create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --database-name secairadar

# Allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Run migrations (set DATABASE_URL first)
cd apps/public-api
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
python scripts/migrate.py
```

**Server Details:**
- FQDN: `ctxeco-db.postgres.database.azure.com`
- Admin: `ctxecoadmin`
- Version: PostgreSQL 16

See `QUICK-START-DATABASE.md` for complete guide.

### 3. Deploy Infrastructure (30 minutes)

Deploy without PostgreSQL (using existing):

```bash
cd infra
az deployment group create \
  --resource-group secai-radar-rg \
  --template-file mcp-infrastructure-existing-db.bicep \
  --parameters @parameters/dev-existing-db.bicepparam
```

This creates:
- Storage Account
- Key Vault
- Container Apps Environment
- Container Registry
- Log Analytics

### 4. Deploy Public API (20 minutes)

```bash
# Build and push container
cd apps/public-api
az acr build --registry <ACR_NAME> --image secai-radar-public-api:latest .

# Deploy to Container Apps
az containerapp create \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --environment <ENV_NAME> \
  --image <ACR_NAME>.azurecr.io/secai-radar-public-api:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
```

### 5. Configure GitHub Secrets (5 minutes)

Add to GitHub repository secrets:
- `VITE_API_BASE` = `https://<your-api-url>/api`
- `DATABASE_URL` = `postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar`

### 6. Test Deployment (10 minutes)

1. Push a commit to trigger deployment
2. Verify Static Web App deploys
3. Test API health endpoint
4. Test frontend loads

## 📋 Full Checklist

See `DEPLOYMENT-NEXT-STEPS.md` for complete deployment guide.

## 🔗 Quick Links

- **Azure Portal (Static Web App):** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
- **Azure Portal (PostgreSQL):** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview
- **GitHub Repo:** https://github.com/zimaxnet/secai-radar
- **Implementation Details:** `IMPLEMENTATION-COMPLETE.md`
- **Deployment Guide:** `DEPLOYMENT-NEXT-STEPS.md`
- **Database Setup:** `QUICK-START-DATABASE.md`
