# 🚨 Enable Authentication - CRITICAL STEP

## Current Status

The 401 error persists because **authentication is not enabled** in Azure Portal. The REST API configuration was sent, but authentication must be **manually enabled** in the Azure Portal.

## ⚠️ Required Action

You **MUST** complete this in Azure Portal - it cannot be done via CLI:

### Step 1: Open Azure Portal

1. Go to: https://portal.azure.com
2. Navigate to: **Static Web App** → `secai-radar` → **Authentication** (left menu)

### Step 2: Enable Microsoft Identity Provider

1. **Click**: "Add identity provider"
2. **Select**: "Microsoft (Azure AD / Entra ID)"
3. **Choose**: "Pick an existing app registration in this directory"
4. **Select**: Search for or select `secai-radar-auth` (App ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
5. **Click**: "Add"

### Step 3: Verify

After adding, you should see:
- **Microsoft** listed under "Identity providers"
- Status: **Enabled** (green checkmark)

### Step 4: Test

1. Wait 1-2 minutes for changes to propagate
2. Visit: https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
3. **Expected**: Should redirect to Microsoft login (not 401 error)

## Why This Is Required

- Azure CLI doesn't fully support Static Web App authentication configuration
- The REST API call we sent creates the config, but the provider must be **enabled** via Portal
- Without enabling in Portal, the authentication endpoint won't work

## Quick Links

- **Direct link to Authentication**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/authentication
- **App Registration**: https://portal.azure.com/#@zimax.net/resource/Microsoft.AAD/RegisteredApplications/1cd314e6-933a-4bf9-b889-ffe04a815b98

---

**This is the ONLY step blocking authentication!** Once enabled in Portal, the 401 will become a redirect to login. 🚀

