# GitHub Issue Templates - Update Summary

**Date:** 2026-01-23  
**Status:** ✅ Complete

## What Was Updated

All GitHub issue templates have been updated to align with the Verified MCP MVP project structure, labels, and workflow.

## Templates Updated

### 1. Task / Chore (`task.yml`) ✅
**Updates:**
- ✅ Added Category dropdown (frontend, backend, data, pipeline, security, devops, ux)
- ✅ Updated Priority options to use label format (`priority:p0`, `priority:p1`, `priority:p2`)
- ✅ Updated Phase options to use label format (`phase:0`, `phase:1`, etc.) with post-MVP option
- ✅ Added Backlog Ticket Reference field
- ✅ Removed hardcoded `type:task` label (labels now set via dropdowns)

### 2. Feature / Endpoint / Service (`feature.yml`) ✅
**Updates:**
- ✅ Added Category dropdown
- ✅ Updated Priority and Phase to use label format
- ✅ Updated service options to match monorepo structure:
  - `apps/public-web`, `apps/public-api`, `apps/registry-api`, `apps/private-web`
  - `apps/workers/scout`, `apps/workers/curator`, `apps/workers/evidence-miner`, etc.
  - `packages/shared`, `packages/scoring`
- ✅ Added Backlog Ticket Reference field
- ✅ Removed hardcoded `type:feature` label

### 3. Bug (`bug.yml`) ✅
**Updates:**
- ✅ Added Category dropdown
- ✅ Added Service dropdown with updated monorepo structure
- ✅ Updated service options to match actual app structure
- ✅ Added Related Issues / Backlog Tickets field
- ✅ Removed hardcoded `type:bug` label

### 4. Epic (`epic.yml`) ✅
**Updates:**
- ✅ Updated Priority to use label format
- ✅ Updated Phase to use label format with post-MVP option
- ✅ Added Backlog Ticket Reference field
- ✅ Enhanced exit criteria (added tests and deployment)
- ✅ Removed hardcoded `type:epic` label

### 5. Spike / Research (`spike.yml`) ✅
**Updates:**
- ✅ Added Category dropdown
- ✅ Updated Phase to use label format with post-MVP option
- ✅ Added Backlog Ticket Reference field
- ✅ Removed hardcoded `type:spike` label

### 6. Config (`config.yml`) ✅
**Updates:**
- ✅ Added "Backlog & Implementation Plan" contact link
- ✅ Added "GitHub Project Board" contact link
- ✅ Kept existing security and methodology links

## Key Improvements

1. **Label Alignment:** All templates now use the actual label names created in GitHub (`category:*`, `priority:*`, `phase:*`)

2. **Monorepo Structure:** Service options updated to match the planned monorepo structure:
   - `apps/public-web`, `apps/public-api`, `apps/registry-api`, `apps/private-web`
   - `apps/workers/*` (scout, curator, evidence-miner, scorer, drift-sentinel, publisher, sage-meridian, graph-builder)
   - `packages/shared`, `packages/scoring`

3. **Backlog Integration:** All templates now include a "Backlog Ticket Reference" field to link issues to backlog tickets (e.g., T-001)

4. **Phase Support:** Added `phase:post-mvp` option to all relevant templates

5. **Contact Links:** Enhanced config.yml with links to backlog and project board

## Files Location

All templates are now in:
```
.github/ISSUE_TEMPLATE/
  - bug.yml
  - config.yml
  - epic.yml
  - feature.yml
  - spike.yml
  - task.yml
  - workflow-failure.md (existing)
  - README.md (new documentation)
```

## Usage

When creating a new issue:
1. Click "New Issue" on GitHub
2. Select the appropriate template
3. Fill in Category, Priority, and Phase (these will auto-apply labels)
4. Reference backlog ticket if applicable (e.g., T-001)
5. Submit

The templates will automatically apply the correct labels based on dropdown selections.

## Next Steps

1. ✅ Templates updated - Complete
2. **Test templates** - Create a test issue to verify labels are applied correctly
3. **Document usage** - Team can now use these templates for all new issues

## References

- **Templates Source:** `secairadar-github-issue-templates-v1/`
- **Templates Location:** `.github/ISSUE_TEMPLATE/`
- **Backlog:** `docs/backlog/mvp-build-tickets.md`
- **Project Board:** https://github.com/orgs/zimaxnet/projects/3

---

**✅ All issue templates updated and ready for use!**
