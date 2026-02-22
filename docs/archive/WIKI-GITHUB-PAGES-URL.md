# GitHub Pages Wiki URL

## Current Status: ⏳ Not Enabled Yet

GitHub Pages for the wiki is **not currently enabled**. Once enabled, it will be available at:

### URLs (Once Enabled)

1. **Custom Domain** (recommended):
   - `https://wiki.secai-radar.zimax.net`
   - This is configured and ready to use

2. **Default GitHub Pages URL**:
   - `https://zimaxnet.github.io/secai-radar`
   - This is the default URL GitHub provides

### Current Status

- ✅ **DNS configured**: `wiki.secai-radar.zimax.net` → `zimaxnet.github.io`
- ✅ **CNAME file updated**: In `wiki` branch at `docs/wiki/CNAME`
- ✅ **GitHub Actions workflow**: Ready at `.github/workflows/pages.yml`
- ❌ **GitHub Pages**: Not enabled yet (returns 404)

### How to Enable

1. Go to: **https://github.com/zimaxnet/secai-radar/settings/pages**
2. Under **Source**, select:
   - **Branch**: `wiki`
   - **Folder**: `/ (root)` or `/docs/wiki` (check the workflow to see which path it uses)
3. Click **Save**

### After Enabling

Once enabled, GitHub will:
- Build and deploy the wiki content from the `wiki` branch
- Make it available at `https://zimaxnet.github.io/secai-radar`
- Verify the custom domain `wiki.secai-radar.zimax.net`
- Provision SSL certificate for the custom domain

### Check Status

To check if it's enabled:
- Visit: https://github.com/zimaxnet/secai-radar/settings/pages
- Look for "Your site is live at..." message

### Alternative: GitHub Wiki

If you prefer not to use GitHub Pages, you can use GitHub's built-in Wiki:
- URL: `https://github.com/zimaxnet/secai-radar/wiki`
- No configuration needed
- Works immediately

