# Complete Entra ID Authentication Setup

## ✅ What's Been Done

1. ✅ App Registration created: `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
2. ✅ Redirect URIs configured:
   - `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
   - `https://secai-radar.zimax.net/.auth/login/aad/callback`
3. ✅ Authentication configuration sent via REST API
4. ✅ Route protection configured in `staticwebapp.config.json`

## 🔧 Complete Authentication Setup (Azure Portal)

Since Azure CLI doesn't fully support Static Web App authentication configuration, use the Azure Portal:

### Step 1: Configure Authentication in Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Static Web App → `secai-radar`
3. **Click**: **Authentication** in the left menu
4. **Click**: **Add identity provider**
5. **Select**: **Microsoft (Azure AD / Entra ID)**
6. **Choose**: **Pick an existing app registration in this directory**
   - **App registration**: `secai-radar-auth` (or search for `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
7. **Click**: **Add**

### Step 2: Verify Configuration

1. **Check Authentication settings**:
   - The "Microsoft" provider should be listed
   - Status should be "Enabled"

2. **Test Authentication**:
   - Visit: https://purple-moss-0942f9e10.3.azurestaticapps.net
   - Try to access a protected route: https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
   - You should be redirected to Microsoft login

### Step 3: Verify App Registration

1. **Go to**: Azure Portal → Azure Active Directory → App registrations
2. **Find**: `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
3. **Verify**:
   - **Authentication** → Redirect URIs should include:
     - `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
     - `https://secai-radar.zimax.net/.auth/login/aad/callback`
   - **API permissions**: Should include "Microsoft Graph" → "User.Read"

## 🧪 Test Authentication

### Test 1: Public Route (No Auth Required)
```bash
curl https://purple-moss-0942f9e10.3.azurestaticapps.net
```
Should return the homepage HTML.

### Test 2: Protected Route (Auth Required)
```bash
curl -L https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
```
Should redirect to Microsoft login or show a login page.

### Test 3: Login Endpoint
```bash
curl https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad
```
Should redirect to Microsoft login.

## 🔒 Route Protection

The `staticwebapp.config.json` file protects routes:

```json
{
  "auth": { "rolesSource": "default" },
  "routes": [
    { "route": "/", "serve": "/index.html" },
    { "route": "/tenant/*", "allowedRoles": ["authenticated"] }
  ]
}
```

- **Public**: `/` (homepage)
- **Protected**: `/tenant/*` (requires authentication)

## 📋 Next Steps After Authentication Works

1. ✅ Test authentication flow
2. ✅ Verify user info is available in Function App
3. ⏳ Configure custom domain authentication (when custom domain is ready)
4. ⏳ Set up role-based access (if needed)

## 🐛 Troubleshooting

### Authentication Not Working?

1. **Check App Registration**:
   ```bash
   az ad app show --id 1cd314e6-933a-4bf9-b889-ffe04a815b98
   ```

2. **Verify Redirect URIs** match exactly (including trailing slash)

3. **Check Static Web App logs** in Azure Portal for errors

4. **Verify Authentication is enabled** in Azure Portal → Static Web App → Authentication

5. **Clear browser cache** and try again

### Common Issues

- **Redirect URI mismatch**: Must match exactly (case-sensitive)
- **App Registration not linked**: Use Azure Portal to link it
- **CORS issues**: Check Function App CORS settings

## 🔗 Useful Links

- **Azure Portal**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/overview
- **App Registration**: https://portal.azure.com/#@zimax.net/resource/Microsoft.AAD/RegisteredApplications/1cd314e6-933a-4bf9-b889-ffe04a815b98
- **Static Web App**: https://purple-moss-0942f9e10.3.azurestaticapps.net

---

**Status**: Authentication configuration sent via REST API. Complete setup in Azure Portal to enable authentication. 🚀

