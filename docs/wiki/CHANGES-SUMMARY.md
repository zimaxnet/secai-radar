# Changes Summary - New Deployment Approach

## Overview

After repeated failures with integrated Azure Functions in Static Web Apps, we've migrated to a **standalone Azure Function App** approach. This provides better reliability, easier debugging, and more control over deployments.

## What Changed

### Architecture
- **Before**: Functions deployed as part of Static Web App (integrated)
- **After**: Functions deployed as separate Azure Function App (standalone)

### Deployment Workflows
- **Before**: Single workflow deploying both web app and API together
- **After**: Two separate workflows:
  - `.github/workflows/azure-static-web-apps.yml` - Deploys web app only
  - `.github/workflows/azure-functions-deploy.yml` - Deploys Function App separately

### Configuration
- **Before**: API configured via `api_location` in Static Web App
- **After**: API URL configured via `VITE_API_BASE` environment variable

## Files Created

1. **`.github/workflows/azure-functions-deploy.yml`**
   - New workflow for deploying Function App separately
   - Triggers on changes to `api/**` directory

2. **`scripts/create-function-app.sh`**
   - Script to provision Function App resources
   - Configures app settings, CORS, and managed identity

3. **`docs/deployment-new-approach.md`**
   - Complete deployment guide for the new approach
   - Step-by-step instructions

4. **`docs/MIGRATION-GUIDE.md`**
   - Migration steps from old to new approach
   - Rollback plan included

5. **`docs/QUICK-START.md`**
   - Quick 5-step setup guide
   - Fast reference for getting started

## Files Modified

1. **`.github/workflows/azure-static-web-apps.yml`**
   - Removed `api_location: "api"` parameter
   - Added `VITE_API_BASE` environment variable for build
   - Updated comments

2. **`docs/deployment-status.md`**
   - Updated to reflect new approach
   - Added links to new guides
   - Updated verification checklist

## What You Need to Do

### Step 1: Create Function App
Run the provisioning script:
```bash
cd scripts
./create-function-app.sh
```

### Step 2: Configure GitHub Secrets
1. Get Function App publish profile
2. Add `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` secret
3. Add `VITE_API_BASE` secret (or configure in Static Web App settings)

### Step 3: Deploy
- Push to `main` branch
- Function App deploys when `api/**` files change
- Static Web App deploys when `web/**` files change

## Benefits

✅ **Better Reliability**: Standard Azure Functions deployment process
✅ **Better Debugging**: Full Azure Functions logging and monitoring
✅ **Independent Scaling**: Scale web app and API independently
✅ **Easier Troubleshooting**: Clear separation of concerns
✅ **Standard Tooling**: Use standard Azure Functions tools and documentation

## Next Steps

1. Follow the [Quick Start Guide](docs/wiki/QUICK-START.md)
2. Review the [Full Deployment Guide](docs/wiki/deployment-new-approach.md)
3. Deploy and verify everything works
4. Monitor and optimize as needed

## Support

If you encounter issues:
- Check [deployment-new-approach.md](docs/wiki/deployment-new-approach.md) for troubleshooting
- Review Function App logs in Azure Portal
- Check GitHub Actions workflow logs

