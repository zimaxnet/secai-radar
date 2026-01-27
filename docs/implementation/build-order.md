# SecAI Radar Verified MCP - Build Order

**Based on:** Step 5 Reference Implementation Plan  
**Timeline:** MVP (4 weeks) → v1 (Weeks 5-8)

## Phase 0 (Day 1–2): Repo + CI Skeleton

### Tasks
- [x] Create mono-repo structure:
  - `/apps/public-web` - Public web application
  - `/apps/public-api` - Public API service
  - `/apps/registry-api` - Private registry API service
  - `/apps/workers/scout` - Scout worker
  - `/apps/workers/curator` - Curator worker
  - `/apps/workers/evidence-miner` - Evidence Miner worker
  - `/apps/workers/scorer` - Scorer worker
  - `/apps/workers/drift-sentinel` - Drift Sentinel worker
  - `/apps/workers/publisher` - Publisher worker
  - `/apps/workers/sage-meridian` - Sage Meridian worker
  - `/packages/shared` - Shared types, schemas, scoring rubric
  - `/packages/scoring` - Trust Score calculation library
- [x] Set up GitHub Actions pipeline: build → test → deploy (ACA)
- [ ] Configure Azure Container Registry (ACR) — optional when using GHCR
- [ ] Set up development environment documentation

## Phase 1 (Week 1): Public MVP "Truth Hub"

**Goal:** Rankings + server pages + daily brief, driven by manual seed + Batch 1.

### Day 1-2: Database Setup
- [x] Create Postgres schema + migrations (apps/public-api/migrations, migrate.py)
- [ ] Set up database connection pooling
- [x] Create seed data scripts for initial providers/servers (seed.py)
- [x] Test database migrations

### Day 3-4: Public API
- [x] Implement `/api/v1/public/mcp/summary` endpoint
- [x] Implement `/api/v1/public/mcp/recently-updated` endpoint
- [x] Implement `/api/v1/public/mcp/rankings` endpoint (with filters)
- [x] Implement `/api/v1/public/mcp/servers/{id}` endpoint
- [x] Implement `/api/v1/public/mcp/servers/{id}/evidence` endpoint
- [x] Implement `/api/v1/public/mcp/servers/{id}/drift` endpoint
- [x] Implement `/api/v1/public/mcp/daily/{date}` endpoint
- [x] Add methodology versioning headers (and attestation envelope)
- [x] Add ETag and caching support (etag.py registered in main.py; 304 returns ETag + Cache-Control)
- [x] Add error handling and response envelopes

### Day 5: Public Web UI
- [x] Implement `/mcp` overview dashboard
- [x] Implement `/mcp/rankings` rankings page
- [x] Implement `/mcp/servers/{slug}` server detail page
- [x] Implement `/mcp/daily/{date}` daily brief page
- [x] Implement `/mcp/methodology` methodology page
- [x] Connect UI to API endpoints

### Day 6-7: Feeds + Publisher
- [x] Create RSS feed renderer (`/mcp/feed.xml`)
- [x] Create JSON Feed renderer (`/mcp/feed.json`)
- [x] Implement publisher "staging swap" (T-051): latest_scores_staging, Scorer WRITE_TO_STAGING=1, Publisher validate_staging + flip
- [ ] Add validation logic for dataset completeness
- [ ] Test end-to-end: seed data → API → UI → feeds (run from apps/public-api: migrate.py → seed.py --refresh → start API; GET /api/v1/public/mcp/rankings)

## Phase 2 (Week 2): Automation Pipeline MVP (Daily Refresh)

**Goal:** Daily run that updates scores/deltas and generates briefs.

### Day 1-2: Scout + Curator
- [x] Build Scout ingestor for Tier 1 sources (raw_observations table, runnable scout, run-scout.sh; Tier 1 URL config in TIER1_SOURCES):
  - Official MCP registry (URL in code; add more sources as needed)
  - Major directory lists
  - Top 50 servers by traffic
- [x] Build Curator (T-071): canonical ID precedence (repoUrl > endpoint host > docs URL > name+source), name normalization, dedupe, review-queue log for duplicate/ambiguous; `./scripts/run-curator.sh`
- [ ] Test with sample sources (run Scout then Curator when Tier 1 returns data)

### Day 3: Evidence Miner
- [x] Build Evidence Miner (T-072): Docs/Repo evidence when repo_url/docs_url present; AuthModel, HostingCustody, ToolAgency claims; evidence_items + evidence_claims with sourceEvidenceId/capturedAt; `./scripts/run-evidence-miner.sh`
- [ ] Extend to full claim set (15 types) and parser framework
- [ ] Test with sample docs/repos (seed or Curator output with URLs)

### Day 4: Scorer
- [x] Implement Trust Score v1 (T-061/T-062 in packages/scoring): domain d1–d6 from claims, weighted score, tier, Evidence Confidence 0–3, fail-fast/risk flags, explainability; 9 tests
- [x] Scorer worker (T-073): `./scripts/run-scorer.sh`, writes score_snapshots + latest_scores
- [ ] Test scoring with sample servers that have evidence (run Scout→Curator→Miner with URLs, then Scorer)

