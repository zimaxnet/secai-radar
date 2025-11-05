# Branch Structure: main vs wiki

## Overview

The repository has two main branches with **different purposes**:

### `main` Branch
- **Purpose**: Main application development and deployment
- **Deploys to**: Azure Static Web App (`secai-radar.zimax.net`)
- **Workflows**: 
  - `azure-static-web-apps.yml` - Deploys web app
  - `azure-functions-deploy.yml` - Deploys API
- **Documentation**: Located in `docs/` (excluding `docs/wiki/`)

### `wiki` Branch
- **Purpose**: GitHub Pages wiki documentation
- **Deploys to**: GitHub Pages (`wiki.secai-radar.zimax.net`)
- **Workflows**: 
  - `pages.yml` - Deploys wiki to GitHub Pages
- **Documentation**: Located in `docs/wiki/`

## Branch Relationship

### Are They Independent?

**Partially independent** - They share application code but have different documentation and workflows:

| Aspect | main | wiki |
|--------|------|------|
| Application code (api/, web/) | ✅ Yes | ✅ Yes (copied from main) |
| Documentation (docs/) | ✅ Yes (excluding wiki/) | ✅ Yes (including docs/wiki/) |
| GitHub Pages workflow | ❌ No | ✅ Yes |
| Azure deployment workflows | ✅ Yes | ✅ Yes |
| CNAME file | ❌ No | ✅ Yes (wiki.secai-radar.zimax.net) |

### Current Status

- **Branches diverged**: They have different commit histories
- **Wiki branch was created from main**: Contains application code + wiki docs
- **Main branch**: Contains application code + regular docs (no wiki)

## Maintenance Strategy

### Option 1: Keep Independent (Current Approach)
- **Pros**: 
  - Wiki changes don't affect main app deployment
  - Can update wiki independently
  - Clear separation of concerns
- **Cons**:
  - Application code exists in both branches
  - Changes to app code need to be synced if wiki needs them
  - Potential for divergence

### Option 2: Sync Application Code
- **Pros**:
  - Single source of truth for application code
  - Wiki always has latest app code references
- **Cons**:
  - Requires manual or automated syncing
  - Wiki updates might trigger unnecessary builds

### Option 3: Separate Wiki Repository
- **Pros**:
  - Complete independence
  - No code duplication
- **Cons**:
  - More repositories to manage
  - Wiki can't reference app code directly

## Recommendations

### For Current Setup

**Keep them independent** but be aware:

1. **Application code updates**: 
   - If you update app code in `main`, consider if `wiki` needs those updates
   - Wiki mainly needs docs, not code updates

2. **Wiki documentation updates**:
   - Edit files in `wiki` branch → `docs/wiki/`
   - Push to `wiki` branch
   - GitHub Pages workflow will deploy automatically

3. **Main documentation updates**:
   - Edit files in `main` branch → `docs/`
   - These are for developers, not end users

### When to Sync

You might want to sync application code if:
- Wiki documentation references specific code structures
- API changes affect wiki examples
- You want wiki to always reflect latest app state

### How to Sync

If you need to sync application code from main to wiki:

```bash
# On wiki branch
git checkout wiki
git merge main --no-edit
# Resolve any conflicts
git push origin wiki
```

Or cherry-pick specific commits:
```bash
git checkout wiki
git cherry-pick <commit-hash>
```

## File Overlap

### Files in Both Branches
- `api/` - Application API code
- `web/` - Web application code
- `seeds/` - Seed data
- `.github/workflows/azure-*.yml` - Azure deployment workflows
- `docs/` - Documentation (but wiki has additional `docs/wiki/`)

### Files Only in wiki Branch
- `docs/wiki/` - Wiki documentation content
- `.github/workflows/pages.yml` - GitHub Pages deployment
- `docs/wiki/CNAME` - Custom domain configuration

### Files Only in main Branch
- Various workflow notification examples
- Some documentation files in `docs/`

## Best Practices

1. **Wiki updates**: Always work on `wiki` branch
2. **App updates**: Always work on `main` branch
3. **Documentation**:
   - Developer docs → `main` branch `docs/`
   - User/wiki docs → `wiki` branch `docs/wiki/`
4. **Sync when needed**: Only sync if wiki needs app code updates

## Summary

**Answer**: The branches are **mostly independent** for documentation purposes, but they **share application code**. The wiki branch is essentially `main` + wiki documentation. This is fine for most use cases - you can update them independently, and only sync application code when the wiki needs to reference updated code structures.

