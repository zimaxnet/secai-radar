# Fix Role Assignments API Path in Azure Portal

## Issue

The build is still showing an error about `"staticwebapp.json"` not being a valid roles source, even though the `staticwebapp.config.json` file has been updated to `"DEFAULT"`.

This is because **Azure Portal has a separate setting** for "Role assignments API path" that may be overriding the config file.

## Solution: Update Azure Portal Setting

### Step 1: Go to Authentication Page

**Direct Link**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/authentication

### Step 2: Update Role Assignments API Path

1. On the **Authentication** page, find the **"Role assignments API path"** field
2. It may currently show: `staticwebapp.json`
3. **Change it to**: `DEFAULT` (or leave it empty for DEFAULT)
4. **Click "Save"**

### Alternative: Use API Path

If you want to use an API endpoint for roles later:

1. Set **"Role assignments API path"** to: `/api/roles`
2. Create the API endpoint in your Function App
3. The endpoint should return JSON with user roles

## Why This Matters

The Azure Portal setting for "Role assignments API path" can override the `rolesSource` in `staticwebapp.config.json`. Both need to be set correctly for the configuration to work.

## Current Configuration

- **Config File**: `rolesSource: "DEFAULT"` ✅
- **Portal Setting**: Should be `DEFAULT` or empty (needs to be updated)

## After Updating Portal

1. **Save** the changes in Azure Portal
2. **Wait 1-2 minutes** for changes to propagate
3. **Trigger a new deployment** or wait for the next build
4. **Verify** the build logs no longer show the error

---

**Status**: The config file is correct. Update the Azure Portal setting to match! 🚀

