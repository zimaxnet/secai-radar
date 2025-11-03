# New Deployment Approach - Standalone Function App

## Overview

After repeated failures with integrated Azure Functions in Static Web Apps, we've moved to a **separate Azure Function App** approach. This provides:

- ✅ Better error visibility and logging
- ✅ Independent scaling and deployment
- ✅ Easier debugging and troubleshooting
- ✅ More reliable deployment process
- ✅ Standard Azure Functions support

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│  Static Web App     │  HTTP   │  Azure Function App  │
│  (Frontend)         │ ──────> │  (API Backend)       │
│  secai-radar        │         │  secai-radar-api     │
└─────────────────────┘         └──────────────────────┘
```

## Prerequisites

- Azure CLI installed and authenticated
- GitHub repository: `zimaxnet/secai-radar`
- Resource group: `secai-radar-rg` (already exists)
- Storage account: `secairadar587d35` (already exists)

## Step 1: Create Function App Resources

Run the provisioning script:

```bash
cd scripts
./create-function-app.sh
```

Or manually via Azure CLI:

```bash
RG="secai-radar-rg"
LOC="centralus"
FUNCTION_APP_NAME="secai-radar-api"
STORAGE_ACCOUNT="secairadar587d35"
APP_SERVICE_PLAN="secai-radar-functions-plan"
PYTHON_VERSION="3.12"

# Get storage connection string
STORAGE_CONN=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RG" \
  --query connectionString \
  --output tsv)

# Create App Service Plan
az functionapp plan create \
  --name "$APP_SERVICE_PLAN" \
  --resource-group "$RG" \
  --location "$LOC" \
  --sku Y1 \
  --is-linux

# Create Function App
az functionapp create \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --storage-account "$STORAGE_ACCOUNT" \
  --plan "$APP_SERVICE_PLAN" \
  --runtime python \
  --runtime-version "$PYTHON_VERSION" \
  --functions-version 4 \
  --os-type Linux

# Configure app settings
az functionapp config appsettings set \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "AzureWebJobsStorage=$STORAGE_CONN" \
    "TABLES_CONN=$STORAGE_CONN" \
    "BLOBS_CONN=$STORAGE_CONN" \
    "BLOB_CONTAINER=assessments" \
    "TENANT_ID=NICO" \
    "FUNCTIONS_EXTENSION_VERSION=~4" \
    "FUNCTIONS_WORKER_RUNTIME=python" \
    "PYTHON_VERSION=$PYTHON_VERSION"

# Configure CORS
az functionapp cors add \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --allowed-origins \
    "https://secai-radar.zimax.net" \
    "https://purple-moss-0942f9e10.3.azurestaticapps.net" \
    "http://localhost:5173" \
    "http://localhost:3000"
```

## Step 2: Get Deployment Credentials

Get the publish profile for GitHub Actions:

```bash
az functionapp deployment list-publishing-profiles \
  --name "secai-radar-api" \
  --resource-group "secai-radar-rg" \
  --xml
```

Copy the entire XML output (it's the publish profile).

## Step 3: Configure GitHub Secrets

1. Go to GitHub repository: `zimaxnet/secai-radar`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
5. Value: Paste the XML publish profile from Step 2
6. Click **Add secret**

## Step 4: Get Function App URL

```bash
az functionapp show \
  --name "secai-radar-api" \
  --resource-group "secai-radar-rg" \
  --query defaultHostName \
  --output tsv
```

This will output something like: `secai-radar-api.azurewebsites.net`

The Function App API URL will be: `https://secai-radar-api.azurewebsites.net/api`

## Step 5: Update Web App Configuration

Update the web app to use the Function App URL:

1. Option A: Set environment variable in build (recommended)
   - Update `.github/workflows/azure-static-web-apps.yml` to pass the Function App URL
   - Or set it as a build-time environment variable

2. Option B: Use environment variable in Static Web App settings
   - Go to Azure Portal → Static Web App → `secai-radar` → Configuration
   - Add application setting: `VITE_API_BASE=https://secai-radar-api.azurewebsites.net/api`

For local development, create `web/.env.local`:
```
VITE_API_BASE=http://localhost:7071/api
```

## Step 6: Deploy

### Deploy Function App

The Function App will deploy automatically on push to `main` branch (when `api/**` files change), or manually via:

```bash
# Trigger workflow manually from GitHub Actions UI
# Or push changes to api/ directory
```

### Deploy Static Web App

The Static Web App will deploy automatically on push to `main` branch, or manually via:

```bash
# Trigger workflow manually from GitHub Actions UI
# Or push changes to web/ directory
```

## Deployment Workflows

### Function App Deployment (`.github/workflows/azure-functions-deploy.yml`)
- Triggers on changes to `api/**` directory
- Installs Python dependencies
- Deploys to Azure Function App

### Static Web App Deployment (`.github/workflows/azure-static-web-apps.yml`)
- Triggers on push to `main`
- Builds React web app
- Deploys to Static Web App (no API integration)

## Verification

1. **Check Function App is running:**
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```

2. **Check Static Web App:**
   ```bash
   curl https://secai-radar.zimax.net
   ```

3. **Verify CORS:**
   - Open browser DevTools
   - Navigate to Static Web App
   - Check Network tab for API calls
   - Should not see CORS errors

## Troubleshooting

### Function App Deployment Fails

1. Check GitHub Actions logs
2. Verify `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` secret is correct
3. Verify Function App exists and is accessible
4. Check Function App logs in Azure Portal

### CORS Errors

1. Verify CORS origins are configured correctly:
   ```bash
   az functionapp cors show \
     --name "secai-radar-api" \
     --resource-group "secai-radar-rg"
   ```

2. Add your domain if missing:
   ```bash
   az functionapp cors add \
     --name "secai-radar-api" \
     --resource-group "secai-radar-rg" \
     --allowed-origins "https://your-domain.com"
   ```

### API Not Responding

1. Check Function App status in Azure Portal
2. View Function App logs:
   ```bash
   az functionapp log tail \
     --name "secai-radar-api" \
     --resource-group "secai-radar-rg"
   ```

3. Test function directly:
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```

## Differences from Previous Approach

| Previous (Integrated) | New (Standalone) |
|----------------------|------------------|
| Functions deployed with SWA | Functions deployed separately |
| Single deployment workflow | Two separate workflows |
| Limited error visibility | Full Azure Functions logging |
| SWA-managed Functions | Standard Azure Function App |
| Harder to debug | Easier to troubleshoot |

## Next Steps

1. ✅ Create Function App resources
2. ✅ Configure GitHub secrets
3. ✅ Update web app API configuration
4. ✅ Deploy and verify
5. ✅ Monitor and optimize

## Useful Commands

```bash
# Get Function App URL
az functionapp show --name secai-radar-api -g secai-radar-rg --query defaultHostName -o tsv

# View Function App logs
az functionapp log tail --name secai-radar-api -g secai-radar-rg

# Restart Function App
az functionapp restart --name secai-radar-api -g secai-radar-rg

# List Function App settings
az functionapp config appsettings list --name secai-radar-api -g secai-radar-rg

# Update CORS
az functionapp cors add --name secai-radar-api -g secai-radar-rg --allowed-origins "https://new-domain.com"
```

