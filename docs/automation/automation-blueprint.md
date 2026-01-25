# SecAI Radar — Verified MCP Automation Blueprint

**Version:** v0.1  
**Date:** 2026-01-23  
**Timezone:** America/Phoenix  
**Reference:** Step 3 Automation Blueprint Document

## Overview

This document defines the end-to-end automation that powers daily refresh, re-ranking, drift detection, and media syndication for **secairadar.cloud/mcp**, backed by SecAI Radar Trust Registry and ctxeco.

## System Architecture

### Components

**Public Layer (secairadar.cloud)**
- Verified MCP dashboards (rankings, server pages, provider pages, daily briefs)
- Public API (read-only)
- RSS/JSON feeds

**Private Layer (app.secairadar.cloud)**
- Org Trust Registry workspaces (inventory, approvals, policies, evidence uploads)
- Audit pack exports (PDF/JSON)

**Content Engine**
- "Daily Trust Brief" generator (Sage Meridian — storyteller)
- Visual asset generator (cards: daily/mover/downgrade/drift)

**Data Layer (GK-first)**
- Graph store: openContextGraph model for entities/relationships
- Relational store: snapshots + scoring history + daily brief objects
- Object storage: evidence artifacts (public links + private uploads)
- Search index: fast lookup for dashboards (servers/providers/tags)

## Agent Roles and Responsibilities

### A) Scout (Discovery Ingestor)

**Goal:** Find MCP servers/providers daily from multiple lists + registries.

**Outputs:** Raw source records + source metadata.

**Sources:**
- Official registry "recently updated"
- Directory catalogs (official/remote)
- GitHub awesome lists / curated repos
- Marketplace listings when relevant
- Vendor docs/repo updates (top providers + top movers)

**Hard Requirements:**
- Capture the source URL(s) and timestamps for every record
- Never overwrite; always append raw observations

### B) Curator (Normalizer + Canonicalizer)

**Goal:** Convert raw records into canonical entities and resolve duplicates.

**Outputs:** Canonical Provider + Server + Endpoint records with stable IDs.

**Functions:**
- Normalize names ("Notion MCP", "notion-mcp-server" → same)
- Normalize endpoints (strip tracking params, normalize scheme/host)
- Normalize repos (canonical GitHub URL)
- Assign deployment type (Remote/Local/Hybrid/Unknown)
- Assign provisional categories/tags

### C) Evidence Miner (Docs/Repo Extractor)

**Goal:** Extract structured posture signals from docs and repos.

**Outputs:** Evidence items + extracted "claims" (with citations).

**Extracts (minimum):**
- Auth model (OAuth/OIDC/API key/PAT/mTLS/unknown)
- Token TTL/scopes (if stated)
- Hosting posture (who operates endpoint; proxy/relay notes)
- Tool agency posture (read-only vs write vs destructive)
- Audit/logging statements (if stated)
- Data handling: retention/deletion/residency (if stated)
- Security posture: SBOM, signing, vuln disclosure, IR policy (if stated)

**Important:** Evidence must always be linked to a URL artifact; claims without source remain "Unknown".

### D) Scorer (Trust Score v1 Evaluator)

**Goal:** Compute Trust Score + Evidence Confidence for each server daily.

**Inputs:** Canonical server record + evidence claims + provider evidence packs.

**Outputs:** Domain subscores (D1–D6), Trust Score, Tier, flags, enterprise fit.

**Rules:**
- Trust Score computed using v1 rubric weights and domain controls
- Evidence Confidence computed independently (0–3)
- Apply **fail-fast rules** to enterprise fit (Experimental if triggered)
- Store an explanation payload ("why it scored this way")

### E) Drift Sentinel (Diff + Change Classifier)

**Goal:** Detect meaningful changes since last run and classify severity.

**Outputs:** Drift events, score deltas, flag deltas, "notable drift" candidates.

**Compares:**
- Tool list / capability labels (added/removed)
- Auth model/scopes/TTL claims changed
- Endpoint/domain changes
- Docs hash diff (content changed)
- Evidence list changes (added/removed)
- Score changes and tier changes
- Fail-fast flag changes

