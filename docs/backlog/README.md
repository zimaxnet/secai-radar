# SecAI Radar Verified MCP - Backlog Management

This directory contains the MVP build tickets and backlog management documentation.

## Files

- `mvp-build-tickets.md` - Complete backlog of 60+ tickets organized by phase
- `ticket-template.md` - Template for creating new tickets
- `README.md` - This file

## Backlog Organization

### By Phase
- **Phase 0** (Day 1-2): Repo + CI Skeleton (4 tickets)
- **Phase 1** (Week 1): Public MVP "Truth Hub" (22 tickets)
- **Phase 2** (Week 2): Automation Pipeline MVP (12 tickets)
- **Phase 3** (Week 3): Private Trust Registry MVP (14 tickets)
- **Phase 4** (Week 4): GK Explorer MVP + Hardening (8 tickets)
- **Post-MVP**: Optional nice-to-have tickets (6 tickets)

### By Category
- **FE** (Frontend): 15 tickets
- **BE** (Backend/API): 18 tickets
- **DATA** (Data/Database): 5 tickets
- **PIPE** (Pipeline/Agents): 10 tickets
- **SEC** (Security): 5 tickets
- **DEVOPS** (CI/CD/Infra): 7 tickets
- **UX** (Copy/Docs): 2 tickets

## Ticket Tracking

### Current Status Summary

**Completed:** 8 tickets  
**In Progress / Partial:** 4 tickets  
**Pending:** 48+ tickets

### Key Completed Tickets
- T-004: Copy system package ✅
- T-040: Public web shell + routing ✅
- T-041: Overview dashboard modules ✅
- T-042: Rankings dashboard ✅
- T-043: Server detail Overview tab ✅
- T-046: Daily brief page ✅
- T-047: Methodology page ✅
- T-048: Submit evidence page ✅
- T-060: Shared types + JSON schemas ✅

### Critical Path (P0 Tickets)

**Phase 0:**
- T-001: Monorepo scaffolding
- T-002: GitHub Actions CI
- T-003: Deploy pipeline

**Phase 1:**
- T-010: Postgres schema
- T-011: Latest projections
- T-020: Public API skeleton
- T-021-T-026: All public API endpoints
- T-030-T-031: Feed renderers

**Phase 2:**
- T-061: Scoring library
- T-062: Evidence Confidence calculator
- T-070-T-076: All pipeline workers

**Phase 3:**
- T-090-T-092: Auth + RBAC
- T-100-T-105: Registry endpoints
- T-110-T-113: Registry UI

**Phase 4:**
- T-120-T-122: Graph builder + endpoint + UI
- T-131: Audit logging

## Using This Backlog

1. **For Planning:** Review tickets by phase to understand dependencies
2. **For Development:** Start with Phase 0, work through phases sequentially
3. **For Tracking:** Update ticket status as work progresses
4. **For Estimation:** Use estimated effort to plan sprints

## Next Steps

1. Set up project management tool (GitHub Projects, Jira, etc.)
2. Import tickets from `mvp-build-tickets.md`
3. Assign tickets to team members
4. Begin Phase 0 implementation
