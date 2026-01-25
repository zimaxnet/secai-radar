# SecAI Radar Verified MCP - Build Order

**Based on:** Step 5 Reference Implementation Plan  
**Timeline:** MVP (4 weeks) → v1 (Weeks 5-8)

## Phase 0 (Day 1–2): Repo + CI Skeleton

### Tasks
- [ ] Create mono-repo structure:
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
- [ ] Set up GitHub Actions pipeline: build → test → deploy (ACA)
- [ ] Configure Azure Container Registry (ACR)
- [ ] Set up development environment documentation

## Phase 1 (Week 1): Public MVP "Truth Hub"

**Goal:** Rankings + server pages + daily brief, driven by manual seed + Batch 1.

### Day 1-2: Database Setup
- [ ] Create Postgres schema + migrations
- [ ] Set up database connection pooling
- [ ] Create seed data scripts for initial providers/servers
- [ ] Test database migrations

### Day 3-4: Public API
- [ ] Implement `/api/v1/public/mcp/summary` endpoint
- [ ] Implement `/api/v1/public/mcp/recently-updated` endpoint
- [ ] Implement `/api/v1/public/mcp/rankings` endpoint (with filters)
- [ ] Implement `/api/v1/public/mcp/servers/{id}` endpoint
- [ ] Implement `/api/v1/public/mcp/servers/{id}/evidence` endpoint
- [ ] Implement `/api/v1/public/mcp/servers/{id}/drift` endpoint
- [ ] Implement `/api/v1/public/mcp/daily/{date}` endpoint
- [ ] Add methodology versioning headers
- [ ] Add ETag and caching support
- [ ] Add error handling and response envelopes

### Day 5: Public Web UI
- [ ] Implement `/mcp` overview dashboard
- [ ] Implement `/mcp/rankings` rankings page
- [ ] Implement `/mcp/servers/{slug}` server detail page
- [ ] Implement `/mcp/daily/{date}` daily brief page
- [ ] Implement `/mcp/methodology` methodology page
- [ ] Connect UI to API endpoints

### Day 6-7: Feeds + Publisher
- [ ] Create RSS feed renderer (`/mcp/feed.xml`)
- [ ] Create JSON Feed renderer (`/mcp/feed.json`)
- [ ] Implement publisher "staging swap" mechanism
- [ ] Add validation logic for dataset completeness
- [ ] Test end-to-end: seed data → API → UI → feeds

## Phase 2 (Week 2): Automation Pipeline MVP (Daily Refresh)

**Goal:** Daily run that updates scores/deltas and generates briefs.

### Day 1-2: Scout + Curator
- [ ] Build Scout ingestor for Tier 1 sources:
  - Official MCP registry
  - Major directory lists
  - Top 50 servers by traffic
- [ ] Build Curator:
  - Canonical ID generation
  - Name normalization
  - Dedupe heuristics
  - Review queue for low-confidence matches
- [ ] Test with sample sources

### Day 3: Evidence Miner
- [ ] Build Evidence Miner for doc/repo extraction:
  - Auth model extraction
  - Tool agency detection
  - Basic claim extraction (15 claim types)
- [ ] Implement parser framework
- [ ] Test with sample docs/repos

### Day 4: Scorer
- [ ] Implement Trust Score v1 calculation:
  - Domain subscores (D1-D6)
  - Weighted Trust Score (0-100)
  - Tier assignment (A/B/C/D)
  - Evidence Confidence calculation (0-3)
  - Fail-fast flag detection
  - Risk flag detection
- [ ] Implement explainability payload generation
- [ ] Test scoring with sample servers

### Day 5: Drift Sentinel
- [ ] Build Drift Sentinel:
  - Diff score snapshots
  - Detect flag changes
  - Detect evidence changes
  - Classify severity (Critical/High/Medium/Low)
  - Generate drift events
- [ ] Test drift detection

### Day 6: Daily Brief Generator
- [ ] Build Daily Brief generator:
  - Calculate top movers (using calculation rules)
  - Calculate top downgrades
  - Identify new entrants
  - Select notable drift events
  - Generate tip of the day
- [ ] Integrate Sage Meridian prompts (or use templates initially)
- [ ] Store daily brief in database

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
- [ ] Set up Entra ID app registration
- [ ] Implement OIDC JWT validation middleware
- [ ] Implement RBAC roles:
  - RegistryAdmin
  - PolicyApprover
  - EvidenceValidator
  - Viewer
  - AutomationOperator
- [ ] Add workspace isolation middleware
- [ ] Test authentication flow

### Day 3: Workspace + Membership
- [ ] Implement workspace creation
- [ ] Implement workspace membership management
- [ ] Add role assignment logic
- [ ] Test multi-tenant isolation

### Day 4: Inventory
- [ ] Implement add server to workspace
- [ ] Implement server metadata (owner, purpose, environment)
- [ ] Implement inventory listing
- [ ] Test inventory operations

### Day 5: Policies
- [ ] Implement policy creation (allow/deny/require approval)
- [ ] Implement policy scope (server/tool/category)
- [ ] Implement policy conditions
- [ ] Implement policy expiration
- [ ] Test policy CRUD

### Day 6: Approvals
- [ ] Implement approval workflow
- [ ] Implement approve/deny actions
- [ ] Add approval history tracking
- [ ] Test approval workflow

### Day 7: Evidence Packs + Exports
- [ ] Implement evidence pack upload to blob storage
- [ ] Implement evidence pack metadata storage
- [ ] Implement validation workflow
- [ ] Implement audit pack export (JSON v0)
- [ ] Test evidence and export flows

## Phase 4 (Week 4): GK "Look Behind the Veil" MVP

**Goal:** Graph explorer on server pages.

### Day 1-2: Graph Snapshot Builder
- [ ] Build graph snapshot builder in pipeline:
  - Server → Tools → Scopes → Data Domains → Evidence → Flags
- [ ] Implement node creation (14 node types)
- [ ] Implement edge creation (13 edge types)
- [ ] Store graph JSON in Postgres
- [ ] Test graph generation

### Day 3-4: Graph API + Explorer
- [ ] Implement `/api/v1/public/mcp/servers/{id}/graph` endpoint
- [ ] Build basic interactive graph explorer UI
- [ ] Add node/edge visualization
- [ ] Add evidence linking
- [ ] Test graph explorer

### Day 5-7: Polish + Integration
- [ ] Integrate graph explorer into server detail page
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
- [ ] Add rate limiting
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
