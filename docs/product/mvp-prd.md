# SecAI Radar Verified MCP - MVP PRD

**Version:** v0.1  
**Date:** 2026-01-23  
**Product:** Verified MCP (public trust hub) + Trust Registry (private)  
**Owner:** Zimax Networks LC (umbrella), delivered via SecAI Radar + ctxeco + openContextGraph (MIT)

## Problem Statement

MCP server lists are helpful but feel like a **black box**:
- No consistent security posture scoring
- No evidence trail
- No drift visibility ("what changed since yesterday?")
- No governance path for enterprise adoption

Verified MCP solves this by providing a **trusted authority**: teach, mentor, and guide organizations with transparent rankings, evidence confidence, drift timelines, and a trust graph.

## Target Users / Personas

### 1. Security Architect / GRC Lead
- **Wants:** Risk posture, evidence, audit exports, governance controls
- **Key Features:** Trust Score breakdown, evidence confidence, drift timeline, audit pack exports
- **Success Metric:** Uses evidence tab and exports audit packs

### 2. Platform Engineer / Developer
- **Wants:** "What works", integration patterns, safe defaults, troubleshooting
- **Key Features:** Rankings, server detail, tool agency, deployment types
- **Success Metric:** Finds and adopts servers based on rankings

### 3. Vendor / MCP Provider
- **Wants:** Visibility and a fair path to improve ranking via evidence packs
- **Key Features:** Provider portfolio, evidence submission, right-to-respond
- **Success Metric:** Submits evidence packs and improves ranking

### 4. Analyst / Researcher / Journalist
- **Wants:** Daily updates and "what changed" signals for stories
- **Key Features:** Daily brief, RSS/JSON feeds, drift events
- **Success Metric:** Subscribes to feeds and references in articles

## MVP Goals (Must Ship)

- Public trust hub at **secairadar.cloud/mcp**
- Rankings + server detail with:
  - Trust Score + Tier
  - Evidence Confidence + evidence links
  - Drift timeline (at least score/evidence/flags)
  - "Why it scored this way" explainability
- Daily Trust Brief page + RSS/JSON feeds
- Outbox drafts for daily social posts (X, LinkedIn)

## MVP Non-Goals (Explicitly Not Required at Launch)

- Full vendor verification/certification claims (avoid)
- Real-time posting automation to every platform (drafts are enough)
- Deep scanning of private endpoints or intrusive testing
- Full graph DB (graph snapshots ok for MVP)
- Private Trust Registry full implementation (skeleton ok)

## Success Metrics (MVP)

### Freshness
- **Target:** Daily run success rate ≥ 95% (last assessed within 24h)
- **Measurement:** Pipeline run logs, "last assessed" timestamps

### Engagement
- **Target:** CTR from overview → server detail ≥ 25%
- **Measurement:** Analytics event tracking

### Trust
- **Target:** % of server pages viewed with evidence tab opened ≥ 30%
- **Measurement:** Analytics event tracking

### Growth
- **Target:** Tracked servers increases week-over-week
- **Measurement:** Database counts, new entrants tracking

### Conversion
- **Target:** Evidence submissions from providers; enterprise inquiries to ctxeco
- **Measurement:** Evidence pack submissions, ctxeco demo requests

## MVP Scope

### In Scope
- Public trust hub (rankings, server detail, daily brief)
- Evidence confidence system (0-3)
- Drift detection and timeline
- Daily automation pipeline
- RSS/JSON feeds
- Basic graph explorer (JSON snapshots)
- Evidence submission workflow (public)
- Methodology page with disclaimers

### Out of Scope (v1+)
- Full private Trust Registry (MVP: skeleton only)
- Real-time social media posting (MVP: drafts only)
- Advanced graph queries (MVP: static snapshots)
- Provider certification program
- Real-time endpoint monitoring
- Advanced search (MVP: basic filters)

## User Flows

### Flow 1: Security Architect Discovers Server
1. Lands on `/mcp` overview
2. Clicks "Rankings" → filters by tier A/B
3. Clicks server → views server detail
4. Opens "Evidence" tab → reviews evidence links
5. Opens "Drift" tab → checks recent changes
6. Downloads evidence for audit trail

### Flow 2: Developer Finds Integration
1. Searches for specific category (e.g., "Cloud")
2. Filters by deployment type "Remote"
3. Sorts by Trust Score
4. Clicks top result → reviews integration docs
5. Checks tool agency and auth model

### Flow 3: Provider Submits Evidence
1. Views provider portfolio page
2. Sees low evidence confidence
3. Clicks "Submit Evidence"
4. Fills out submission form
5. Uploads evidence pack
6. Receives confirmation

### Flow 4: Analyst Tracks Daily Updates
1. Subscribes to RSS feed
2. Receives daily brief in feed reader
3. Clicks through to full brief
4. Reviews top movers and downgrades
5. Clicks server links for details

## Technical Constraints

- Must work with Azure Static Web Apps (current hosting)
- Must support daily automation pipeline
- Must maintain append-only audit trail
- Must support multi-tenant isolation (private registry)
- Must be performant with caching

## Launch Criteria

- [ ] All MVP pages functional and tested
- [ ] Daily pipeline runs successfully
- [ ] Feeds validated and accessible
- [ ] Methodology page complete with disclaimers
- [ ] Evidence submission workflow working
- [ ] Analytics tracking implemented
- [ ] Performance targets met (page load < 2s)
- [ ] Mobile responsive design
