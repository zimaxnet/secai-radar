# Deployment Debugging Guide

## Current Issue

**Symptom**: Build succeeds, but deployment fails with "Failed to deploy the Azure Functions"

**What's Working**:
- ✅ Web app builds successfully
- ✅ Oryx builds Functions app successfully
- ✅ Dependencies install correctly
- ✅ Artifacts upload successfully

**What's Failing**:
- ❌ Functions deployment fails after upload
- ❌ No specific error message in logs

## Possible Causes

### 1. Missing Application Settings
Functions may be failing at startup because required environment variables are not set.

**Required Settings**:
- `AzureWebJobsStorage` - Storage connection string
- `TABLES_CONN` - Storage connection string
- `BLOBS_CONTAINER` - Storage connection string
- `BLOB_CONTAINER` - `assessments`
- `TENANT_ID` - `NICO`

**Verify**:
```bash
az staticwebapp appsettings list -n secai-radar -g secai-radar-rg
```

### 2. Functions Runtime Startup Failure
Functions may be failing during initialization, possibly due to:
- Import errors
- Missing dependencies
- Connection string validation failures

### 3. Application Settings Not Applied
Settings may not be properly configured or accessible during Function startup.

## Debugging Steps

### Step 1: Check Azure Portal
1. Go to Azure Portal → Static Web App → `secai-radar`
2. Navigate to **Functions** in the left menu
3. Check if any functions are listed
4. Click on a function (e.g., `domains`) to see detailed logs

### Step 2: Check Deployment History
1. Go to **Deployment** in the Static Web App
2. Click on the latest deployment
3. Check for detailed error messages

### Step 3: Test Function Endpoints
Try accessing the function endpoints directly:
- `https://purple-moss-0942f9e10.3.azurestaticapps.net/api/domains`
- `https://secai-radar.zimax.net/api/domains` (if custom domain is configured)

### Step 4: Check Application Insights (if enabled)
1. Go to Static Web App → **Application Insights**
2. Check for errors or exceptions

### Step 5: Re-verify Application Settings
```bash
# Get connection string
SA=secairadar587d35
RG=secai-radar-rg
CONN_STR=$(az storage account show-connection-string -n "$SA" -g "$RG" --query connectionString -o tsv)

# Set all required settings
SWA_NAME=secai-radar
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "AzureWebJobsStorage=$CONN_STR"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "TABLES_CONN=$CONN_STR"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "BLOBS_CONN=$CONN_STR"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "BLOB_CONTAINER=assessments"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "TENANT_ID=NICO"
```

## Next Steps

1. Check Azure Portal for detailed error messages
2. Verify application settings are correctly configured
3. Test function endpoints directly
4. Check if functions are actually deployed (may be deployed but not starting)

## Alternative: Temporarily Disable Functions

If functions continue to fail, you can temporarily:
1. Remove `api_location: "api"` from the workflow
2. Deploy web app only to verify it works
3. Re-add functions once the issue is resolved