**Severity:**
- **Critical:** new fail-fast; auth downgrade; scope expansion; endpoint custody change
- **High:** destructive tools introduced; audit claims removed; retention unclear emerges
- **Medium:** tooling changes; docs changed with security implications
- **Low:** cosmetic docs edits; metadata updates

### F) Publisher (Dashboards + Feeds + API)

**Goal:** Publish updated rankings, pages, and feeds atomically.

**Outputs:** Updated public API dataset + rendered pages + RSS/JSON feed items.

**Publishing Rules:**
- Never publish partial datasets; use staging → swap
- Stamp every page with:
  - Last assessed (timestamp)
  - Methodology version
  - Evidence Confidence label
  - "Not a certification" disclaimer

### G) Sage Meridian (Storyteller + Visual Director)

**Goal:** Convert daily data into narrative and visuals.

**Outputs:** Daily Brief (short + long), social variants, card prompts.

**Inputs:**
- Top movers/downgrades/new entrants
- Notable drift events
- "Tip of the day" governance message
- Any special alerts (e.g., major downgrade)

**Outputs:**
- Daily Trust Brief page body
- X thread text
- LinkedIn post
- Weekly Reddit post draft (queued; not daily spam)
- HN/Lobsters post draft (major events only)
- Visual asset prompts (daily card, mover, downgrade, drift)

## Daily Pipeline Runbook

### Schedule (Recommended - America/Phoenix timezone)

- **02:30** Scout run (discovery)
- **03:00** Curator run (canonicalize/dedupe)
- **03:20** Evidence Miner run (extract claims)
- **04:00** Scorer run (compute scores)
- **04:20** Drift Sentinel run (diff + classify)
- **04:40** Publisher run (update dashboards + API + feeds)
- **05:00** Sage Meridian run (daily brief + social variants + visual prompts)
- **05:20** Publish media outputs to "outbox" (queued for posting)

> Posting to external platforms is handled by a separate "Distribution" service that uses each platform's API and respects rate limits.

### Idempotency

Each run is keyed by `runId = YYYY-MM-DD` + source version hashes.

Re-runs should:
- Not duplicate canonical entities
- Append new evidence and drift events
- Update "latest snapshot" pointers atomically

### Minimal Deliverables per Run (Success Criteria)

- Rankings updated
- Drift events computed
- Daily brief generated
- Feed items published
- Outbox created (X/LinkedIn/Reddit/HN drafts)

If any of these fail, publish a "stale data" banner and keep yesterday's dataset live.

## Source Connector Plan

### Tier 1 Sources (Always Daily)

- Official MCP registry / "recently updated"
- Major directory list(s) that track remote/official servers
- Your own verified provider submissions / evidence packs
- The "Top 50 by traffic" server pages (to keep popular items fresh)

### Tier 2 Sources (Rotating)

- GitHub awesome lists and curated repos (scan weekly; daily for deltas on top items)
- Vendor docs for top providers (watch RSS/changes where possible)
- Marketplace listings (weekly scan; daily for top movers)

### Source Metadata Stored

For each observation:
- `sourceName`, `sourceUrl`, `retrievedAt`
- `rawContentHash` (for drift detection)
- `parserVersion` (so you can reproduce extraction)

## Canonical Identity + Dedupe Rules

### Canonical IDs

Create stable IDs:
- `providerId = hash(legalName + primaryDomain)`
- `serverId = hash(providerId + primaryIdentifier)`

Where `primaryIdentifier` is chosen by precedence:
1. Official repo URL (canonical)
2. Official hosted endpoint domain
3. Official product page URL
4. If none: (normalized name + top source URL)

### Dedupe Heuristics (in order)

1. Exact match on repo URL
2. Exact match on endpoint host
3. Fuzzy match on normalized names + same provider domain
4. Fuzzy match on repo name + same provider
5. Human review queue when confidence < threshold

### Alias Management

Store aliases:
- Name variants
- Endpoint variants
- Old repos / moved repos

This supports drift tracking and reduces "false new entrants".

## Evidence Model

### Evidence Objects

