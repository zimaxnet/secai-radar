# GitHub Project and Issue Setup Guide

**Purpose:** This document provides instructions for creating the GitHub project and converting all backlog tickets to GitHub issues.

## GitHub Project Setup

### Step 1: Create GitHub Project

1. Go to the repository: https://github.com/zimaxnet/secai-radar
2. Click on "Projects" tab
3. Click "New project"
4. Choose "Board" template
5. Name: **"Verified MCP MVP Implementation"**
6. Description: "4-phase implementation plan to bring Verified MCP Trust Hub to production MVP"

### Step 2: Configure Project Columns

Set up the following columns (in order):

1. **Backlog** - All tickets not yet started
2. **Phase 0: Foundation** - Monorepo, CI/CD, Infrastructure
3. **Phase 1: Public MVP** - Database, API, Frontend Integration
4. **Phase 2: Automation** - Pipeline Workers
5. **Phase 3: Private Registry** - Auth, RBAC, Registry API/UI
6. **Phase 4: Graph + Hardening** - Graph Explorer, Security, Observability
7. **In Progress** - Currently active tickets
8. **Review** - Completed tickets awaiting review
9. **Done** - Completed and merged

### Step 3: Create Labels

Create the following labels:

**Category Labels:**
- `category:frontend` (FE)
- `category:backend` (BE)
- `category:data` (DATA)
- `category:pipeline` (PIPE)
- `category:security` (SEC)
- `category:devops` (DEVOPS)
- `category:ux` (UX)

**Priority Labels:**
- `priority:p0` (Critical - must have for MVP)
- `priority:p1` (High - important for MVP)
- `priority:p2` (Nice to have - post-MVP)

**Phase Labels:**
- `phase:0` (Foundation)
- `phase:1` (Public MVP)
- `phase:2` (Automation)
- `phase:3` (Private Registry)
- `phase:4` (Graph + Hardening)
- `phase:post-mvp` (Post-MVP)

**Status Labels:**
- `status:completed` (Already completed)
- `status:partial` (Partially complete)
- `status:blocked` (Blocked by dependencies)

### Step 4: Create Milestones

Create the following milestones:

- **Phase 0: Foundation** (Due: Week 1, Day 2)
- **Phase 1: Public MVP** (Due: Week 1, Day 7)
- **Phase 2: Automation** (Due: Week 2, Day 7)
- **Phase 3: Private Registry** (Due: Week 3, Day 7)
- **Phase 4: Graph + Hardening** (Due: Week 4, Day 7)
- **MVP Launch** (Due: Week 4, Day 7)

## Issue Creation

### Issue Template

Use this template for each issue:

```markdown
## Description
[Full description from backlog ticket]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Dependencies
- Depends on: #[issue-number] (if applicable)
- Blocks: #[issue-number] (if applicable)

## Estimated Effort
[X hours]

## Technical Notes
[Any technical considerations or related files]

## References
- Backlog Ticket: T-XXX
- Related Docs: [links to relevant documentation]
```

### Automated Issue Creation

You can use the GitHub CLI (`gh`) to create issues in bulk. Here's a script template:

```bash
#!/bin/bash

# Set repository
REPO="zimaxnet/secai-radar"

# Function to create issue
create_issue() {
    local ticket_id=$1
    local title=$2
    local body=$3
    local labels=$4
    local milestone=$5
    
    gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --milestone "$milestone"
}

# Example: Create T-001
create_issue \
    "T-001" \
    "T-001: Monorepo scaffolding" \
    "$(cat <<EOF
## Description
Create repo structure (\`apps/public-web\`, \`apps/public-api\`, \`apps/registry-api\`, \`apps/workers/*\`, \`packages/shared\`).

## Acceptance Criteria
- [ ] Folder structure exists with readme per app
- [ ] \`packages/shared\` exports types + schemas placeholder
- [ ] Workspace configured; one command builds all apps

## Estimated Effort
4 hours

## References
- Backlog Ticket: T-001
- Related Docs: docs/backlog/mvp-build-tickets.md
EOF
)" \
    "category:devops,priority:p0,phase:0" \
    "Phase 0: Foundation"
```

### Manual Issue Creation Checklist

For each ticket in `docs/backlog/mvp-build-tickets.md`:

1. [ ] Create issue with ticket ID and name as title
2. [ ] Add full description from backlog
3. [ ] Add acceptance criteria (as checklist)
4. [ ] Add dependencies (link to other issues)
5. [ ] Add labels (category, priority, phase, status if completed/partial)
6. [ ] Add milestone (appropriate phase)
7. [ ] Add to appropriate project column
8. [ ] Link to backlog ticket in references

## Issue List by Phase

### Phase 0: Foundation (4 issues)

- [ ] **T-001**: Monorepo scaffolding
- [ ] **T-002**: GitHub Actions: build/test pipeline
- [ ] **T-003**: Deploy pipeline skeleton (staging)
- [x] **T-004**: Standard copy + disclaimer snippets package (✅ Completed)

### Phase 1: Public MVP (22 issues)

**Data + Migrations:**
- [ ] **T-010**: Postgres schema + migrations v0
- [ ] **T-011**: Latest projections
- [ ] **T-012**: Rankings cache table

