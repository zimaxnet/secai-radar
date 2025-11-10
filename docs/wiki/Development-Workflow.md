# Development Workflow

## Overview

SecAI Radar uses a **dual-branch strategy** that allows seamless development of the application alongside maintenance of public documentation—all from the same codebase. This approach provides clear separation between development work and user-facing documentation while maintaining flexibility to switch contexts as needed.

## Branch Structure

### `main` Branch - Application Development

**Purpose**: Primary development branch for the SecAI Radar application

**Contains**:
- Application code (`api/`, `web/`)
- Developer documentation (`docs/` excluding `docs/wiki/`)
- Azure deployment workflows
- Development tools and scripts

**Deploys to**: Azure Static Web App at `secai-radar.zimax.net`

**When to use**:
- Developing new features
- Updating API endpoints
- Modifying web UI
- Writing developer documentation
- Fixing application bugs
- Working on architecture decisions

### `gh-pages` Branch - Public Documentation

**Purpose**: User-facing documentation published via GitHub Pages

**Contains**:
- Wiki documentation (`docs/wiki/`)
- Application code (for reference, synced from main)
- GitHub Pages deployment workflow
- Custom domain configuration

**Deploys to**: GitHub Pages at `wiki.secai-radar.zimax.net`

**When to use**:
- Updating user documentation
- Adding new wiki pages
- Fixing documentation errors
- Updating public-facing guides

## Development Workflow

### Working on Application Development

**Default workflow** - You'll spend most of your time here:

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Make your changes to:
# - api/ (API endpoints)
# - web/ (React UI)
# - docs/ (developer documentation)

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

**What happens**:
- Changes are committed to `main` branch
- GitHub Actions workflows automatically deploy to Azure
- Static Web App and Function App are updated
- Application is live at `secai-radar.zimax.net`

### Updating Public Documentation

**When you need to update the wiki**:

```bash
# Switch to gh-pages branch
git checkout gh-pages
git pull origin gh-pages

# Edit wiki documentation in docs/wiki/
# For example:
# - docs/wiki/Home.md
# - docs/wiki/User-Guide.md
# - docs/wiki/API-Reference.md

# Commit and push
git add docs/wiki/
git commit -m "Update wiki documentation"
git push origin gh-pages

# Switch back to main when done
git checkout main
```

**What happens**:
- Changes are committed to `gh-pages` branch
- GitHub Actions workflow automatically builds and deploys to GitHub Pages
- Wiki is updated at `wiki.secai-radar.zimax.net`
- Custom domain SSL certificate is automatically maintained

## Switching Contexts

### From App Development to Documentation

**Scenario**: You're working on a feature in `main` and need to document it for users

```bash
# 1. Finish your current work on main
git add .
git commit -m "Add new feature"
git push origin main

# 2. Switch to gh-pages branch
git checkout gh-pages

# 3. Update wiki documentation
# Edit docs/wiki/ files as needed

# 4. Commit wiki changes
git add docs/wiki/
git commit -m "Document new feature in wiki"
git push origin gh-pages

# 5. Return to main for continued development
git checkout main
```

### From Documentation to App Development

**Scenario**: You're updating wiki docs and realize you need to fix a bug

```bash
# 1. Save your wiki work (commit or stash)
git add docs/wiki/
git commit -m "WIP: Wiki documentation updates"
# OR
git stash

# 2. Switch to main
git checkout main

# 3. Fix the bug
# Make changes to api/ or web/

# 4. Commit and push
git add .
git commit -m "Fix bug description"
git push origin main

# 5. Return to wiki to finish documentation
git checkout gh-pages
git stash pop  # If you used stash
# Continue editing wiki docs
```

## Benefits of This Approach

### ✅ Clear Separation
- Application code and developer docs are in `main`
- User documentation is in `wiki`
- No risk of accidentally breaking production docs while developing

### ✅ Independent Deployments
- App changes deploy to Azure automatically
- Wiki changes deploy to GitHub Pages automatically
- No interference between deployments

### ✅ Flexible Context Switching
- Switch branches anytime to work on different aspects
- Same codebase, different contexts
- No need for separate repositories

### ✅ Version Control Benefits
- All code and docs in one repository
- Easy to reference code from documentation
- Simple to sync when needed

### ✅ Context-Aware Development
- Cursor IDE automatically understands which branch you're on
- `.cursorrules` guides you to the right files
- No confusion about where files belong

## Syncing Application Code

**When to sync**: Only if wiki documentation needs to reference updated application code

**How to sync**:

```bash
# On gh-pages branch
git checkout gh-pages

# Merge latest from main
git merge main --no-edit

# Resolve any conflicts if they occur
# (Usually minimal since wiki mainly has docs changes)

# Push updated gh-pages branch
git push origin gh-pages
```

**Note**: Most of the time, you won't need to sync. The wiki primarily contains documentation, not code references.

## Best Practices

### 1. Commit Frequently
- Commit your work on `main` before switching to `wiki`
- Commit wiki changes before switching back
- This prevents confusion about what's changed

### 2. Use Descriptive Commit Messages
- `main`: "Add user authentication feature"
- `gh-pages`: "Document user authentication in Getting Started guide"

### 3. Keep Branches in Sync (When Needed)
- Sync application code only if wiki needs updated references
- Don't sync unnecessarily (it triggers unnecessary builds)

### 4. Test Before Pushing
- Test application changes on `main` before pushing
- Preview wiki changes locally if possible before pushing to `wiki`

### 5. Use Feature Branches (Optional)
- For major features, create feature branches from `main`
- Merge to `main` when complete
- Then update wiki if needed

## Common Scenarios

### Scenario 1: New Feature Development
1. Work on `main` branch
2. Develop feature in `api/` and `web/`
3. Test locally
4. Commit and push to `main`
5. Switch to `gh-pages` branch
6. Update user documentation
7. Commit and push to `wiki`

### Scenario 2: Documentation Updates Only
1. Switch to `gh-pages` branch
2. Edit `docs/wiki/` files
3. Commit and push to `wiki`
4. Stay on `wiki` or switch back to `main`

### Scenario 3: Bug Fix During Documentation
1. On `gh-pages` branch, commit or stash changes
2. Switch to `main` branch
3. Fix bug
4. Commit and push to `main`
5. Switch back to `wiki` and continue documentation

### Scenario 4: API Changes Requiring Docs Update
1. Update API in `main` branch
2. Commit and push to `main`
3. Switch to `gh-pages` branch
4. Update API documentation in `docs/wiki/API-Reference.md`
5. Commit and push to `wiki`

## Troubleshooting

### "I'm on the wrong branch"
```bash
# Check current branch
git branch

# Switch to correct branch
git checkout main    # or
git checkout gh-pages
```

### "I have uncommitted changes when switching"
```bash
# Option 1: Commit them
git add .
git commit -m "Your message"

# Option 2: Stash them
git stash
git checkout <other-branch>
# Later, restore with: git stash pop
```

### "Wiki doesn't show my changes"
- Check that you pushed to `gh-pages` branch
- Check GitHub Actions workflow status
- Wait a few minutes for GitHub Pages to build and deploy

### "I need code from main in wiki"
- Use `git merge main` on gh-pages branch
- Or cherry-pick specific commits
- Only do this when necessary

## Summary

The dual-branch strategy provides:

- **Clear separation** between development and documentation
- **Independent deployments** to different platforms
- **Flexible context switching** between app dev and public docs
- **Same codebase** for everything, no repository juggling
- **Context-aware tooling** that understands your workflow

You can freely develop the application on `main` and update public documentation on `wiki`—all from the same repository, with seamless context switching as needed.

