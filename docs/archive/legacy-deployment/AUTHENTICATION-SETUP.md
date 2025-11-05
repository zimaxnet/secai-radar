# Entra ID Authentication Setup

## ✅ Status

Authentication has been configured for the Static Web App using Entra ID (Azure AD).

## Configuration Details

- **App Registration**: `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
- **Tenant ID**: `8838531d-55dd-4018-8341-77705f4845f4`
- **Redirect URIs**:
  - `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
  - `https://secai-radar.zimax.net/.auth/login/aad/callback`

## Verification

### Test Authentication

1. **Visit the Static Web App**:
   ```
   https://purple-moss-0942f9e10.3.azurestaticapps.net
   ```

2. **Try to access a protected route**:
   ```
   https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
   ```

3. **You should be redirected to login** if authentication is working.

### Check Authentication Status

1. **Azure Portal**: 
   - Go to: Static Web App → `secai-radar` → **Authentication**
   - Verify that "Microsoft" identity provider is configured

2. **Test Login Endpoint**:
   ```bash
   curl https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login
   ```

## Route Protection

The `staticwebapp.config.json` file configures route protection:

```json
{
  "auth": { "rolesSource": "default" },
  "routes": [
    { "route": "/", "serve": "/index.html" },
    { "route": "/tenant/*", "allowedRoles": ["authenticated"] }
  ],
  "navigationFallback": { "rewrite": "/index.html" }
}
```

Routes under `/tenant/*` require authentication.

## User Information in Functions

When calling the Function App API from the authenticated Static Web App, user information is available via headers:

- `x-ms-client-principal`: Base64-encoded JSON with user info
- `x-ms-client-principal-name`: User's email/name
- `x-ms-client-principal-id`: User's object ID

## Next Steps

1. ✅ Authentication configured
2. ⏳ Test authentication flow
3. ⏳ Configure custom domain authentication (when custom domain is ready)

## Troubleshooting

If authentication is not working:

1. **Check App Registration**:
   ```bash
   az ad app show --id 1cd314e6-933a-4bf9-b889-ffe04a815b98
   ```

2. **Verify Redirect URIs** match your domain

3. **Check Azure Portal** → Static Web App → Authentication for any errors

4. **Review Static Web App logs** in Azure Portal for authentication errors

