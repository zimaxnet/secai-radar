# Troubleshooting Azure Functions Deployment

## Common Issues

### 1. Missing Application Settings

If Functions deployment fails, verify all required application settings are configured:

**Required Settings:**
- `AzureWebJobsStorage` - Storage account connection string
- `TABLES_CONN` - Storage account connection string (can be same as AzureWebJobsStorage)
- `BLOBS_CONN` - Storage account connection string (can be same as AzureWebJobsStorage)
- `BLOB_CONTAINER` - `assessments`
- `TENANT_ID` - `NICO`

**Check Settings:**
```bash
az staticwebapp appsettings list -n secai-radar -g secai-radar-rg
```

### 2. Import Path Issues

All functions use `from shared.utils import ...`. Verify:
- `api/shared/__init__.py` exists (empty file is fine)
- All function directories have `__init__.py` files
- No circular import issues

### 3. Python Version

Functions runtime uses Python 3.11 (from Oryx logs), which is compatible with code written for 3.9.

### 4. Deployment Failure Debugging

Check deployment logs in:
- GitHub Actions → Workflow run → Deploy to Azure Static Web Apps step
- Azure Portal → Static Web App → Deployment history

### 5. Function App Validation

Functions may fail validation if:
- `function.json` has invalid syntax
- Required bindings are missing
- Import paths are incorrect

## Quick Fixes

### Re-verify Application Settings
```bash
RG=secai-radar-rg
SA=secairadar587d35
SWA_NAME=secai-radar
CONN_STR=$(az storage account show-connection-string -n "$SA" -g "$RG" --query connectionString -o tsv)

az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "AzureWebJobsStorage=$CONN_STR"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "TABLES_CONN=$CONN_STR"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "BLOBS_CONN=$CONN_STR"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "BLOB_CONTAINER=assessments"
az staticwebapp appsettings set -n "$SWA_NAME" -g "$RG" --setting-names "TENANT_ID=NICO"
```

### Check Function Logs
In Azure Portal:
1. Go to Static Web App → `secai-radar`
2. Navigate to Functions
3. Click on a function (e.g., `domains`)
4. Check Logs or Monitor for errors

