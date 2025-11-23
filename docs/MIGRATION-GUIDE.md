# Migration Guide: From Integrated Functions to Standalone Function App

## Why This Migration?

The integrated Azure Functions approach in Static Web Apps has been causing repeated deployment failures. This migration moves to a **standalone Azure Function App**, which provides:

- ✅ Reliable deployments with better error visibility
- ✅ Independent scaling and monitoring
- ✅ Standard Azure Functions tooling and support
- ✅ Easier debugging and troubleshooting

## Migration Steps

### Step 1: Create Function App Resources

Run the provisioning script:

```bash
cd scripts
./create-function-app.sh
```

This will:
- Create an App Service Plan (Consumption/Linux)
- Create the Function App (`secai-radar-api`)
- Configure all required app settings
- Set up CORS for the Static Web App

### Step 2: Get Deployment Credentials

Get the publish profile for GitHub Actions:

```bash
az functionapp deployment list-publishing-profiles \
  --name "secai-radar-api" \
  --resource-group "secai-radar-rg" \
  --xml > function-app-publish-profile.xml
```

### Step 3: Configure GitHub Secrets

1. Go to GitHub repository: `zimaxnet/secai-radar`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
5. Value: Copy the entire XML content from the file created in Step 2
6. Click **Add secret**

### Step 4: Get Function App URL

```bash
az functionapp show \
  --name "secai-radar-api" \
  --resource-group "secai-radar-rg" \
  --query defaultHostName \
  --output tsv
```

This outputs: `secai-radar-api.azurewebsites.net`

The API base URL is: `https://secai-radar-api.azurewebsites.net/api`

### Step 5: Update Web App API Configuration

The web app is already configured to use `VITE_API_BASE` environment variable. You have two options:

**Option A: Set in GitHub Secrets (Recommended)**
1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add secret: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

**Option B: Set in Static Web App Settings**
1. Azure Portal → Static Web App → `secai-radar` → **Configuration**
2. Add application setting: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

For local development, create `web/.env.local`:
```
VITE_API_BASE=http://localhost:7071/api
```

### Step 6: Deploy

1. **Deploy Function App:**
   - Push changes or trigger workflow manually
   - The Function App will deploy automatically when `api/**` files change

2. **Deploy Static Web App:**
   - Push changes or trigger workflow manually
   - The Static Web App will deploy without the integrated API

### Step 7: Verify

1. **Test Function App directly:**
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```

2. **Test from Static Web App:**
   - Open browser DevTools
   - Navigate to your Static Web App
   - Check Network tab for API calls
   - Should not see CORS errors

3. **Check Function App logs:**
   ```bash
   az functionapp log tail \
     --name "secai-radar-api" \
     --resource-group "secai-radar-rg"
   ```

## What Changed?

### Before (Integrated Functions)
- Functions deployed with Static Web App
- Single deployment workflow
- Limited error visibility
- Deployment failures were hard to debug

### After (Standalone Function App)
- Functions deployed separately
- Two independent workflows
- Full Azure Functions logging
- Standard Azure Functions deployment

## Rollback Plan

If you need to rollback:

1. Remove the standalone Function App (or keep it for reference)
2. Restore `.github/workflows/azure-static-web-apps.yml` to include `api_location: "api"`
3. Revert web app API configuration to use `/api` paths

## Support

If you encounter issues:
1. Check the [deployment-new-approach.md](./deployment-new-approach.md) guide
2. Review Function App logs in Azure Portal
3. Check GitHub Actions workflow logs

