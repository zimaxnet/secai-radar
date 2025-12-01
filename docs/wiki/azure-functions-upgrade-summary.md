# Azure Functions Upgrade Summary

## Overview
Comprehensive upgrade and review of Azure Functions configuration to ensure compatibility with latest Node.js and Python versions, and proper deployment setup.

## Changes Made

### 1. Python Version Updates
- **Updated `.python_version`**: Changed from `3.9` to `3.12` (latest stable)
- **Created `runtime.txt`**: Added `python-3.12` to explicitly specify Python version for Azure Static Web Apps
- **Updated `api/README.md`**: Added Python 3.12+ requirement in local dev instructions

### 2. Node.js Version Updates
- **Updated GitHub Actions workflow**: Changed from Node.js 20 to Node.js 22 (latest LTS)
- **Workflow now uses**: `actions/setup-node@v4` with `node-version: '22'`

### 3. GitHub Actions Workflow Improvements
Updated `.github/workflows/azure-static-web-apps.yml`:
- Added Python 3.12 setup step using `actions/setup-python@v5`
- Added Python dependency installation step before building
- Upgraded Node.js from 20 to 22
- Added pip caching for faster builds
- Proper dependency installation order: Python dependencies first, then Node.js build

### 4. Requirements.txt Updates
Updated `api/requirements.txt` with version constraints for better compatibility:
- `azure-functions>=1.18.0`
- `azure-data-tables>=12.4.0`
- `azure-storage-blob>=12.19.0`
- `pydantic>=2.0.0`
- `fastjsonschema>=2.19.0`
- `python-multipart>=0.0.6`

### 5. Host.json Configuration
Enhanced `api/host.json`:
- Added `extensionBundle` configuration for Azure Functions v4 runtime
- Added `functionTimeout` set to 5 minutes
- Maintained existing HTTP route prefix configuration

### 6. Function Configuration Verification
Verified all `function.json` files are correctly configured:
- ✅ All 7 functions have `authLevel: "anonymous"` (correct for Static Web Apps)
- ✅ All HTTP triggers properly configured
- ✅ All routes properly defined

Functions verified:
- `api/controls/function.json`
- `api/domains/function.json`
- `api/gaps/function.json`
- `api/import_controls/function.json`
- `api/summary/function.json`
- `api/tenant_tools/function.json`
- `api/tools/function.json`

### 7. Documentation Updates
- **Updated `docs/deployment.md`**: 
  - Changed troubleshooting section to reflect Node.js 22 and Python 3.12
  - Updated CI/CD workflow description

## Current Configuration

### Runtime Versions
- **Python**: 3.12.6 (latest stable)
- **Node.js**: 22.x (latest LTS)
- **Azure Functions Runtime**: v4.x (via extensionBundle)

### Local Environment
- Python: 3.12.6 ✅
- Node.js: v25.1.0 ✅
- pip: 24.2 ✅

### Deployment Configuration
- **API Location**: `/api`
- **App Location**: `/web`
- **Output Location**: `dist`
- **Python Runtime**: Specified via `runtime.txt` (python-3.12)

## Next Steps

1. **Commit and Push Changes**: All changes are ready to be committed
2. **Monitor GitHub Actions**: The workflow will automatically:
   - Install Python 3.12 dependencies
   - Build with Node.js 22
   - Deploy to Azure Static Web Apps
3. **Verify Deployment**: Check Azure Portal for successful deployment
4. **Test API Endpoints**: Verify all Azure Functions are working correctly

## Files Modified

1. `api/.python_version` - Updated to 3.12
2. `api/runtime.txt` - Created (new file)
3. `api/requirements.txt` - Added version constraints
4. `api/host.json` - Added extensionBundle and timeout
5. `api/README.md` - Updated Python version requirement
6. `.github/workflows/azure-static-web-apps.yml` - Major updates for Python 3.12 and Node.js 22
7. `docs/deployment.md` - Updated version references

## Verification Checklist

- [x] Python version updated to 3.12
- [x] Node.js version updated to 22
- [x] GitHub Actions workflow updated
- [x] Requirements.txt has version constraints
- [x] Host.json configured for v4 runtime
- [x] All function.json files verified
- [x] Documentation updated
- [x] Runtime.txt created for Azure
- [x] No linter errors

## Notes

- Azure Static Web Apps will automatically detect Python 3.12 from `runtime.txt`
- The extensionBundle in host.json ensures compatibility with Azure Functions v4 runtime
- All functions are configured with `anonymous` auth level, which is correct for Static Web Apps (auth is handled at the SWA level)
- The workflow now properly installs Python dependencies before deployment, ensuring all packages are available

