# Branch Structure

SecAI Radar uses a branch-based deployment strategy:

- **`main` branch**: Contains the main application (web app, API, core functionality)
- **`wiki` branch**: Contains the wiki documentation and GitHub Pages deployment

---

## Branch Overview

### Main Branch (`main`)

**Purpose**: Main application deployment

**Contains**:
- Web application (`web/`)
- API functions (`api/`)
- Core application code (`src/`)
- Application configuration (`config/`)
- Application deployment workflows:
  - `.github/workflows/azure-static-web-apps.yml` (deploys web app)
  - `.github/workflows/azure-functions-deploy.yml` (deploys API)

**Deployment**: Deploys to Azure Static Web Apps and Azure Functions

**URL**: `https://secai-radar.zimax.net` (root domain)

---

### Wiki Branch (`wiki`)

**Purpose**: Wiki documentation and GitHub Pages

**Contains**:
- Wiki documentation (`docs/wiki/`)
- GitHub Pages configuration (`docs/wiki/_config.yml`)
- CNAME file (`docs/wiki/CNAME`)
- GitHub Pages deployment workflow:
  - `.github/workflows/pages.yml` (deploys wiki to GitHub Pages)

**Deployment**: Deploys to GitHub Pages

**URL**: `https://secai-radar.zimax.net/wiki` (subdirectory)

---

## Deployment Workflows

### Main App Deployment

**Workflow**: `.github/workflows/azure-static-web-apps.yml`
- **Trigger**: Push to `main` branch
- **Deploys**: Web app to Azure Static Web Apps
- **Location**: Root of `secai-radar.zimax.net`

### Wiki Deployment

**Workflow**: `.github/workflows/pages.yml` (on `wiki` branch)
- **Trigger**: Push to `wiki` branch
- **Deploys**: Wiki to GitHub Pages
- **Location**: `secai-radar.zimax.net/wiki` subdirectory

---

## DNS Configuration

### Single CNAME Record

Both the main app and wiki use the **same domain** (`secai-radar.zimax.net`) with **one CNAME record**:

```
Type: CNAME
Name: secai-radar
Value: zimaxnet.github.io
TTL: 3600
```

**How it works**:
- Main app: `https://secai-radar.zimax.net` (root)
- Wiki: `https://secai-radar.zimax.net/wiki` (subdirectory)

Both resolve to the same GitHub Pages domain, with path-based routing handling the separation.

---

## Working with Branches

### Making Changes to Main App

```bash
# Switch to main branch
git checkout main

# Make changes
# ... edit files ...

# Commit and push
git add .
git commit -m "Update app features"
git push origin main
```

### Making Changes to Wiki

```bash
# Switch to wiki branch
git checkout wiki

# Make changes to docs/wiki/
# ... edit files ...

# Commit and push
git add docs/wiki/
git commit -m "Update wiki documentation"
git push origin wiki
```

---

## Branch Structure Summary

```
main branch
├── web/                    # Main web application
├── api/                    # API functions
├── src/                    # Core application code
├── config/                 # Application configuration
├── .github/workflows/
│   ├── azure-static-web-apps.yml    # Deploy web app
│   └── azure-functions-deploy.yml    # Deploy API
└── ...                     # Other app files

wiki branch
├── docs/wiki/              # Wiki documentation
│   ├── _config.yml         # Jekyll configuration
│   ├── CNAME               # Custom domain
│   ├── index.md            # Home page
│   └── ...                 # Other wiki pages
└── .github/workflows/
    └── pages.yml           # Deploy wiki to GitHub Pages
```

---

## Benefits of Branch Structure

1. **Separation of Concerns**: App code and wiki documentation are separate
2. **Independent Deployments**: App and wiki can be deployed independently
3. **Clean Organization**: Easier to manage and maintain
4. **Clear Ownership**: Different teams can work on different branches
5. **Path-Based Routing**: Single domain with subdirectory routing

---

## Important Notes

1. **Same Domain**: Both app and wiki use `secai-radar.zimax.net`
2. **Single CNAME**: Only one DNS record needed for both
3. **Path Routing**: Wiki is accessed via `/wiki` subdirectory
4. **Independent Updates**: Changes to app don't affect wiki and vice versa
5. **GitHub Pages**: Wiki deployment is handled by GitHub Pages workflow

---

**Related**: [DNS-CONFIGURATION.md](DNS-CONFIGURATION.md) | [GITHUB-PAGES-SETUP.md](GITHUB-PAGES-SETUP.md)

