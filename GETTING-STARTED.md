# Getting Started - Verified MCP Implementation

**Last Updated:** 2026-01-23  
**Status:** Planning Complete, Ready for Implementation

## Quick Start Guide

When you're ready to begin implementation, start here. This document provides a clear roadmap for the first steps.

---

## What's Been Completed ✅

### Planning & Documentation (100% Complete)
- ✅ All 7 planning steps completed
- ✅ Frontend UI components and routes (using mock data)
- ✅ Type definitions and API client stubs
- ✅ Database schema designed
- ✅ Infrastructure Bicep templates created
- ✅ Backlog with 60+ tickets organized by phase
- ✅ GitHub project, milestones, labels, and issues created

### Frontend (Complete with Mock Data)
- ✅ Route structure (`/mcp/*`)
- ✅ All public pages (Overview, Rankings, Server Detail, Daily Brief, Methodology, Submit)
- ✅ UI components (TierBadge, EvidenceConfidenceBadge, FlagTooltip, Disclaimer)
- ✅ Copy system and analytics utilities
- ⏳ **Needs:** Connect to real API endpoints (replace mock data)

### Backend (Not Started)
- ⏳ API endpoints (10 endpoints defined, need implementation)
- ⏳ Database schema (defined, needs migration)
- ⏳ Automation pipeline (7 workers need implementation)

---

## Where to Start: Phase 0 (Days 1-2)

**Goal:** Set up development infrastructure and monorepo structure

### Step 1: Monorepo Restructure (T-001)

**Start Here:** This is the foundation for everything else.

**Tasks:**
1. Create monorepo structure:
   ```
   secai-radar/
   ├── apps/
   │   ├── public-web/        # Move existing web/ content here
   │   ├── public-api/        # New Python FastAPI service
   │   ├── registry-api/       # New Python FastAPI service (private)
   │   └── workers/
   │       ├── scout/
   │       ├── curator/
   │       ├── evidence-miner/
   │       ├── scorer/
   │       ├── drift-sentinel/
   │       ├── publisher/
   │       ├── sage-meridian/
   │       └── graph-builder/
   ├── packages/
   │   ├── shared/            # Shared TypeScript types, copy system
   │   └── scoring/           # Trust Score calculation library (Python)
   └── infra/                 # Existing Bicep templates
   ```

2. Move existing code:
   - `web/src/` → `apps/public-web/src/`
   - `web/src/utils/copy.ts` → `packages/shared/copy/`
   - `web/src/types/*.ts` → `packages/shared/types/`

3. Configure workspace:
   - Add `package.json` workspace config (or `pnpm-workspace.yaml`)
   - Create build scripts for each app
   - Test: one command builds all apps

**Reference:**
- **GitHub Issue:** T-001 (search in project board)
- **Backlog:** `docs/backlog/mvp-build-tickets.md` (T-001)
- **Implementation Plan:** `docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md` (Phase 0.1)

**Estimated Time:** 4 hours

---

### Step 2: CI/CD Pipeline Setup (T-002, T-003)

**After T-001 is complete**

**Tasks:**
1. Create GitHub Actions workflow (`.github/workflows/ci.yml`):
   - Lint (ESLint for TypeScript, Ruff for Python)
   - Type check (TypeScript, mypy)
   - Unit tests
   - Build all apps
   - Generate artifacts

2. Create deployment workflow (`.github/workflows/deploy-staging.yml`):
   - Deploy to Azure Container Apps (staging)
   - Use Azure Key Vault for secrets
   - Manual approval gate for production

**Reference:**
- **GitHub Issues:** T-002, T-003
- **Backlog:** `docs/backlog/mvp-build-tickets.md` (T-002, T-003)

**Estimated Time:** 14 hours (6h + 8h)

---

### Step 3: Infrastructure Deployment (T-003)

**Can be done in parallel with T-002**

**Tasks:**
1. Deploy Azure resources using Bicep:
   ```bash
   az deployment group create \
     --resource-group secai-radar-rg \
     --template-file infra/mcp-infrastructure.bicep \
     --parameters @infra/parameters/dev.bicepparam
   ```

2. Resources to deploy:
   - PostgreSQL Flexible Server
   - Storage Account (evidence-private, public-assets, exports-private containers)
   - Key Vault
   - Container Apps Environment
   - Container Registry (ACR)

