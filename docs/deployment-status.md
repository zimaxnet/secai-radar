# Deployment Status

## ✅ Completed Steps

### 1. Azure Resources
- ✅ Resource Group: `secai-radar-rg` (Central US)
- ✅ Storage Account: `secairadar587d35` (Standard_LRS)
- ✅ Static Web App: `secai-radar` (Free tier)
  - Default hostname: `purple-moss-0942f9e10.3.azurestaticapps.net`

### 2. DNS Configuration
- ✅ CNAME record created: `secai-radar.zimax.net` → `purple-moss-0942f9e10.3.azurestaticapps.net`
- ⏳ Custom domain verification pending (may take a few minutes)

### 3. GitHub Configuration
- ✅ GitHub Actions workflow created (`.github/workflows/azure-static-web-apps.yml`)
- ✅ Deployment token added to GitHub secrets: `AZURE_STATIC_WEB_APPS_API_TOKEN`

### 4. Application Settings
- ✅ `AzureWebJobsStorage` - Storage account connection string
- ✅ `TABLES_CONN` - Storage account connection string
- ✅ `BLOBS_CONN` - Storage account connection string
- ✅ `BLOB_CONTAINER` - `assessments`
- ✅ `TENANT_ID` - `NICO`

## 🔄 Next Steps (Manual)

### 1. Custom Domain Verification
1. Go to Azure Portal → Static Web App → `secai-radar` → Custom domains
2. Verify `secai-radar.zimax.net` is listed
3. Wait for DNS validation to complete (may take 5-30 minutes)
4. SSL certificate will be automatically provisioned

### 2. Authentication Setup (Entra ID)
1. Go to Azure Portal → Static Web App → `secai-radar` → Authentication
2. Click "Add identity provider"
3. Select "Microsoft (Azure AD / Entra ID)"
4. Choose "Create new app registration" or use existing
5. Configure redirect URL: `https://secai-radar.zimax.net/.auth/login/aad/callback`

### 3. GitHub Connection
1. Go to Azure Portal → Static Web App → `secai-radar` → Deployment
2. Verify GitHub connection is linked to `zimaxnet/secai-radar`
3. Branch: `main`
4. Build details:
   - App location: `/web`
   - API location: `/api`
   - Output location: `dist`

### 4. Trigger Deployment
1. Push any commit to `main` branch (or commit is already pushed)
2. Check GitHub Actions tab for workflow status
3. Monitor deployment in Azure Portal

## 📋 Verification Checklist

- [ ] DNS CNAME record is propagated (check with `dig secai-radar.zimax.net CNAME`)
- [ ] Custom domain shows as "Validated" in Azure Portal
- [ ] SSL certificate is provisioned for custom domain
- [ ] Entra ID authentication is configured
- [ ] GitHub Actions workflow runs successfully
- [ ] Application accessible at `https://secai-radar.zimax.net`
- [ ] API endpoints respond correctly

## 🔗 Useful Links

- **Azure Portal**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/overview
- **GitHub Repository**: https://github.com/zimaxnet/secai-radar
- **Default Hostname**: https://purple-moss-0942f9e10.3.azurestaticapps.net
- **Custom Domain** (when ready): https://secai-radar.zimax.net

