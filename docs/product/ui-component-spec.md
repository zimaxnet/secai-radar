# SecAI Radar Verified MCP - UI Component Specification

**Based on:** Step 6 MVP PRD + UI Component Spec  
**Version:** v0.1

## Global UI System

### Header
- **Logo:** "SecAI Radar — Verified MCP"
- **Navigation:**
  - Overview
  - Rankings
  - Daily Brief
  - Methodology
- **CTA:** Submit Evidence
- **Search:** Server/provider search
- **Filter chip:** Updated in 24h/7d/30d

### Footer
- Zimax Networks LC link (zimax.net)
- ctxeco product link (ctxeco.com/mcp)
- openContextGraph (MIT) link
- Disclaimers + contact + press

## Page Specifications

### 2.2 /mcp (Overview Dashboard)

#### Modules + Components

1. **Daily Brief Hero**
   - Title + date
   - 3 highlight bullets
   - CTA: "Read today's brief"

2. **KPI Strip**
   - Servers tracked
   - Providers tracked
   - Tier distribution (A/B/C/D)
   - Evidence confidence distribution (0–3)

3. **Top Movers / Downgrades / New Entrants**
   - 3 columns layout
   - Each row: server + provider + delta + badge + link

4. **Risk Flags Trending**
   - Tile grid (sparkline optional)
   - Click tile → rankings filtered

5. **Recently Updated Table**
   - Sortable columns
   - Server | Provider | Trust Score | Evidence Confidence | Last Verified | Drift Count (7d)

#### Empty States
- If daily run failed: show "Data last updated" banner and link to status page

### 2.3 /mcp/rankings (Rankings Dashboard)

#### Core Components
- **Facet rail:** Official/Remote/Auth/ToolAgency/EvidenceConfidence/Flags
- **Results table:**
  - rank, server, provider, trust score, tier, evidence confidence, delta, last assessed
- **Compare tray** (v1 optional): select up to 3

#### Key UI Behaviors
- Filters update URL query string (shareable)
- Hover on flags shows tooltip definitions
- Clicking evidence confidence badge opens a popover explaining levels

### 2.4 /mcp/servers/{serverSlug} (Server Detail)

#### Hero
- Server + Provider
- Trust Score + Tier badge
- Evidence Confidence badge
- Last assessed timestamp
- Enterprise fit badge

#### Tabs

**Overview**
- Domain breakdown chart (D1–D6)
- Fail-fast checklist
- "Recommended mitigations" card

**Evidence**
- Evidence table (link, type, confidence, capturedAt)
- Claims panel (Auth model, hosting custody, retention, audit)
- "Evidence gaps" callout

**Drift**
- Timeline list with severity badges
- "What changed since yesterday?" summary
- Link to diff details (v1)

**Graph**
- Graph snapshot viewer (MVP)
- Click node → evidence + last verified (v1 richer)

**Provider response**
- Submission status: none/submitted/verified
- Right-to-respond text + link to submit evidence

### 2.5 /mcp/daily/YYYY-MM-DD (Daily Brief)
- Headline + narrative
- Movers/downgrades/new entrants (lists)
- Notable drift
- Tip of the day
- Methodology version + disclaimers

### 2.6 /mcp/methodology
- What Trust Score is (risk posture assessment)
- Domain definitions D1–D6
- Evidence Confidence definition 0–3
- Rubric changelog links
- "How to submit evidence packs" guide

### 2.7 /mcp/submit (Submit Evidence)
- Choose: Provider or Customer
- Provider submission:
  - contact email
  - server URL/repo
  - evidence links
  - optional upload → routes to private workflow (may require account)
- Acknowledge: "not a certification"; "we may publish a response status"

## Component Library

### Badges
- TierBadge (A/B/C/D)
- EvidenceConfidenceBadge (0-3)
- EnterpriseFitBadge (Regulated/Standard/Experimental)
- FlagBadge (with tooltip)

### Cards
- ServerCard
- ProviderCard
- DailyBriefCard
- MoverCard
- DowngradeCard
- DriftEventCard

### Tables
- RankingsTable
- RecentlyUpdatedTable
- EvidenceTable
- DriftTimelineTable

### Charts
- DomainBreakdownChart (D1-D6)
- TierDistributionChart
- EvidenceConfidenceChart
- RiskFlagsChart

### Forms
- SearchForm
- FilterForm
- EvidenceSubmissionForm

### Modals/Dialogs
- EvidenceConfidenceModal
- FlagDefinitionModal
- CompareServersModal (v1)
