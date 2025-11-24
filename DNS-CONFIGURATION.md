---
layout: default
title: Dns Configuration
---

> **Update (2025-11):** The wiki now publishes at `https://zimaxnet.github.io/secai-radar/`. References to the former `/wiki` subdirectory are retained for historical context.


# DNS Configuration for SecAI Radar

DNS configuration guide for the main app and wiki.

---

## Domain Structure

- **Main App**: `secai-radar.zimax.net` (root domain)
- **Wiki**: `zimaxnet.github.io/secai-radar` (GitHub Pages project site)

---

## DNS Configuration

### Single CNAME Record

Both the main app and wiki use the **same domain** (`secai-radar.zimax.net`). You only need **one CNAME record**:

```
Type: CNAME
Name: secai-radar
Value: your-username.github.io
TTL: 3600
```

**Important**: Replace `your-username` with your actual GitHub username or organization name.

**Example**: If your GitHub username is `derek`, use:
```
Type: CNAME
Name: secai-radar
Value: derek.github.io
TTL: 3600
```

---

## How It Works

1. **Main App**: Deployed to `secai-radar.zimax.net` (root)
2. **Wiki**: Deployed to `zimaxnet.github.io/secai-radar` (GitHub Pages project site)

Both use the same:
- DNS record (CNAME to `your-username.github.io`)
- Domain (`secai-radar.zimax.net`)
- SSL certificate
- GitHub Pages deployment

---

## GitHub Pages Setup

### Main App (Root)

- **Source**: Your main app deployment
- **Custom Domain**: `secai-radar.zimax.net`
- **CNAME**: Points to `secai-radar.zimax.net`

### Wiki (Subdirectory)

- **Source**: `docs/wiki/` directory
- **Custom Domain**: `secai-radar.zimax.net` (same as main app)
- **CNAME**: Points to `secai-radar.zimax.net` (same as main app)
- **Path**: `GitHub Pages project site

---

## Deployment

### Main App Deployment

The main app should be deployed to the root of `secai-radar.zimax.net`.

### Wiki Deployment

The wiki is deployed to `_site/wiki/` subdirectory, making it available at `zimaxnet.github.io/secai-radar`.

---

## Verification

### Check DNS

```bash
dig secai-radar.zimax.net
nslookup secai-radar.zimax.net
```

Should return:
- **Type**: CNAME
- **Value**: `your-username.github.io`

### Check Main App

Visit: `https://secai-radar.zimax.net`

### Check Wiki

Visit: `https://zimaxnet.github.io/secai-radar`

---

## Troubleshooting

### Main App Not Loading

- Check main app deployment
- Verify DNS is configured
- Check GitHub Pages settings for main app

### Wiki Not Loading

- Check wiki deployment in Actions tab
- Verify `baseurl: "/wiki"` in `_config.yml`
- Check that wiki is built to `_site/wiki/` directory
- Verify internal links use `/wiki/` prefix

### DNS Not Working

- Verify CNAME record is correct
- Wait for DNS propagation (up to 24 hours)
- Check DNS provider settings

---

## Important Notes

1. **Same Domain**: Both app and wiki use `secai-radar.zimax.net`
2. **Single DNS Record**: Only one CNAME record needed
3. **Path-Based Routing**: Wiki is at `GitHub Pages project site
4. **Separate Deployments**: Main app and wiki deploy separately
5. **Shared SSL**: Same SSL certificate for both

---

**Related**: [GitHub-Pages-Deployment-Instructions.md](GitHub-Pages-Deployment-Instructions.md) | [GITHUB-PAGES-SETUP.md](GITHUB-PAGES-SETUP.md)