**Public API:**
- [ ] **T-020**: Public API skeleton + response envelope
- [ ] **T-021**: GET summary endpoint
- [ ] **T-022**: GET rankings endpoint with filters
- [ ] **T-023**: GET server detail endpoint
- [ ] **T-024**: GET server evidence endpoint
- [ ] **T-025**: GET server drift endpoint
- [ ] **T-026**: GET daily brief endpoint
- [ ] **T-027**: HTTP caching (ETag + Cache-Control)
- [ ] **T-030**: RSS/Atom renderer
- [ ] **T-031**: JSON Feed renderer

**Public Web UI:**
- [x] **T-040**: Public web shell + routing (✅ Completed)
- [x] **T-041**: Overview dashboard modules (✅ Completed)
- [x] **T-042**: Rankings dashboard with facet filters (✅ Completed)
- [x] **T-043**: Server detail page: Overview tab (✅ Completed)
- [~] **T-044**: Server detail page: Evidence tab (🔄 Partial)
- [~] **T-045**: Server detail page: Drift tab (🔄 Partial)
- [x] **T-046**: Daily brief page (✅ Completed)
- [x] **T-047**: Methodology page (✅ Completed)
- [x] **T-048**: Submit evidence page (✅ Completed)

**Publish Safety:**
- [ ] **T-050**: Redaction middleware for public responses
- [ ] **T-051**: Staging swap publishing pattern

### Phase 2: Automation Pipeline (12 issues)

**Shared Types & Scoring:**
- [x] **T-060**: Shared types + JSON schemas (✅ Completed)
- [ ] **T-061**: Scoring library (Trust Score v1)
- [ ] **T-062**: Evidence Confidence calculator

**Workers:**
- [ ] **T-070**: Worker: Scout (discovery ingest)
- [ ] **T-071**: Worker: Curator (canonicalize + dedupe)
- [ ] **T-072**: Worker: Evidence Miner (basic docs/repo extraction)
- [ ] **T-073**: Worker: Scorer
- [ ] **T-074**: Worker: Drift Sentinel
- [ ] **T-075**: Worker: Daily Brief generator (Sage Meridian integration stub)
- [ ] **T-076**: Publisher job hooks

**Observability:**
- [ ] **T-080**: Run logs + run status table
- [ ] **T-081**: Status endpoint + stale banner support

### Phase 3: Private Trust Registry (14 issues)

**Authentication & RBAC:**
- [ ] **T-090**: Entra OIDC auth for registry-api
- [ ] **T-091**: Workspace + membership tables
- [ ] **T-092**: RBAC middleware

**Registry API:**
- [ ] **T-100**: Registry: list/add servers to workspace inventory
- [ ] **T-101**: Registry: policies CRUD
- [ ] **T-102**: Registry: policy approvals
- [ ] **T-103**: Evidence pack upload (private blob)
- [ ] **T-104**: Evidence pack validation workflow
- [ ] **T-105**: Audit pack export v0 (JSON)

**Private Web UI:**
- [ ] **T-110**: Private shell + login redirect
- [ ] **T-111**: Registry inventory UI
- [ ] **T-112**: Policy UI (create + list)
- [ ] **T-113**: Evidence pack upload UI

**Audit:**
- [ ] **T-131**: Audit logging (private)

### Phase 4: Graph Explorer + Hardening (8 issues)

**Graph:**
- [ ] **T-120**: Graph snapshot builder job
- [ ] **T-121**: Public server graph endpoint
- [~] **T-122**: Graph tab UI (MVP viewer) (🔄 Partial)

**Security:**
- [ ] **T-130**: Public rate limiting + WAF rules (baseline)
- [ ] **T-132**: Backups + retention policy for DB + blobs

**Observability:**
- [ ] **T-133**: Observability dashboard

**Legal:**
- [ ] **T-134**: Fairness + right-to-respond page + contact channel

### Post-MVP (6 issues)

- [ ] **T-200**: Compare tray (rankings)
- [ ] **T-201**: Provider portfolio endpoints + pages
- [ ] **T-202**: Doc hash diff + richer drift classification
- [ ] **T-203**: Visual cards gallery + immutable asset URLs
- [ ] **T-204**: Service Bus eventing for pipeline scaling
- [ ] **T-205**: Search via Azure AI Search (typeahead + facets)

## Quick Start Commands

### Using GitHub CLI

```bash
# Install GitHub CLI if not installed
# brew install gh (macOS)
# or visit: https://cli.github.com/

# Authenticate
gh auth login

# Set default repository
gh repo set-default zimaxnet/secai-radar

# Create a single issue
gh issue create \
  --title "T-001: Monorepo scaffolding" \
  --body-file issue-template.md \
  --label "category:devops,priority:p0,phase:0" \
  --milestone "Phase 0: Foundation"
```

### Using GitHub API

You can also use the GitHub API directly with curl or a script:

```bash
# Set your GitHub token
export GITHUB_TOKEN="your-token-here"

# Create issue via API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/zimaxnet/secai-radar/issues \
  -d '{
    "title": "T-001: Monorepo scaffolding",
    "body": "## Description\n...",
    "labels": ["category:devops", "priority:p0", "phase:0"],
    "milestone": 1
  }'
```

## Next Steps

1. **Create GitHub Project** - Follow Step 1-3 above
2. **Create Milestones** - Follow Step 4 above
3. **Create Issues** - Use the checklist above or automated script
4. **Organize Issues** - Move issues to appropriate project columns
5. **Begin Work** - Start with Phase 0 tickets

---

**Reference:** See `docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md` for complete plan details.
