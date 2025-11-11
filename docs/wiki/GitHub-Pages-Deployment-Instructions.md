---
layout: default
title: Github Pages Deployment Instructions
---

> **Update (2025-11):** The wiki now publishes at `https://zimaxnet.github.io/secai-radar/`. References to the former `/wiki` subdirectory are retained for historical context.


# GitHub Pages Deployment Instructions

Quick reference for deploying SecAI Radar wiki to `secai-radar.zimax.net`.

---

## Quick Setup Steps

### 1. Push to GitHub

All files are ready. Just push to your repository:

```bash
git add docs/wiki/ .github/workflows/pages.yml
git commit -m "Add GitHub Pages deployment configuration"
git push origin main
```

### 2. Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under **Source**, select: **GitHub Actions**
3. Click **Save**

### 3. Configure Custom Domain

**Important**: The wiki will be deployed as a independent project site on the main app domain.

1. In **Settings** → **Pages**, scroll to **Custom domain**
2. Enter: `secai-radar.zimax.net` (same domain as the main app)
3. Check **Enforce HTTPS**
4. Click **Save**

The wiki will be available at `https://zimaxnet.github.io/secai-radar` (not a separate subdomain).

### 4. Configure DNS

**Important**: The DNS should already be configured for the main app at `secai-radar.zimax.net`. The wiki will use the same domain.

If the main app DNS is already configured, you don't need to add another DNS record. The wiki will be served from the same domain at `/wiki` path.

If you need to configure DNS for the main app:

```
Type: CNAME
Name: secai-radar
Value: your-username.github.io
TTL: 3600
```

**Note**: Replace `your-username` with your actual GitHub username or organization name.

**Note**: This is the same DNS record used for the main app. The wiki will be available at `https://zimaxnet.github.io/secai-radar`.

### 5. Wait for Deployment

- GitHub Actions will automatically deploy (check **Actions** tab)
- DNS propagation may take 1-24 hours (usually 1-2 hours)
- SSL certificate will be issued automatically

---

## Access Your Wiki

Once deployed, the wiki will be available at:

**Wiki URL**: `https://zimaxnet.github.io/secai-radar`

**Note**: The wiki is served as a independent project site on the main app domain `secai-radar.zimax.net`.

All pages:
- Home: `https://zimaxnet.github.io/secai-radar/Home`
- Getting Started: `https://zimaxnet.github.io/secai-radar/Getting-Started`
- User Guide: `https://zimaxnet.github.io/secai-radar/User-Guide`
- etc.

---

## Files Created

### Configuration Files
- `docs/wiki/CNAME` - Custom domain configuration
- `docs/wiki/_config.yml` - Jekyll configuration
- `docs/wiki/Gemfile` - Jekyll dependencies
- `docs/wiki/index.md` - Homepage
- `docs/wiki/.nojekyll` - Disable Jekyll (if needed)

### Workflow
- `.github/workflows/pages.yml` - GitHub Actions deployment workflow

### Documentation
- 16 wiki pages in `docs/wiki/`

---

## Troubleshooting

### Deployment Not Working

1. **Check Actions Tab**: Review workflow runs for errors
2. **Check Permissions**: Verify Pages permissions in Settings
3. **Check Workflow**: Ensure workflow file is correct

### DNS Not Working

1. **Check DNS**: Use `dig secai-radar.zimax.net` or `nslookup`
2. **Wait**: DNS propagation can take up to 24 hours
3. **Verify CNAME**: Ensure CNAME record points to `your-username.github.io`

### Site Not Loading

1. **Check Deployment**: Verify deployment succeeded in Actions
2. **Check Domain**: Verify domain is configured in Settings → Pages
3. **Check SSL**: Wait for SSL certificate to be issued (automatic)

---

## Manual Deployment

If automatic deployment doesn't work:

1. Go to **Actions** tab
2. Select **Deploy Wiki to GitHub Pages** workflow
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**

---

## Next Steps

1. **Push Changes**: Push to GitHub
2. **Enable Pages**: Follow Step 2 above
3. **Configure DNS**: Follow Step 4 above
4. **Test**: Visit `https://zimaxnet.github.io/secai-radar` after DNS propagates

---

**For detailed instructions, see**: [GITHUB-PAGES-SETUP.md](GITHUB-PAGES-SETUP.md)