### Day 5: Drift Sentinel
- [x] Build Drift Sentinel (T-074): diff latest vs previous score_snapshots; ScoreChanged/FlagChanged/EvidenceAdded/EvidenceRemoved with severity; topMovers/topDowngrades; `./scripts/run-drift-sentinel.sh`
- [ ] Test drift detection

### Day 6: Daily Brief Generator
- [x] Build Daily Brief generator (T-075): movers/downgrades/newEntrants/notableDrift from drift_events + score_snapshots; template in `templates/daily_brief.txt`; narrativeShort (≤600) + narrativeLong; store in daily_briefs; `./scripts/run-daily-brief.sh [YYYY-MM-DD]`
- [ ] Integrate Sage Meridian prompts for narrative_long (optional; template placeholder in place)
- [x] Store daily brief in database (date, headline, narrative_long, narrative_short, highlights, payload_json)

### Day 7: Outbox + Integration
- [ ] Create outbox schema and storage
- [ ] Generate social media drafts:
  - X thread (5-7 posts)
  - LinkedIn post
  - Reddit post (weekly)
  - HN post (major events only)
- [ ] Test end-to-end daily pipeline run

## Phase 3 (Week 3): Private Trust Registry MVP

**Goal:** Customer workspace can govern servers.

### Day 1-2: Authentication + RBAC
- [x] Set up Entra ID app registration
- [x] Implement OIDC JWT validation middleware
- [x] Implement RBAC roles:
  - RegistryAdmin
  - PolicyApprover
  - EvidenceValidator
  - Viewer
  - AutomationOperator
- [x] Add workspace isolation middleware
- [ ] Test authentication flow

### Day 3: Workspace + Membership
- [x] Implement workspace creation
- [x] Implement workspace membership management
- [x] Add role assignment logic
- [ ] Test multi-tenant isolation

### Day 4: Inventory
- [x] Implement add server to workspace
- [x] Implement server metadata (owner, purpose, environment)
- [x] Implement inventory listing
- [ ] Test inventory operations

### Day 5: Policies
- [x] Implement policy creation (allow/deny/require approval)
- [x] Implement policy scope (server/tool/category)
- [x] Implement policy conditions
- [x] Implement policy expiration
- [ ] Test policy CRUD

### Day 6: Approvals
- [x] Implement approval workflow
- [x] Implement approve/deny actions
- [x] Add approval history tracking
- [ ] Test approval workflow

### Day 7: Evidence Packs + Exports
- [x] Implement evidence pack upload to blob storage
- [x] Implement evidence pack metadata storage
- [x] Implement validation workflow
- [x] Implement audit pack export (JSON v0)
- [ ] Test evidence and export flows

## Phase 4 (Week 4): GK "Look Behind the Veil" MVP

**Goal:** Graph explorer on server pages.

### Day 1-2: Graph Snapshot Builder
- [x] Build graph snapshot builder in pipeline:
  - Server → Tools → Scopes → Data Domains → Evidence → Flags
- [x] Implement node creation (14 node types)
- [x] Implement edge creation (13 edge types)
- [x] Store graph JSON in Postgres
- [ ] Test graph generation

### Day 3-4: Graph API + Explorer
- [x] Implement `/api/v1/public/mcp/servers/{id}/graph` endpoint
- [x] Build basic interactive graph explorer UI
- [x] Add node/edge visualization
- [x] Add evidence linking
- [ ] Test graph explorer

### Day 5-7: Polish + Integration
- [x] Integrate graph explorer into server detail page
- [ ] Add graph navigation and filtering
- [ ] Test end-to-end: pipeline → graph → UI
- [ ] Performance optimization
- [ ] Documentation

## v1 (Weeks 5–8): Production Hardening + Flair

### Week 5: Infrastructure Improvements
- [ ] Move to Azure Service Bus for pipeline events
- [ ] Add Azure AI Search for fast faceted search
- [ ] Implement provider right-to-respond workflow
- [ ] Enhanced drift detection (docs hash diffing)

### Week 6: Visual Assets + Distribution
- [ ] Visual card pipeline (Sage Meridian integration)
- [ ] Store images in public-assets with immutable URLs
- [ ] Build distribution service (or manual posting)
- [ ] Test social media posting

### Week 7: Edge + Security
- [ ] Set up Azure Front Door
- [ ] Configure WAF rules
- [ ] Set up caching rules
- [x] Add rate limiting (in-API rate_limit middleware; see RATE-LIMITING-AND-WAF.md)
- [ ] Security audit

### Week 8: Observability + Documentation
- [ ] SOC2-ready logging
- [ ] Set up alerts and monitoring
- [ ] Create incident runbooks
- [ ] Complete API documentation
- [ ] User documentation

## Definition of Done (MVP Launch)

### Public
- [x] /mcp overview + rankings + server pages + daily brief
- [x] RSS + JSON feed live
- [x] Each server has Trust Score + Evidence Confidence + last assessed
- [x] Drift timeline shows at least score/evidence/flag changes

### Automation
- [x] Daily run completes end-to-end with stable publish
- [x] Daily brief text generated and stored
- [x] Outbox drafts created

### Private
- [x] Basic workspace + inventory + policy skeleton