Each evidence item includes:
- `evidenceId`, `serverId`, `type` (docs/repo/report/config/logs)
- `url` (public) or `blobRef` (private)
- `capturedAt`, `confidence` (1–3)
- `extracts` (structured claims + quote snippets where allowed)
- `hash` (content hash for drift)

### Public vs Private

**Public pages:**
- Show evidence URLs and non-sensitive extracts

**Private workspace:**
- Allows uploading confidential artifacts (SOC2, pen test letters, internal configs)
- Supports evidence validation workflows and higher confidence scoring

## Scoring + Explanation Payload

### Persist Domain Scores

Store:
- D1–D6 subscores (0–5)
- Weighted Trust Score (0–100)
- Tier A/B/C/D
- Enterprise fit flag
- Fail-fast flags and risk flags

### Explainability Payload

For every scored server, store:
- "Top 5 factors increasing score" (with evidence links)
- "Top 5 gaps lowering score" (with evidence links or "unknown")
- "Recommended enterprise mitigations"

This powers "look behind the veil" on the server detail page.

## Drift Detection Details

### What We Diff Daily

- Evidence list changes (added/removed)
- Auth model claim changes
- Endpoint changes
- Tool list changes (if obtainable)
- Docs content hash changes
- Score/tier changes
- Flag changes

### Drift Event Generation

Generate drift events whenever:
- A tracked field changes AND
- The source claim is credible (confidence >= 1) AND
- Change is meaningful (severity threshold)

### "Notable Drift" Selection (for Daily Brief)

Priority ordering:
Endpoint custody/auth changes > scope changes > destructive tool introduction > tool additions > docs edits.

## Publishing Layer and "Outbox" Distribution

### Public Publish Artifacts

- Updated rankings dataset (JSON)
- Updated pages (overview, rankings, server, provider)
- Daily brief permalink page
- RSS feed item
- JSON feed item

### Outbox Objects (for Distribution Service)

Create a durable outbox record:
- `channel` (x, linkedin, reddit, hn, mastodon, bluesky)
- `content` (text + links)
- `media` (image URLs)
- `policy` (rate limits, cadence)
- `status` (queued/sent/failed)

### Posting Cadence Guardrails

- X / LinkedIn: daily
- Reddit: weekly (avoid daily spam)
- HN/Lobsters: major events only
- Always link to the permalink daily brief and/or server pages

## Reliability, Safety, and Governance Guardrails

### Accuracy Guardrails

- Never infer facts not present in evidence
- Distinguish "Unknown" from "Missing" explicitly
- Store extraction confidence and parser version

### Fairness / Defamation Risk Controls

- Use "risk posture assessment" language; never imply certification
- Provide provider "right to respond" and evidence submission workflow
- Show "last assessed" timestamp and evidence confidence prominently
- Maintain a public rubric changelog and re-score notes

### Security Controls for the Pipeline

- Secrets in Key Vault (or equivalent)
- Least-privileged service identities
- Audit logs for pipeline actions
- Content sanitization: do not ingest credentials from docs; redact if detected
- Rate limit scrapers; respect robots.txt where applicable

### Human-in-the-Loop Points (Recommended)

- New provider merges when dedupe confidence is low
- Critical downgrades published as "Alert" (review queue)
- Vendor dispute resolutions (log decisions)

## MVP Implementation Checklist (Ordered)

1. Stand up canonical data model (Provider, Server, Evidence, Score, Drift, DailyBrief)
2. Build Scout + Curator (discovery + canonical IDs)
3. Implement Evidence Miner for Tier 1 sources
4. Implement Scorer (Trust Score v1 + Evidence Confidence)
5. Implement Drift Sentinel (diffs + severity)
6. Implement Publisher (rankings + daily brief + feeds)
7. Connect Sage Meridian prompts (daily narrative + social templates + card prompts)
8. Add outbox + distribution service integration

## "Day 1" Operational Definition of Success

- secairadar.cloud/mcp shows:
  - Updated rankings
  - Daily brief
  - Server detail pages with "why" + evidence + drift
- Feeds update automatically
- Social drafts and visual prompts are produced daily without manual work
