/**
 * TypeScript types for MCP (Model Context Protocol) content objects
 * Based on Step 2: Content Objects + Feed Specs specification
 */

// ============================================================================
// 1.1 MCP Server Record (public view)
// ============================================================================
export interface MCPServerRecord {
  serverId: string
  serverSlug: string
  serverName: string
  providerId: string
  providerSlug: string
  providerName: string
  category: string
  tags: string[]
  deploymentType: 'Remote' | 'Local' | 'Hybrid' | 'Unknown'
  authModel: 'OAuth/OIDC' | 'API key' | 'PAT' | 'mTLS' | 'Unknown'
  toolAgency: 'ReadOnly' | 'ReadWrite' | 'DestructivePresent' | 'Unknown'
  trustScore: number // 0-100
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number // 0-3
  evidenceConfidenceLabel: string
  failFastFlags: string[]
  riskFlags: string[]
  lastAssessedAt: string // ISO timestamp
  lastVerifiedAt: string | null // ISO timestamp (null if evidence confidence < 2)
  scoreDelta24h: number
  scoreDelta7d: number
  driftEvents7d: number
  publicEvidenceLinks: Array<{
    url: string
    type: 'docs' | 'repo' | 'report' | 'config'
    date: string
  }>
}

// ============================================================================
// 1.2 Daily Trust Brief
// ============================================================================
export interface DailyTrustBrief {
  date: string // YYYY-MM-DD
  headline: string
  narrativeLong: string // Sage Meridian generated
  narrativeShort: string // <= 600 chars
  highlights: string[]
  topMovers: MoverObject[]
  topDowngrades: DowngradeObject[]
  newEntrants: NewEntrantObject[]
  notableDrift: DriftEventObject[]
  tipOfTheDay: string
  methodologyVersion: string
  generatedAt: string // ISO timestamp
  permalink: string
}

// ============================================================================
// 1.3 Mover Object
// ============================================================================
export interface MoverObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  scoreDelta: number // positive
  reasonCodes: string[] // e.g., 'EvidenceAdded', 'AuthClarified', 'ToolListDiffResolved'
  flagChanges: {
    added: string[]
    removed: string[]
  }
  evidenceConfidenceDelta: number // positive
}

// ============================================================================
// 1.4 Downgrade Object
// ============================================================================
export interface DowngradeObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  scoreDelta: number // negative
  reasonCodes: string[] // e.g., 'NewFailFastFlag', 'EvidenceRemoved', 'ToolScopeExpanded'
  flagChanges: {
    added: string[]
    removed: string[]
  }
  evidenceConfidenceDelta: number // negative or 0
}

// ============================================================================
// 1.5 Drift Event Object
// ============================================================================
export interface DriftEventObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  eventType: 'ToolsAdded' | 'ToolsRemoved' | 'AuthChanged' | 'ScopeChanged' | 'EndpointChanged' | 'DocsChanged'
  summary: string
  detectedAt: string // ISO timestamp
}

// ============================================================================
// 1.6 New Entrant Object
// ============================================================================
export interface NewEntrantObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  authModel: string
  deploymentType: string
  evidenceConfidence: number
  trustScore: number
  firstObservedAt: string // ISO timestamp
}

// ============================================================================
// 1.7 Scorecard Update Object
// ============================================================================
export interface ScorecardUpdateObject {
  serverId: string
  providerName: string
  serverName: string
  permalink: string
  trustScoreOld: number
  trustScoreNew: number
  tierOld: 'A' | 'B' | 'C' | 'D'
  tierNew: 'A' | 'B' | 'C' | 'D'
  evidenceConfidenceOld: number
  evidenceConfidenceNew: number
  flagsOld: string[]
  flagsNew: string[]
  changeSummary: string
  effectiveDate: string // ISO timestamp
}

// ============================================================================
// Feed Types
// ============================================================================

// RSS/Atom Feed Item
export interface RSSFeedItem {
  title: string
  link: string
  pubDate: string
  guid: string
  description: string
  categories: string[]
  contentEncoded?: string
  mediaImageUrl?: string
}

// JSON Feed Item (JSON Feed v1)
export interface JSONFeedItem {
  id: string
  url: string
  title: string
  content_text: string
  content_html?: string
  date_published: string
  tags: string[]
  attachments?: Array<{
    url: string
    mime_type: string
    title?: string
  }>
  author?: string
}

export interface JSONFeed {
  version: string
  title: string
  description?: string
  home_page_url: string
  feed_url: string
  items: JSONFeedItem[]
}

// ============================================================================
// Daily Tiers Snapshot
// ============================================================================
export interface DailyTiersSnapshot {
  totalServersTracked: number
  tierDistribution: {
    a: number
    b: number
    c: number
    d: number
  }
  evidenceConfidenceDistribution: {
    '0': number
    '1': number
    '2': number
    '3': number
  }
  failFastFlaggedServers: number
  date: string // YYYY-MM-DD
}