**Reference:**
- **Bicep Template:** `infra/mcp-infrastructure.bicep`
- **Implementation Plan:** `docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md` (Phase 0.3)

**Estimated Time:** 2-4 hours (deployment time)

---

## After Phase 0: Phase 1 (Week 1)

Once Phase 0 is complete, proceed to Phase 1:

1. **Database Setup** (T-010, T-011, T-012)
   - Run migrations from `docs/implementation/database-schema.sql`
   - Create seed data
   - Set up connection pooling

2. **Public API Implementation** (T-020-T-031)
   - Create FastAPI application
   - Implement all 10 public endpoints
   - Add caching and redaction

3. **Frontend API Integration** (T-040-T-048)
   - Connect frontend to real API
   - Replace mock data with API calls

---

## Key Files to Reference

### Planning & Architecture
- **Master Services Doc:** `secairadar-cloud-master-services-kickoff-v1.md`
- **Implementation Plan:** `docs/IMPLEMENTATION-PLAN-AND-PREPARATION.md`
- **Build Order:** `docs/implementation/build-order.md`
- **Refactoring Progress:** `REFACTORING-PROGRESS.md`

### Backlog & Tracking
- **Backlog:** `docs/backlog/mvp-build-tickets.md`
- **GitHub Project:** https://github.com/orgs/zimaxnet/projects/3
- **Ticket Template:** `docs/backlog/ticket-template.md`

### Database & Infrastructure
- **Database Schema:** `docs/implementation/database-schema.sql`
- **Bicep Template:** `infra/mcp-infrastructure.bicep`
- **Security Model:** `docs/implementation/security-model.md`

### Type Definitions & Utilities
- **Data Models:** `web/src/types/dataModel.ts`
- **MCP Types:** `web/src/types/mcp.ts`
- **Graph Schema:** `web/src/types/graph.ts`
- **API Clients:** `web/src/api/public.ts`, `web/src/api/private.ts`

### Automation
- **Automation Blueprint:** `docs/automation/automation-blueprint.md`
- **Canonical IDs:** `web/src/utils/canonicalIds.ts`
- **Dedupe Logic:** `web/src/utils/dedupe.ts`
- **Calculations:** `web/src/utils/calculations.ts`

---

## First Day Checklist

When you return to start implementation:

- [ ] Review this document
- [ ] Check GitHub project board: https://github.com/orgs/zimaxnet/projects/3
- [ ] Review Phase 0 tickets (T-001, T-002, T-003)
- [ ] Set up local development environment
- [ ] Start with T-001: Monorepo scaffolding
- [ ] Create a branch: `feature/phase-0-monorepo-restructure`
- [ ] Begin implementation

---

## Development Environment Setup

### Prerequisites
- Node.js/pnpm (for frontend and monorepo)
- Python 3.11+ (for backend and workers)
- Azure CLI (for infrastructure)
- Docker (for local container testing)
- PostgreSQL client (for database work)

### Local Setup Steps
1. Clone repository (if not already)
2. Install dependencies (after monorepo restructure)
3. Set up local PostgreSQL (or use Azure)
4. Configure environment variables
5. Run local development servers

---

## Quick Reference: Ticket IDs

**Phase 0 (Start Here):**
- T-001: Monorepo scaffolding
- T-002: GitHub Actions: build/test pipeline
- T-003: Deploy pipeline skeleton (staging)

**Phase 1 (Week 1):**
- T-010: Postgres schema + migrations v0
- T-020: Public API skeleton + response envelope
- T-021-T-031: All public API endpoints

**Find all tickets:** `docs/backlog/mvp-build-tickets.md` or GitHub project board

---

## Support & Resources

- **GitHub Project:** https://github.com/orgs/zimaxnet/projects/3
- **Repository:** https://github.com/zimaxnet/secai-radar
- **Azure Portal:** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite
- **Issue Templates:** `.github/ISSUE_TEMPLATE/`

---

## Summary

**When you return:**
1. **Start with T-001** - Monorepo restructure (4 hours)
2. **Then T-002** - CI/CD pipeline (6 hours)
3. **Then T-003** - Infrastructure deployment (8 hours)
4. **Then Phase 1** - Database and API implementation

**Everything is planned and ready. Just start with T-001!**

---

**Last Updated:** 2026-01-23  
**Next Step:** T-001 - Monorepo scaffolding
