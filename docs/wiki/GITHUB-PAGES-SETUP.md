---
layout: default
title: Github Pages Setup
permalink: /GITHUB-PAGES-SETUP/
---

# GitHub Pages Setup Instructions

This guide explains how to publish the SecAI Radar wiki to GitHub Pages at `secai-radar.zimax.net/wiki` (as a subdirectory of the main app domain).

---

## Prerequisites

1. GitHub repository with wiki files in `docs/wiki/`
2. Repository access to configure GitHub Pages
3. DNS access to configure the custom domain

---

## Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select:
   - **Source**: `GitHub Actions` (not "Deploy from a branch")
4. Click **Save**

---

## Step 2: Configure Custom Domain

### On GitHub

**Note**: The wiki will be deployed as a subdirectory `/wiki` on the main app domain `secai-radar.zimax.net`.

1. In **Settings** → **Pages**, scroll to **Custom domain**
2. Enter: `secai-radar.zimax.net` (same domain as the main app)
3. Check **Enforce HTTPS**
4. Click **Save**

**Important**: The CNAME file points to `secai-radar.zimax.net` (same as the main app). The wiki will be available at `secai-radar.zimax.net/wiki`.

### DNS Configuration

Configure DNS records for `secai-radar.zimax.net`:

#### Option A: CNAME Record (Recommended)

```
Type: CNAME
Name: secai-radar
Value: your-username.github.io
TTL: 3600
```

Or if using an organization:

```
Type: CNAME
Name: secai-radar
Value: your-org.github.io
TTL: 3600
```

**Note**: Replace `your-username` or `your-org` with your actual GitHub username or organization name.

#### Option B: A Records (Alternative)

If CNAME doesn't work, use A records:

```
Type: A
Name: secai-radar
Value: 185.199.108.153
TTL: 3600

Type: A
Name: secai-radar
Value: 185.199.109.153
TTL: 3600

Type: A
Name: secai-radar
Value: 185.199.110.153
TTL: 3600

Type: A
Name: secai-radar
Value: 185.199.111.153
TTL: 3600
```

**Note**: GitHub Pages IP addresses may change. Check [GitHub Pages documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) for current IPs.

---

## Step 3: Deploy to GitHub Pages

### Automatic Deployment

The GitHub Actions workflow (`.github/workflows/pages.yml`) will automatically deploy when:
- Files in `docs/wiki/` are pushed to `main` branch
- Workflow is manually triggered from Actions tab

### Manual Deployment

1. Push changes to `main` branch:
   ```bash
   git add docs/wiki/
   git commit -m "Update wiki documentation"
   git push origin main
   ```

2. GitHub Actions will automatically deploy
3. Check **Actions** tab for deployment status
4. Wait for deployment to complete (usually 1-2 minutes)

---

## Step 4: Verify Deployment

1. **Wait for DNS propagation** (can take up to 24 hours, usually 1-2 hours)
2. **Check GitHub Pages**:
   - Go to **Settings** → **Pages**
   - Verify domain is configured
   - Check deployment status (should show green checkmark)
3. **Test the site**:
   - Visit `https://secai-radar.zimax.net/wiki`
   - Verify all pages load correctly
   - Test navigation links
   - Check HTTPS is working (green lock icon)

---

## Step 5: Access the Wiki

Once deployed, the wiki will be available at:

- **Wiki URL**: `https://secai-radar.zimax.net/wiki`
- **Homepage**: `https://secai-radar.zimax.net/wiki/Home`
- **All Pages**: `https://secai-radar.zimax.net/wiki/{PageName}`

**Note**: The wiki is served as a subdirectory `/wiki` on the main app domain `secai-radar.zimax.net`.

All pages will be accessible at:
- `https://secai-radar.zimax.net/wiki/` (Home)
- `https://secai-radar.zimax.net/wiki/Getting-Started` (Getting Started)
- `https://secai-radar.zimax.net/wiki/User-Guide` (User Guide)
- etc.

---

## Troubleshooting

### Site Not Loading

1. **Check DNS**: Verify DNS records are correct
   ```bash
   dig secai-radar.zimax.net
   nslookup secai-radar.zimax.net
   ```

2. **Check GitHub Pages**: Verify deployment succeeded
   - Go to **Settings** → **Pages**
   - Check deployment status
   - Review **Actions** tab for errors

3. **Check CNAME**: Verify `docs/wiki/CNAME` file exists and contains:
   ```
   secai-radar.zimax.net
   ```

### Custom Domain Not Working

1. **Wait for DNS propagation** (up to 24 hours)
2. **Check DNS records** are correct (use `dig` or `nslookup`)
3. **Verify HTTPS** is enabled in GitHub Pages settings
4. **Clear browser cache** and try again
5. **Check SSL certificate** is issued (may take a few minutes after DNS)

### 404 Errors

1. **Check file names**: Ensure file names match link paths (case-sensitive)
2. **Check internal links**: Verify all internal links use correct paths
3. **Check Jekyll build**: Review Actions logs for build errors
4. **Check baseurl**: Verify `baseurl` in `_config.yml` is correct

### Build Errors

1. **Check Actions logs**: Review build logs in Actions tab
2. **Check Jekyll**: Verify Jekyll build succeeded
3. **Check dependencies**: Ensure Gemfile is correct
4. **Check YAML**: Verify YAML syntax in `_config.yml`

---

## File Structure

```
docs/wiki/
├── CNAME                    # Custom domain (secai-radar.zimax.net)
├── _config.yml              # Jekyll configuration
├── .nojekyll                # Disable Jekyll processing (if needed)
├── Gemfile                  # Jekyll dependencies
├── index.md                 # Homepage (redirects to Home.md content)
├── Home.md                  # Wiki homepage
├── Getting-Started.md       # Quick start
├── User-Guide.md            # User documentation
├── Dashboard-Guide.md       # Dashboard guide
├── Controls-Guide.md        # Controls guide
├── Tools-Guide.md           # Tools guide
├── Gaps-Guide.md            # Gaps guide
├── API-Reference.md         # API docs
├── Architecture.md          # Architecture
├── Installation.md          # Installation
├── Configuration.md         # Configuration
├── FAQ.md                   # FAQ
├── Troubleshooting.md       # Troubleshooting
├── Glossary.md              # Glossary
├── Contributing.md          # Contributing
└── README.md                # Wiki README
```

---

## Next Steps

1. **Push to GitHub**: Commit and push all changes
   ```bash
   git add docs/wiki/ .github/workflows/pages.yml
   git commit -m "Add GitHub Pages deployment configuration"
   git push origin main
   ```

2. **Enable GitHub Pages**: Follow Step 1 above
3. **Configure DNS**: Follow Step 2 above
4. **Wait for Deployment**: GitHub Actions will deploy automatically
5. **Verify**: Test the site at `https://secai-radar.zimax.net`

---

## Additional Configuration

### Enabling HTTPS

GitHub Pages automatically provides HTTPS for custom domains. After DNS is configured:
1. Wait for SSL certificate to be issued (usually automatic)
2. Enable "Enforce HTTPS" in GitHub Pages settings
3. Test HTTPS is working

### Custom Theme

The current setup uses `jekyll-theme-minimal`. To change:
1. Update `theme` in `_config.yml`
2. Add theme gem to `Gemfile`
3. Redeploy

### Additional Plugins

To add Jekyll plugins:
1. Add plugin to `Gemfile`
2. Add plugin to `_config.yml` under `plugins`
3. Redeploy

---

## Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Custom Domain Setup](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Actions for Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)

---

**Last Updated**: 2025-01-15
