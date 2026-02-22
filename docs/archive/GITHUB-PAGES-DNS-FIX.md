# GitHub Pages DNS Configuration Fix

## Issue
The domain `secai-radar.zimax.net` was resolving to `zimaxnet.github.io` because GitHub Pages was configured and taking precedence over the Azure DNS CNAME record.

## Solution

### Option 1: Disable GitHub Pages (Recommended)
Since you're using Azure Static Web Apps for hosting, GitHub Pages is not needed:

1. Go to: https://github.com/zimaxnet/secai-radar/settings/pages
2. Under **Source**, select **None** (or click **Disable GitHub Pages**)
3. Save changes

This will:
- Stop GitHub Pages from serving the repository
- Allow your Azure DNS CNAME to work correctly
- Remove the `zimaxnet.github.io` DNS resolution

### Option 2: Keep GitHub Pages but Use Different Domain
If you want to keep GitHub Pages for documentation or other purposes:

1. Keep GitHub Pages enabled but **don't use a custom domain**
2. GitHub Pages will be available at: `https://zimaxnet.github.io/secai-radar/`
3. Your Azure Static Web App will be at: `https://secai-radar.zimax.net`

## Current Configuration

### Azure Static Web App
- **Hosting**: Azure Static Web Apps
- **Domain**: `secai-radar.zimax.net`
- **Default URL**: `https://purple-moss-0942f9e10.3.azurestaticapps.net`
- **DNS CNAME**: `secai-radar.zimax.net` → `purple-moss-0942f9e10.3.azurestaticapps.net`

### GitHub Pages (if enabled)
- **Hosting**: GitHub Pages
- **Domain**: `zimaxnet.github.io` (or custom domain if configured)
- **DNS**: Can conflict with Azure DNS if both point to same domain

## Why This Matters

When GitHub Pages is enabled with a custom domain, it creates DNS records that can conflict with your Azure DNS Zone. The DNS resolution was pointing to GitHub Pages (`zimaxnet.github.io`) instead of your Azure Static Web App.

## Verification

After disabling GitHub Pages:
1. Wait 5-10 minutes for DNS cache to clear
2. Check DNS: `dig @8.8.8.8 secai-radar.zimax.net`
3. Should resolve to: `purple-moss-0942f9e10.3.azurestaticapps.net`
4. Check Azure Portal → Static Web App → Custom domains
5. Status should change from "Validating" to "Ready"

## Next Steps

1. **Disable GitHub Pages** at: https://github.com/zimaxnet/secai-radar/settings/pages
2. **Wait for DNS propagation** (5-30 minutes)
3. **Verify** DNS resolution points to Azure
4. **Check** Azure Static Web App custom domain status
5. **Test** access at `https://secai-radar.zimax.net`

