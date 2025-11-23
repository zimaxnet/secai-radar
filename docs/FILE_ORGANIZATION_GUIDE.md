# File Organization Guide

## Overview

This guide ensures all files are organized into proper scaffolding. **All files should be in appropriate subdirectories, NOT in root directories.**

## Directory Structure Rules

### Root Directory (`/Users/derek/.../code/SecAI/`)
**ONLY these files allowed in root:**
- `README.md` - Project README

**All other files must be in subdirectories:**
- Documentation → `docs/`
- Application code → `secai-radar/`
- Analysis scripts → `analysis/`
- Sanitized files → `sanitized/`

### Application Root (`secai-radar/`)
**ONLY these files allowed in root:**
- `README.md` - Application README
- `.gitignore` - Git ignore rules
- `.cursorrules` - Cursor AI rules

**All other files must be in subdirectories:**
- Backend code → `backend/`
- Frontend code → `frontend/`
- Documentation → `docs/`
- Scripts → `scripts/`
- Infrastructure → `infra/`
- Configuration → `config/`
- Seed data → `seeds/`
- Archived code → `archive_v1/`

## File Locations

### Documentation Files

**Root Level Documentation:**
- `docs/summaries/` - Implementation summaries
- `docs/guides/` - Comprehensive guides
- `docs/wiki/` - Wiki documentation (for gh-pages)

**Application Documentation:**
- `secai-radar/docs/wiki/` - Application wiki source
- `secai-radar/docs/summaries/` - Application summaries
- `secai-radar/docs/` - Other application docs

### Code Files

**Backend Code:**
- `secai-radar/backend/main.py` - FastAPI app entry
- `secai-radar/backend/requirements.txt` - Dependencies
- `secai-radar/backend/src/routes/` - API routes
- `secai-radar/backend/src/services/` - Business logic
- `secai-radar/backend/src/agents/` - AI agents
- `secai-radar/backend/src/integrations/` - External integrations
- `secai-radar/backend/src/orchestrator.py` - Orchestrator

**Frontend Code:**
- `secai-radar/frontend/package.json` - Dependencies
- `secai-radar/frontend/src/App.tsx` - Main app
- `secai-radar/frontend/src/components/` - React components
- `secai-radar/frontend/src/pages/` - Page components
- `secai-radar/frontend/src/services/` - API clients
- `secai-radar/frontend/src/data/` - Static data

## Writing Files - Rules

**When creating new files:**
1. ✅ **ALWAYS** write to appropriate subdirectories
2. ❌ **NEVER** write to root directories (except README.md)
3. ✅ Check file location before creating
4. ✅ Use existing directory structure
5. ✅ Create subdirectories if needed

**Examples:**
- ✅ `secai-radar/backend/main.py` - CORRECT
- ❌ `main.py` - WRONG (root)
- ✅ `secai-radar/frontend/src/pages/Dashboard.tsx` - CORRECT
- ❌ `Dashboard.tsx` - WRONG (root)
- ✅ `docs/summaries/IMPLEMENTATION_SUMMARY.md` - CORRECT
- ❌ `IMPLEMENTATION_SUMMARY.md` - WRONG (root)

## Verification Checklist

Before committing:
- [ ] No .md files in root (except README.md)
- [ ] All documentation in `docs/` or `secai-radar/docs/`
- [ ] All backend code in `secai-radar/backend/`
- [ ] All frontend code in `secai-radar/frontend/`
- [ ] All scripts in `secai-radar/scripts/`
- [ ] All config in `secai-radar/config/`

---

**Last Updated**: 2025-01-15

