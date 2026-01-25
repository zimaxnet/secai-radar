# GitHub Issue Templates Update - Summary

**Date:** 2026-01-23  
**Status:** ✅ Complete

## Overview

All GitHub issue templates have been updated to align with the Verified MCP MVP project structure, labels, milestones, and workflow.

## What Was Updated

### Templates Updated (6 files)

1. **`task.yml`** - Task / Chore template
2. **`feature.yml`** - Feature / Endpoint / Service template
3. **`bug.yml`** - Bug template
4. **`epic.yml`** - Epic template
5. **`spike.yml`** - Spike / Research template
6. **`config.yml`** - Template configuration

### Key Changes Made

#### 1. Label Alignment ✅
- **Before:** Hardcoded labels like `type:task`, `type:feature`
- **After:** Removed hardcoded labels, added Category/Priority/Phase dropdowns
- **Result:** Templates now use dropdowns that match our label structure

#### 2. Category Dropdowns ✅
Added Category dropdown to all templates with options:
- `category:frontend`
- `category:backend`
- `category:data`
- `category:pipeline`
- `category:security`
- `category:devops`
- `category:ux`

#### 3. Priority Dropdowns ✅
Updated Priority dropdowns to use label format:
- `priority:p0` (Critical - must have for MVP)
- `priority:p1` (High - important for MVP)
- `priority:p2` (Nice to have - post-MVP)

#### 4. Phase Dropdowns ✅
Updated Phase dropdowns to use label format:
- `phase:0` (Phase 0: Foundation)
- `phase:1` (Phase 1: Public MVP)
- `phase:2` (Phase 2: Automation)
- `phase:3` (Phase 3: Private Registry)
- `phase:4` (Phase 4: Graph + Hardening)
- `phase:post-mvp` (Post-MVP)

#### 5. Service Options Updated ✅
Updated service options in Feature and Bug templates to match monorepo structure:
- `apps/public-web` (secairadar.cloud)
- `apps/public-api` (secairadar.cloud)
- `apps/registry-api` (secairadar.cloud)
- `apps/private-web` (app.secairadar.cloud)
- `apps/workers/scout`
- `apps/workers/curator`
- `apps/workers/evidence-miner`
- `apps/workers/scorer`
- `apps/workers/drift-sentinel`
- `apps/workers/publisher`
- `apps/workers/sage-meridian`
- `apps/workers/graph-builder`
- `packages/shared`
- `packages/scoring`
- `infrastructure`

#### 6. Backlog Integration ✅
Added "Backlog Ticket Reference" field to all templates:
- Allows linking issues to backlog tickets (e.g., T-001)
- Helps track which issues correspond to planned work

#### 7. Config Updates ✅
Enhanced `config.yml` with additional contact links:
- Security vulnerability disclosure (existing)
- Product + methodology (existing)
- **Backlog & Implementation Plan** (new)
- **GitHub Project Board** (new)

## Template Details

### Task / Chore Template
**Use for:** Smaller engineering tasks (refactor, wiring, config, docs, CI, infra)

**Fields:**
- Category (dropdown)
- Priority (dropdown)
- Phase (dropdown)
- Task description
- Implementation checklist
- Done when criteria
- Dependencies / links
- Backlog ticket reference

### Feature / Endpoint / Service Template
**Use for:** Implementing or enhancing endpoints, pages, services, workers, or shared packages

**Fields:**
- Category, Priority, Phase (dropdowns)
- Primary service (dropdown with monorepo structure)
- Domain surface (dropdown)
- Summary, Goal/Outcome
- In scope / Out of scope
- Interfaces (routes, endpoints, events)
- Data model impact
- Security & privacy considerations
- Acceptance criteria
- Dependencies / Blockers
- References
- Quality gates (checkboxes)
- Notes for implementation
- Backlog ticket reference

### Bug Template
**Use for:** Something broken or incorrect (runtime, UI, data, scoring, pipeline)

**Fields:**
- Severity (S0-S3)
- Category (dropdown)
- Service (dropdown with monorepo structure)
- What happened?
- Steps to reproduce
- Expected behavior
- Logs / screenshots / request IDs
- Proposed fix (if known)
- Related issues / backlog tickets

### Epic Template
**Use for:** Large multi-issue initiatives (P0/P1 milestone or full phase)

**Fields:**
- Priority, Phase (dropdowns)
- Epic objective
- Scope (what's included)
- Non-goals
- Child issues checklist
- Exit criteria (enhanced)
- Backlog ticket reference

### Spike / Research Template
**Use for:** Time-boxed research to de-risk architecture, scoring, security, or requirements

**Fields:**
- Category, Phase (dropdowns)
- Research question
- Timebox
- Deliverables
- Backlog ticket reference

## Files Location

All updated templates are in:
```
.github/ISSUE_TEMPLATE/
  - bug.yml ✅
  - config.yml ✅
  - epic.yml ✅
  - feature.yml ✅
  - spike.yml ✅
  - task.yml ✅
  - workflow-failure.md (existing, unchanged)
  - README.md (new documentation)
```

## Important Notes

### Label Application
**Note:** GitHub issue forms store dropdown values in the issue body but don't automatically apply them as labels. You have two options:

1. **Manual:** Apply labels manually after creating the issue
2. **Automation:** Set up a GitHub Action to read form responses and apply labels automatically (recommended for future)

The dropdown values are still useful for:
- Structured issue creation
- Categorization in issue body
- Automation scripts
- Reporting and filtering

### Template Usage
When creating a new issue:
1. Click "New Issue" on GitHub
2. Select the appropriate template
3. Fill in all required fields (Category, Priority, Phase)
4. Reference backlog ticket if applicable (e.g., T-001)
5. Submit the issue
6. **Apply labels manually** based on your dropdown selections (or set up automation)

## Next Steps

1. ✅ **Templates Updated** - Complete
2. **Test Templates** - Create a test issue to verify form works correctly
3. **Set Up Automation** (Optional) - Create GitHub Action to auto-apply labels from form responses
4. **Team Training** - Share template usage with team

## References

- **Templates Location:** `.github/ISSUE_TEMPLATE/`
- **Template Documentation:** `.github/ISSUE_TEMPLATE/README.md`
- **Backlog:** `docs/backlog/mvp-build-tickets.md`
- **Implementation Plan:** `docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md`
- **Project Board:** https://github.com/orgs/zimaxnet/projects/3

---

**✅ All issue templates updated and ready for use!**
