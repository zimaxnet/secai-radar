# Fix 401 Unauthorized Error

## Current Status

The `/tenant` route is returning **401 Unauthorized**, which means:
- ✅ Route protection is working
- ❌ Authentication provider is not fully enabled

## Issue

The authentication configuration was sent via REST API, but it needs to be **completed in Azure Portal** to fully enable the Microsoft identity provider.

## Solution

### Step 1: Complete Authentication Setup in Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Static Web App → `secai-radar`
3. **Click**: **Authentication** in the left menu
4. **Check if "Microsoft" provider is listed**:
   - If **not listed**: Click "Add identity provider" → Select "Microsoft (Azure AD / Entra ID)" → Choose existing app registration `secai-radar-auth` → Click "Add"
   - If **listed but shows "Not configured"**: Click on it → Complete the configuration

5. **Verify the configuration**:
   - App Registration should be: `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
   - Status should be: **Enabled**

### Step 2: Verify App Registration

1. **Go to**: Azure Portal → Azure Active Directory → App registrations
2. **Find**: `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
3. **Check**:
   - **Authentication** → Redirect URIs should include:
     - `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
   - **API permissions** → Should have "Microsoft Graph" → "User.Read" (if needed)

### Step 3: Test Authentication

After completing the setup:

1. **Visit**: https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
2. **Expected behavior**: Should redirect to Microsoft login (not show 401)
3. **After login**: Should redirect back to `/tenant` route

## What Changed

I've updated `staticwebapp.config.json` to:
- Use `rolesSource: "staticwebapp.json"` (more reliable)
- Add `responseOverrides` to redirect 401 to login page

## Verify After Fix

```bash
# Should redirect to login (not return 401)
curl -L https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
```

## If Still Getting 401

1. **Check Authentication Status** in Azure Portal → Static Web App → Authentication
2. **Verify App Registration** is linked correctly
3. **Check Static Web App logs** for authentication errors
4. **Wait a few minutes** after configuration changes (propagation delay)

---

**Status**: Configuration updated. Complete authentication setup in Azure Portal to resolve 401 error. 🚀

