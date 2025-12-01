# SecAI Radar Wiki Location

## GitHub Wiki Branch

The SecAI Radar repository has a **`wiki` branch** that contains GitHub Pages configuration.

### Current Status
- **Branch**: `wiki` (remote: `origin/wiki`)
- **GitHub Pages URL**: `https://zimaxnet.github.io/secai-radar` (returns 404 - not currently enabled)
- **GitHub Wiki**: Available at `https://github.com/zimaxnet/secai-radar/wiki` (standard GitHub Wiki)
- **Wiki Content**: Located in `docs/wiki/` directory on the `wiki` branch
- **Deployment**: GitHub Actions workflow (`.github/workflows/pages.yml`) deploys to GitHub Pages

### GitHub Pages Configuration

The `wiki` branch contains:
- `.github/workflows/pages.yml` - GitHub Actions workflow for deploying to GitHub Pages
- `docs/wiki/` - Wiki content (Jekyll-based or static Markdown)
- `docs/wiki/CNAME` - Custom domain configuration (if set)
- Multiple documentation files:
  - Home.md, Getting-Started.md, User-Guide.md
  - Architecture.md, Configuration.md, API-Reference.md
  - Controls-Guide.md, Dashboard-Guide.md, Tools-Guide.md, Gaps-Guide.md
  - Troubleshooting.md, FAQ.md, Glossary.md
  - DNS-related documentation files

### How to Check GitHub Pages Settings

1. **Repository Settings**: https://github.com/zimaxnet/secai-radar/settings/pages
   - Check if GitHub Pages is enabled
   - See which branch is configured as the source
   - Check if a custom domain is set

2. **Current Status**: 
   - GitHub Pages appears to be **disabled** (404 when accessing `zimaxnet.github.io/secai-radar`)
   - This is correct if you want to use Azure Static Web Apps instead

### Options

#### Option 1: Use GitHub Pages for Wiki (Recommended if you want a separate wiki)
1. Enable GitHub Pages at: https://github.com/zimaxnet/secai-radar/settings/pages
2. Set source branch to: `wiki`
3. Wiki will be available at: `https://zimaxnet.github.io/secai-radar`
4. Use a different subdomain for the wiki (e.g., `wiki-secai-radar.zimax.net`) to avoid conflicts

#### Option 2: Use GitHub Wiki (Built-in)
- Access at: `https://github.com/zimaxnet/secai-radar/wiki`
- No GitHub Pages needed
- Built into GitHub
- Easy to use, but limited customization

#### Option 3: Keep GitHub Pages Disabled (Current Setup)
- Use Azure Static Web Apps for the main app
- Use GitHub Wiki for documentation
- Or host wiki separately

### ⚠️ DNS Conflict Found!

**IMPORTANT**: The `docs/wiki/CNAME` file in the `wiki` branch contains:
```
secai-radar.zimax.net
```

This is **causing a DNS conflict** with your Azure Static Web App! When GitHub Pages is enabled, it tries to use this domain, which conflicts with Azure's DNS configuration.

### DNS Considerations

**Current Issue**: 
- The wiki branch has `CNAME` file pointing to `secai-radar.zimax.net`
- This domain is used by Azure Static Web App
- When GitHub Pages is enabled, it creates DNS records that conflict with Azure DNS

**Solution Options**:

1. **Disable GitHub Pages** (Recommended if using Azure Static Web App)
   - Remove or update the `CNAME` file in the `wiki` branch
   - Or disable GitHub Pages in repository settings

2. **Use Different Subdomain for Wiki**
   - Update `docs/wiki/CNAME` to use a different subdomain:
     - `wiki-secai-radar.zimax.net`
     - `docs-secai-radar.zimax.net`
     - `secai-radar-wiki.zimax.net`
   - Create DNS CNAME record for the new subdomain
   - Keep `secai-radar.zimax.net` for Azure Static Web App

3. **Keep GitHub Pages Disabled**
   - Don't enable GitHub Pages
   - Use GitHub's built-in Wiki instead
   - Or host wiki documentation separately

### Next Steps

To check the current GitHub Pages configuration:
1. Visit: https://github.com/zimaxnet/secai-radar/settings/pages
2. Check if it's enabled and which branch is configured
3. Decide if you want to:
   - Enable it for the wiki branch
   - Keep it disabled (current setup)
   - Use GitHub's built-in Wiki instead

