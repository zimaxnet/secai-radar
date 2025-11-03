# Azure Portal Manual Configuration Steps

## GitHub Repository Linking

### Step 1: Link GitHub Repository
1. Go to Azure Portal → Static Web App → `secai-radar`
2. Navigate to **Deployment** in the left menu
3. If not already linked, click **Add deployment source** or **Edit**
4. Select:
   - **Source**: GitHub
   - **Organization**: `zimaxnet`
   - **Repository**: `secai-radar`
   - **Branch**: `main`
   - **Build Presets**: Custom
5. Configure build details:
   - **App location**: `/web`
   - **API location**: `/api`
   - **Output location**: `dist`
6. Click **Save**

### Step 2: Authorize GitHub (if needed)
- If prompted, authorize Azure to access your GitHub account
- Grant access to the `zimaxnet` organization

## Authentication Configuration (Entra ID)

### App Registration Details
- **App ID**: `1cd314e6-933a-4bf9-b889-ffe04a815b98`
- **Display Name**: `secai-radar-auth`
- **Tenant ID**: `8838531d-55dd-4018-8341-77705f4845f4`

### Step 1: Configure Authentication in Static Web App
1. Go to Azure Portal → Static Web App → `secai-radar`
2. Navigate to **Authentication** in the left menu
3. Click **Add identity provider**
4. Select **Microsoft (Azure AD / Entra ID)**
5. Choose **Create new app registration** (or use existing: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
6. Configure:
   - **Name**: `secai-radar-auth`
   - **App registration type**: Create new
   - The app registration is already created with redirect URIs:
     - `https://secai-radar.zimax.net/.auth/login/aad/callback`
     - `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
7. Click **Add**

### Step 2: Configure App Registration (if using existing)
If you want to use the existing app registration (`1cd314e6-933a-4bf9-b889-ffe04a815b98`):
1. Go to Azure Portal → Azure Active Directory → App registrations
2. Find `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)
3. Go to **Authentication**
4. Verify redirect URIs are configured:
   - `https://secai-radar.zimax.net/.auth/login/aad/callback`
   - `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
5. Under **Implicit grant and hybrid flows**, enable:
   - ✅ ID tokens (used for implicit and hybrid flows)
6. Save changes

### Step 3: Configure API Permissions (if needed)
1. In App Registration → **API permissions**
2. Ensure Microsoft Graph permissions are configured for user authentication
3. Default permissions should be sufficient

## Custom Domain Verification

### Domain Status
- **Domain**: `secai-radar.zimax.net`
- **CNAME**: Already configured → `purple-moss-0942f9e10.3.azurestaticapps.net`
- **DNS Zone**: `dns-rg` / `zimax.net`

### Verification Steps
1. Go to Azure Portal → Static Web App → `secai-radar` → **Custom domains**
2. Verify `secai-radar.zimax.net` is listed
3. Wait for validation to complete (may take 5-30 minutes)
4. SSL certificate will be automatically provisioned after validation

## Verification Checklist

After completing the above steps:
- [ ] GitHub repository is linked and deployment source shows `zimaxnet/secai-radar`
- [ ] Authentication shows Microsoft provider configured
- [ ] Custom domain shows as "Validated" with SSL certificate
- [ ] Application accessible at `https://secai-radar.zimax.net`
- [ ] Authentication redirect works (try `/tenant/NICO/dashboard`)

## Useful Links

- **Static Web App**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/overview
- **App Registration**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/23f4e2c5-0667-4514-8e2e-f02ca7880c95/providers/Microsoft.AAD/ApplicationRegistrations/1cd314e6-933a-4bf9-b889-ffe04a815b98/overview
- **DNS Zone**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/dns-rg/providers/Microsoft.Network/dnszones/zimax.net/overview

