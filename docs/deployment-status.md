# Deployment Status

## 🆕 New Approach: Standalone Function App

**Status**: Migrated from integrated Functions to standalone Azure Function App

After repeated failures with integrated Azure Functions in Static Web Apps, we've migrated to a **separate Azure Function App** approach for better reliability and easier debugging.

### Quick Links
- [Quick Start Guide](./QUICK-START.md) - Get started in 5 steps
- [Full Deployment Guide](./deployment-new-approach.md) - Complete setup instructions
- [Migration Guide](./MIGRATION-GUIDE.md) - Migration steps and details

## ✅ Completed Steps

### 1. Azure Resources
- ✅ Resource Group: `secai-radar-rg` (Central US)
- ✅ Storage Account: `secairadar587d35` (Standard_LRS)
- ✅ Static Web App: `secai-radar` (Free tier)
  - Default hostname: `purple-moss-0942f9e10.3.azurestaticapps.net`
- ✅ Function App: `secai-radar-api` (Deployed and working)

### 2. DNS Configuration
- ✅ CNAME record created: `secai-radar.zimax.net` → `purple-moss-0942f9e10.3.azurestaticapps.net`
- ⏳ Custom domain verification pending (may take a few minutes)

### 3. GitHub Configuration
- ✅ GitHub Actions workflow for Static Web App (`.github/workflows/azure-static-web-apps.yml`)
- ✅ GitHub Actions workflow for Function App (`.github/workflows/azure-functions-deploy.yml`)
- ✅ Deployment token added to GitHub secrets: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- ✅ Function App credentials added to GitHub secrets: `AZURE_CREDENTIALS`

### 4. Application Settings
- ✅ Static Web App settings configured
- ✅ Function App settings configured (CORS, storage connections, app settings)

## 🔄 Next Steps (Follow Quick Start)

### 1. Create Function App
Run the provisioning script:
```bash
cd scripts
./create-function-app.sh
```

### 2. Configure GitHub Secrets
1. Get Function App publish profile (see [Quick Start](./QUICK-START.md) Step 2)
2. Add to GitHub Secrets: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
3. Add Function App URL: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

### 3. Deploy
- Push to `main` branch or trigger workflows manually
- Function App deploys when `api/**` files change
- Static Web App deploys when `web/**` files change

### 4. Verify
- Test Function App: `curl https://secai-radar-api.azurewebsites.net/api/domains`
- Test Static Web App in browser
- Check CORS is working (no errors in DevTools)
- Monitor deployment in Azure Portal

## 📋 Verification Checklist

       ### Static Web App
       - [ ] DNS CNAME record is propagated (check with `dig secai-radar.zimax.net CNAME`)
       - [ ] Custom domain shows as "Validated" in Azure Portal
       - [ ] SSL certificate is provisioned for custom domain
       - [x] Entra ID authentication is configured and enabled
       - [x] Static Web App deployment workflow runs successfully
       - [x] Application accessible at `https://purple-moss-0942f9e10.3.azurestaticapps.net`

       ### Function App
       - [x] Function App created and accessible
       - [x] Function App credentials added to GitHub Secrets (`AZURE_CREDENTIALS`)
       - [x] Function App deployment workflow runs successfully
       - [x] Function App URL configured in web app (`VITE_API_BASE`)
       - [x] CORS configured correctly (no CORS errors in browser)
       - [x] API endpoints respond correctly: `curl https://secai-radar-api.azurewebsites.net/api/domains`

## 🔗 Useful Links

- **Azure Portal**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/overview
- **GitHub Repository**: https://github.com/zimaxnet/secai-radar
- **Default Hostname**: https://purple-moss-0942f9e10.3.azurestaticapps.net
- **Custom Domain** (when ready): https://secai-radar.zimax.net

