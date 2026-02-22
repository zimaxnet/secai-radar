# Wiki Setup Complete - wiki.secai-radar.zimax.net

## ✅ Completed Actions

1. **Updated CNAME file** in `wiki` branch:
   - Changed from: `secai-radar.zimax.net` (conflicting with Azure Static Web App)
   - Changed to: `wiki.secai-radar.zimax.net`

2. **Created DNS CNAME record** in Azure DNS:
   - **Record**: `wiki.secai-radar` (in `zimax.net` zone)
   - **Target**: `zimaxnet.github.io`
   - **TTL**: 3600 seconds
   - **Status**: ✅ Created and verified

3. **DNS Resolution**: ✅ Working
   - `wiki.secai-radar.zimax.net` resolves to `zimaxnet.github.io`

## 📋 Next Steps to Enable GitHub Pages

### Step 1: Enable GitHub Pages
1. Go to: https://github.com/zimaxnet/secai-radar/settings/pages
2. Under **Source**, select:
   - **Branch**: `wiki`
   - **Folder**: `/ (root)` or `/docs/wiki` (depending on your workflow)
3. Click **Save**

### Step 2: Configure GitHub Pages Settings
- The GitHub Actions workflow (`.github/workflows/pages.yml`) will automatically deploy when:
  - Changes are pushed to the `wiki` branch
  - Files in `docs/wiki/` are modified
  - Workflow is manually triggered

### Step 3: Verify Custom Domain
1. After enabling GitHub Pages, GitHub will verify the custom domain
2. This may take a few minutes
3. Check the status at: https://github.com/zimaxnet/secai-radar/settings/pages

### Step 4: Access Your Wiki
Once enabled, your wiki will be available at:
- **Custom Domain**: `https://wiki.secai-radar.zimax.net`
- **GitHub Pages URL**: `https://zimaxnet.github.io/secai-radar` (if enabled)

## 📊 Current Configuration

### DNS Records
- **Main App**: `secai-radar.zimax.net` → `purple-moss-0942f9e10.3.azurestaticapps.net` (Azure Static Web App)
- **Wiki**: `wiki.secai-radar.zimax.net` → `zimaxnet.github.io` (GitHub Pages)

### Branches
- **main**: Main application code (deployed to Azure Static Web App)
- **wiki**: Wiki content and GitHub Pages configuration (deployed to GitHub Pages)

### GitHub Actions
- **Wiki Deployment**: `.github/workflows/pages.yml` on `wiki` branch
- **App Deployment**: `.github/workflows/azure-static-web-apps.yml` on `main` branch

## 🔍 Verification

### Check DNS
```bash
dig @8.8.8.8 wiki.secai-radar.zimax.net
# Should resolve to: zimaxnet.github.io
```

### Check Azure DNS
```bash
az network dns record-set cname show \
  --resource-group dns-rg \
  --zone-name zimax.net \
  --name wiki.secai-radar
```

### Check GitHub Pages Status
- Visit: https://github.com/zimaxnet/secai-radar/settings/pages
- Should show: "Your site is live at wiki.secai-radar.zimax.net"

## 📝 Notes

- The DNS conflict is now resolved - the wiki uses a different subdomain
- The main app (`secai-radar.zimax.net`) is unaffected
- GitHub Pages will automatically provision SSL certificate for the custom domain
- The wiki content is in the `docs/wiki/` directory on the `wiki` branch

## 🎯 Summary

✅ CNAME file updated in wiki branch  
✅ DNS CNAME record created in Azure  
✅ DNS resolution verified  
⏳ Next: Enable GitHub Pages in repository settings

