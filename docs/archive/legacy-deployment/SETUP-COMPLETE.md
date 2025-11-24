# ✅ Function App Setup Complete!

## What Was Done

1. ✅ **Function App Created**: `secai-radar-api` (Consumption plan)
2. ✅ **App Settings Configured**: All required environment variables set
3. ✅ **CORS Configured**: Allowed origins for Static Web App and localhost
4. ✅ **Managed Identity Enabled**: System-assigned identity for future use
5. ✅ **Publish Profile Saved**: `function-app-publish-profile.xml`

## Function App Details

- **Name**: `secai-radar-api`
- **URL**: `https://secai-radar-api.azurewebsites.net`
- **API Base URL**: `https://secai-radar-api.azurewebsites.net/api`
- **Resource Group**: `secai-radar-rg`
- **Region**: Central US
- **Plan**: Consumption (serverless)

## Next Steps - Configure GitHub Secrets

### Step 1: Add Function App Publish Profile

1. Go to GitHub repository: `zimaxnet/secai-radar`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. **Name**: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
5. **Value**: Copy the entire contents of `function-app-publish-profile.xml` file
   ```bash
   cat function-app-publish-profile.xml
   ```
6. Click **Add secret**

### Step 2: Add API Base URL (Optional but Recommended)

1. In GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name**: `VITE_API_BASE`
4. **Value**: `https://secai-radar-api.azurewebsites.net/api`
5. Click **Add secret**

**Alternative**: You can also set this in Azure Static Web App settings instead:
- Azure Portal → Static Web App → `secai-radar` → **Configuration**
- Add application setting: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

## Deploy

Once GitHub Secrets are configured:

1. **Deploy Function App**:
   - Push changes to `api/**` directory, OR
   - Manually trigger workflow: `.github/workflows/azure-functions-deploy.yml`

2. **Deploy Static Web App**:
   - Push changes to `web/**` directory, OR
   - Manually trigger workflow: `.github/workflows/azure-static-web-apps.yml`

## Verify Deployment

### Test Function App Directly

```bash
# Test domains endpoint
curl https://secai-radar-api.azurewebsites.net/api/domains

# Test tools endpoint
curl https://secai-radar-api.azurewebsites.net/api/tools
```

### Test from Static Web App

1. Open your Static Web App in browser
2. Open DevTools → Network tab
3. Navigate through the app
4. Verify API calls are going to `https://secai-radar-api.azurewebsites.net/api`
5. Check for CORS errors (should be none)

### Check Function App Logs

```bash
az functionapp log tail \
  --name secai-radar-api \
  --resource-group secai-radar-rg
```

## Configuration Summary

### Function App Settings
- `AzureWebJobsStorage` - Storage connection string
- `TABLES_CONN` - Storage connection string
- `BLOBS_CONN` - Storage connection string
- `BLOB_CONTAINER` - `assessments`
- `TENANT_ID` - `NICO`
- `FUNCTIONS_EXTENSION_VERSION` - `~4`
- `FUNCTIONS_WORKER_RUNTIME` - `python`
- `PYTHON_VERSION` - `3.12`

### CORS Allowed Origins
- `https://secai-radar.zimax.net`
- `https://purple-moss-0942f9e10.3.azurestaticapps.net`
- `http://localhost:5173` (local dev)
- `http://localhost:3000` (local dev)

## Troubleshooting

### Function App Not Deploying

1. Verify `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` secret is correct
2. Check GitHub Actions workflow logs
3. Verify Function App exists and is running:
   ```bash
   az functionapp show --name secai-radar-api --resource-group secai-radar-rg
   ```

### CORS Errors

1. Verify CORS origins:
   ```bash
   az functionapp cors show --name secai-radar-api --resource-group secai-radar-rg
   ```

2. Add missing origin:
   ```bash
   az functionapp cors add \
     --name secai-radar-api \
     --resource-group secai-radar-rg \
     --allowed-origins "https://your-domain.com"
   ```

### API Not Responding

1. Check Function App status in Azure Portal
2. View logs:
   ```bash
   az functionapp log tail --name secai-radar-api --resource-group secai-radar-rg
   ```
3. Test function directly:
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```

## Useful Commands

```bash
# Get Function App URL
az functionapp show --name secai-radar-api --resource-group secai-radar-rg --query defaultHostName -o tsv

# View Function App logs
az functionapp log tail --name secai-radar-api --resource-group secai-radar-rg

# Restart Function App
az functionapp restart --name secai-radar-api --resource-group secai-radar-rg

# List Function App settings
az functionapp config appsettings list --name secai-radar-api --resource-group secai-radar-rg

# Update CORS
az functionapp cors add --name secai-radar-api --resource-group secai-radar-rg --allowed-origins "https://new-domain.com"
```

## Files Created

- `function-app-publish-profile.xml` - Publish profile for GitHub Secrets
- `docs/SETUP-COMPLETE.md` - This file

## Next Actions

1. ✅ Add `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` to GitHub Secrets
2. ✅ Add `VITE_API_BASE` to GitHub Secrets (or Static Web App settings)
3. ✅ Deploy Function App (push to `main` or trigger workflow)
4. ✅ Deploy Static Web App (push to `main` or trigger workflow)
5. ✅ Verify everything works

---

**Status**: Function App is ready for deployment! 🚀

