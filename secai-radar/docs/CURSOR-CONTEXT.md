# Cursor Context Guide for SecAI Radar

## Overview

This guide helps you use Cursor effectively when working on SecAI Radar, especially when switching between the `main` and `wiki` branches.

## Branch Awareness in Cursor

### Current Branch Detection

Cursor automatically detects which branch you're on. To verify:
- Check the status bar in Cursor (usually shows current branch)
- Or check terminal: `git branch`

### Context Files

Cursor uses these files for context:
- `.cursorrules` - Contains branch structure awareness and documentation rules
- `docs/PROMPTING-GUIDE.md` - Advanced prompting principles for SecAI Radar development
- `docs/PROMPTING-QUICK-REF.md` - Quick reference for common prompting patterns
- Files you open in the editor
- Files in your current workspace

## Working with Main Branch (Application Development)

### When to Work on Main
- Developing new features
- Updating API endpoints
- Modifying web UI
- Writing developer documentation
- Fixing bugs in application code

### Files to Edit
- `api/**` - API code
- `web/**` - Web application code
- `docs/**` (excluding `docs/wiki/`) - Developer documentation
- `.github/workflows/azure-*.yml` - Deployment workflows

### Documentation to Update
- Architecture Decision Records: `docs/adr/`
- Deployment guides: `docs/deployment*.md`
- Development guides: `docs/QUICK-START.md`, etc.

## Working with Wiki Branch (User Documentation)

### When to Work on Wiki Branch
- Updating user-facing documentation
- Adding wiki pages
- Fixing GitHub Pages deployment
- Updating wiki content

### Switching to Wiki Branch
```bash
git checkout wiki
```

### Files to Edit
- `docs/wiki/**` - Wiki documentation content
- `.github/workflows/pages.yml` - GitHub Pages workflow
- `docs/wiki/CNAME` - Custom domain configuration

### After Making Changes
```bash
git add docs/wiki/
git commit -m "Update wiki documentation"
git push origin wiki
```

## Cursor Tips for Branch Context

### 1. Use `.cursorrules` for Context
The `.cursorrules` file contains branch awareness. Cursor will:
- Understand which branch you're on
- Know where to place documentation
- Guide you on branch-specific workflows

### 2. Open Relevant Files
When working on a specific branch:
- Open files relevant to that branch
- Cursor will use these for context
- Close files from other branches if not needed

### 3. Use Cursor's Context Menu
- Right-click on files to see branch-aware options
- Use "Add to Context" for important files
- Reference branch structure docs when needed

### 4. Switch Context When Changing Branches
When switching branches:
1. Close files that don't exist in the new branch
2. Open files relevant to the new branch
3. Cursor will update its context automatically

## Common Workflows

### Workflow 1: Adding a Feature to Main
1. Ensure you're on `main`: `git checkout main`
2. Open relevant files in Cursor (`api/`, `web/`)
3. Make changes
4. Commit and push to `main`
5. If wiki needs to reference the feature, switch to `wiki` and update docs

### Workflow 2: Updating Wiki Documentation
1. Switch to `wiki`: `git checkout wiki`
2. Open `docs/wiki/` files in Cursor
3. Make documentation changes
4. Commit and push to `wiki`
5. GitHub Pages will deploy automatically

### Workflow 3: Syncing Application Code to Wiki
Only needed if wiki references need updated code:
1. On `wiki` branch: `git checkout wiki`
2. Merge from main: `git merge main --no-edit`
3. Resolve conflicts if any
4. Push to `wiki`

## Cursor Settings for Branch Awareness

### Recommended Settings
1. **Enable Git Branch Detection**: Cursor should show current branch
2. **Open Files from Current Branch**: When switching branches, be aware of open files
3. **Use `.cursorrules`**: Ensure `.cursorrules` is loaded for context

### File Watchers
- Cursor watches files in your workspace
- Changes to `.cursorrules` will update context
- Git branch changes update Cursor's understanding

## Tips for Maintaining Context

### 1. Keep Documentation in Sync
- Update `docs/BRANCH-STRUCTURE.md` when branch structure changes
- Update `.cursorrules` if workflow changes
- Document branch-specific conventions

### 2. Use Branch-Specific Documentation
- `main` branch docs: For developers
- `wiki` branch docs: For end users
- Keep them separate but consistent

### 3. Reference Branch Structure
When unsure which branch to use:
- Check `docs/BRANCH-STRUCTURE.md`
- Review `.cursorrules` for guidance
- Ask Cursor: "Which branch should I use for [task]?"

## Troubleshooting

### Cursor Not Aware of Branch
- Check if `.cursorrules` is in the root directory
- Verify you're on the correct branch
- Restart Cursor if needed

### Wrong Documentation Location
- Check `.cursorrules` for documentation rules
- Verify you're on the correct branch
- Review `docs/BRANCH-STRUCTURE.md`

### Context Confusion
- Close files from other branches
- Open files relevant to current branch
- Check `.cursorrules` for branch-specific guidance

## Summary

- **`.cursorrules` is branch-aware**: It knows about `main` vs `wiki` branches
- **Cursor detects current branch**: Automatically through Git integration
- **Context updates**: When you switch branches, update open files
- **Documentation separation**: Developer docs in `main`, user docs in `wiki`
- **Workflow awareness**: `.cursorrules` guides you on which branch to use

For more details, see `docs/BRANCH-STRUCTURE.md`.

