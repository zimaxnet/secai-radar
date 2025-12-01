# Branch Roots Guide

## Overview

This document explains where the root directories are for the **main branch** and **gh-pages branch** in the SecAI Radar repository.

---

## Repository Location

**Git Repository Root:**
```
/Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar/
```

The git repository is located in the `secai-radar/` subdirectory.

---

## Main Branch Root

**Root Directory:** `secai-radar/` (the repository root)

**Structure:**
```
secai-radar/                    ← ROOT for main branch
├── .git/                       ← Git repository
├── backend/                    ← FastAPI backend application
│   ├── main.py
│   ├── requirements.txt
│   └── src/
├── frontend/                   ← React frontend application
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── docs/                       ← Documentation (wiki source files)
│   └── wiki/
├── archive_v1/                 ← Archived v1 code
├── start_app.sh                ← Startup script
└── README.md
```

**Main Branch Contains:**
- ✅ Application code (backend and frontend)
- ✅ Documentation source files (`docs/wiki/`)
- ✅ Archive code
- ✅ Configuration files
- ✅ All implementation code

**Absolute Path:**
```
/Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar/
```

---

## gh-pages Branch Root

**Root Directory:** `secai-radar/` (same repository, different branch)

**Structure (gh-pages branch):**
```
secai-radar/                    ← ROOT for gh-pages branch
├── _config.yml                 ← Jekyll config (if using Jekyll)
├── index.md                    ← Wiki homepage
├── Platform-Features.md        ← Wiki pages
├── Agent-Integration.md
├── Evidence-Collection.md
├── Feature-Documentation-Index.md
├── Assessment-Workflow.md
├── User-Guide.md
├── ... (other wiki pages)
└── ... (GitHub Pages files)
```

**gh-pages Branch Contains:**
- ✅ Wiki documentation files (Markdown)
- ✅ GitHub Pages configuration
- ✅ Jekyll config (if using Jekyll)
- ✅ Static site files for documentation
- ❌ NO application code (just documentation)

**Absolute Path:**
```
/Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar/
```

---

## Key Differences

### Main Branch
- **Purpose**: Application development
- **Contains**: Code + Documentation source
- **Root**: `secai-radar/`
- **Subdirectories**: `backend/`, `frontend/`, `docs/`, `archive_v1/`
- **Use**: Development, code updates, documentation source

### gh-pages Branch
- **Purpose**: Documentation publication
- **Contains**: Only documentation files
- **Root**: `secai-radar/` (same directory, different branch)
- **Subdirectories**: None (or minimal - just wiki pages at root)
- **Use**: Publishing wiki to GitHub Pages

---

## Workflow

### To Work on Application Code

```bash
cd /Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar
git checkout main
# Work on backend/ and frontend/ directories
# Documentation source is in docs/wiki/
```

### To Publish Wiki Documentation

```bash
cd /Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar
git checkout gh-pages
# Copy files from docs/wiki/ to root of gh-pages branch
# Commit and push to gh-pages
```

---

## Documentation Flow

### Step 1: Write Documentation (Main Branch)

1. **Switch to main branch:**
   ```bash
   cd secai-radar
   git checkout main
   ```

2. **Edit/create documentation in:**
   ```
   secai-radar/docs/wiki/
   ```

3. **Commit to main:**
   ```bash
   git add docs/wiki/
   git commit -m "Add new documentation"
   git push origin main
   ```

### Step 2: Publish to GitHub Pages (gh-pages Branch)

1. **Switch to gh-pages branch:**
   ```bash
   cd secai-radar
   git checkout gh-pages
   ```

2. **Copy documentation files to root:**
   ```bash
   cp -r docs/wiki/* .
   # Or selectively copy files
   cp docs/wiki/Platform-Features.md .
   cp docs/wiki/Agent-Integration.md .
   cp docs/wiki/Evidence-Collection.md .
   # etc.
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Publish new documentation to wiki"
   git push origin gh-pages
   ```

4. **GitHub Pages automatically deploys** from gh-pages branch

---

## File Locations Summary

### Documentation Source (Main Branch)

**Location:** `secai-radar/docs/wiki/`

**Files:**
- `docs/wiki/index.md`
- `docs/wiki/Platform-Features.md`
- `docs/wiki/Agent-Integration.md`
- `docs/wiki/Evidence-Collection.md`
- `docs/wiki/Feature-Documentation-Index.md`
- `docs/wiki/_config.yml`
- ... (other wiki files)

### Documentation Published (gh-pages Branch)

**Location:** `secai-radar/` (root of branch)

**Files:**
- `index.md` (copied from `docs/wiki/index.md`)
- `Platform-Features.md` (copied from `docs/wiki/Platform-Features.md`)
- `Agent-Integration.md` (copied from `docs/wiki/Agent-Integration.md`)
- `Evidence-Collection.md` (copied from `docs/wiki/Evidence-Collection.md`)
- `Feature-Documentation-Index.md` (copied from `docs/wiki/Feature-Documentation-Index.md`)
- `_config.yml` (copied from `docs/wiki/_config.yml`)
- ... (other wiki files)

---

## Quick Reference

| Item | Main Branch | gh-pages Branch |
|------|-------------|-----------------|
| **Root Path** | `secai-radar/` | `secai-radar/` |
| **Purpose** | Application code | Documentation |
| **Doc Location** | `docs/wiki/` | Root (`./`) |
| **App Code** | `backend/`, `frontend/` | ❌ Not present |
| **Publishes To** | GitHub repo | GitHub Pages |

---

## Summary

- **Main Branch Root**: `/Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar/`
  - Contains: Application code + Documentation source in `docs/wiki/`
  
- **gh-pages Branch Root**: `/Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar/`
  - Contains: Only documentation files at the root level
  - Published to: `https://zimaxnet.github.io/secai-radar/`

**Both branches use the same directory structure but contain different files!**

---

**Last Updated**: 2025-01-15

