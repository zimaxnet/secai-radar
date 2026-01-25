# GitHub Issue Templates

This directory contains GitHub issue templates for the SecAI Radar Verified MCP project.

## Available Templates

### 1. Task / Chore
**File:** `task.yml`  
**Use for:** Smaller engineering tasks (refactor, wiring, config, docs, CI, infra)

**Fields:**
- Category (frontend, backend, data, pipeline, security, devops, ux)
- Priority (p0, p1, p2)
- Phase (0-4, post-mvp)
- Task description
- Implementation checklist
- Done when criteria
- Dependencies / links
- Backlog ticket reference

### 2. Feature / Endpoint / Service
**File:** `feature.yml`  
**Use for:** Implementing or enhancing endpoints, pages, services, workers, or shared packages

**Fields:**
- Category
- Priority
- Phase
- Primary service (public-web, public-api, registry-api, workers, packages)
- Domain surface (secairadar.cloud, app.secairadar.cloud, internal)
- Summary
- Goal / Outcome
- In scope / Out of scope
- Interfaces (routes, endpoints, events)
- Data model impact
- Security & privacy considerations
- Acceptance criteria
- Dependencies / Blockers
- References
- Quality gates
- Notes for implementation
- Backlog ticket reference

### 3. Bug
**File:** `bug.yml`  
**Use for:** Something broken or incorrect (runtime, UI, data, scoring, pipeline)

**Fields:**
- Severity (S0-S3)
- Category
- Service affected
- What happened?
- Steps to reproduce
- Expected behavior
- Logs / screenshots / request IDs
- Proposed fix (if known)
- Related issues / backlog tickets

### 4. Epic
**File:** `epic.yml`  
**Use for:** Large multi-issue initiatives (P0/P1 milestone or full phase)

**Fields:**
- Priority
- Phase
- Epic objective
- Scope (what's included)
- Non-goals
- Child issues checklist
- Exit criteria
- Backlog ticket reference

### 5. Spike / Research
**File:** `spike.yml`  
**Use for:** Time-boxed research to de-risk architecture, scoring, security, or requirements

**Fields:**
- Category
- Phase
- Research question
- Timebox
- Deliverables
- Backlog ticket reference

## Configuration

**File:** `config.yml`

- Disables blank issues (forces template use)
- Provides contact links:
  - Security vulnerability disclosure
  - Product + methodology
  - Backlog & Implementation Plan
  - GitHub Project Board

## Label Alignment

All templates are aligned with the project's label structure:

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
- `phase:0` (Phase 0: Foundation)
- `phase:1` (Phase 1: Public MVP)
- `phase:2` (Phase 2: Automation)
- `phase:3` (Phase 3: Private Registry)
- `phase:4` (Phase 4: Graph + Hardening)
- `phase:post-mvp` (Post-MVP)

## Usage

When creating a new issue on GitHub:

1. Click "New Issue"
2. Select the appropriate template
3. Fill in all required fields
4. Add backlog ticket reference if applicable (e.g., T-001)
5. Submit the issue

**Note:** GitHub issue forms store dropdown values in the issue body. Labels are not automatically applied from dropdown selections. You can:
- Apply labels manually after creating the issue
- Set up a GitHub Action to auto-apply labels based on form responses (recommended)

The templates will:
- Structure the issue with all necessary information
- Store category, priority, and phase in the issue body for reference
- Link to relevant documentation

## References

- **Backlog:** [docs/backlog/mvp-build-tickets.md](../../docs/backlog/mvp-build-tickets.md)
- **Implementation Plan:** [docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md](../../docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md)
- **GitHub Project:** https://github.com/orgs/zimaxnet/projects/3
