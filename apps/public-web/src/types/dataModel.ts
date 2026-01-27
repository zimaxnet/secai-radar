/**
 * Canonical Data Model Types
 * Based on Step 4: Data Model + API Spec specification
 */

// ============================================================================
// 1.1 Core Entities
// ============================================================================

export interface Provider {
  providerId: string // stable hash
  providerName: string
  primaryDomain: string
  providerType: 'Vendor' | 'Community' | 'Directory' | 'Official'
  contactUrl?: string
  createdAt: string
  updatedAt: string
}

export interface MCPServer {
  serverId: string // stable hash
  serverSlug: string
  serverName: string
  providerId: string
  categoryPrimary: string
  tags: string[]
  deploymentType: 'Remote' | 'Local' | 'Hybrid' | 'Unknown'
  authModel: 'OAuthOIDC' | 'APIKey' | 'PAT' | 'mTLS' | 'Unknown'
  toolAgency: 'ReadOnly' | 'ReadWrite' | 'DestructivePresent' | 'Unknown'
  endpoints: string[] // hostnames + urls
  repoUrl?: string
  docsUrl?: string
  status: 'Active' | 'Deprecated' | 'Unknown'
  firstSeenAt: string
  lastSeenAt: string
}

export interface EvidenceItem {
  evidenceId: string
  serverId: string
  type: 'Docs' | 'Repo' | 'Report' | 'Config' | 'Logs' | 'Attestation'
  url?: string // public
  blobRef?: string // private
  capturedAt: string
  confidence: 1 | 2 | 3 // 0 is "unknown" at server level; evidence items start at 1
  contentHash: string
  extracts: ExtractedClaim[]
}

export interface ScoreSnapshot {
  scoreId: string
  serverId: string
  methodologyVersion: string
  assessedAt: string
  // Domain subscores (0-5)
  d1: number // Authentication
  d2: number // Authorization
  d3: number // Data Protection
  d4: number // Audit & Logging
  d5: number // Operational Security
  d6: number // Compliance
  trustScore: number // 0-100
  tier: 'A' | 'B' | 'C' | 'D'
  enterpriseFit: 'Regulated' | 'Standard' | 'Experimental'
  evidenceConfidence: 0 | 1 | 2 | 3
  failFastFlags: string[]
  riskFlags: string[]
  explainability: ExplainabilityPayload
}

export interface DriftEvent {
  driftId: string
  serverId: string
  detectedAt: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
  eventType: 'ToolsAdded' | 'ToolsRemoved' | 'AuthChanged' | 'ScopeChanged' | 'EndpointChanged' | 'DocsChanged' | 'EvidenceAdded' | 'EvidenceRemoved' | 'FlagChanged' | 'ScoreChanged'
  summary: string
  diffRef?: string // pointer to structured diff payload
}

export interface DailyBrief {
  date: string // YYYY-MM-DD
  headline: string
  narrativeLong: string
  narrativeShort: string
  highlights: string[]
  topMovers: MoverObject[]
  topDowngrades: DowngradeObject[]
  newEntrants: NewEntrantObject[]
  notableDrift: DriftEvent[]
  tipOfTheDay: string
  methodologyVersion: string
  generatedAt: string
  permalink: string
}

// Re-export from mcp.ts for consistency
export interface MoverObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  scoreDelta: number
  reasonCodes: string[]
  flagChanges: {
    added: string[]
    removed: string[]
  }
  evidenceConfidenceDelta: number
}

export interface DowngradeObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  scoreDelta: number
  reasonCodes: string[]
  flagChanges: {
    added: string[]
    removed: string[]
  }
  evidenceConfidenceDelta: number
}

export interface NewEntrantObject {
  serverId: string
  serverName: string
  providerName: string
  permalink: string
  authModel: string
  deploymentType: string
  evidenceConfidence: number
  trustScore: number
  firstObservedAt: string
}

// ============================================================================
// 1.2 Extracted Claims Schema
// ============================================================================

export type ClaimType =
  | 'AuthModel'
  | 'TokenTTL'
  | 'Scopes'
  | 'HostingCustody'
  | 'ToolList'
  | 'ToolCapabilities'
  | 'AuditLogging'
  | 'DataRetention'
  | 'DataDeletion'
  | 'Residency'
  | 'Encryption'
  | 'SBOM'
  | 'Signing'
  | 'VulnDisclosure'
  | 'IRPolicy'

export interface ExtractedClaim {
  claimType: ClaimType
  value: string | number | object
  confidence: 1 | 2 | 3
  sourceEvidenceId: string
  sourceUrl: string
  capturedAt: string
}

// ============================================================================
// 1.3 Explainability Payload
// ============================================================================

export interface ExplainabilityPayload {
  positiveFactors: Array<{
    factorCode: string
    summary: string
    evidenceLinks: string[]
  }>
  negativeFactors: Array<{
    factorCode: string
    summary: string
    evidenceLinks: (string | null)[]
  }>
  recommendedMitigations: string[]
}

// ============================================================================
// Public API Response Types
// ============================================================================

export interface PublicAPIResponse<T> {
  methodologyVersion: string
  generatedAt: string
  data: T
  meta?: {
    requestId: string
    page?: number
    pageSize?: number
    total?: number
  }
  error?: {
    code: string
    message: string
    details?: any
  }
}

export interface SummaryResponse {
  serversTracked: number
  providersTracked: number
  tierCounts: {
    A: number
    B: number
    C: number
    D: number
  }
  evidenceConfidenceCounts: {
    '0': number
    '1': number
    '2': number
    '3': number
  }
  failFastCount: number
  topMovers: Array<{
    serverId: string
    serverName: string
    providerName: string
    scoreDelta: number
    permalink: string
  }>
  topDowngrades: Array<{
    serverId: string
    serverName: string
    providerName: string
    scoreDelta: number
    permalink: string
  }>
  newEntrants: Array<{
    serverId: string
    serverName: string
    providerName: string
    permalink: string
  }>
  notableDrift: Array<{
    serverId: string
    eventType: string
    severity: string
    summary: string
  }>
}

export interface RecentlyUpdatedItem {
  serverId: string
  serverSlug: string
  serverName: string
  providerName: string
  categoryPrimary: string
  trustScore: number
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number
  lastAssessedAt: string
  scoreDelta24h: number
  driftEvents7d: number
  flags: string[]
}

export interface RankingItem {
  rank: number
  serverId: string
  serverSlug: string
  serverName: string
  providerName: string
  trustScore: number
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number
  scoreDelta24h: number
  lastAssessedAt: string
  flags: string[]
}

export interface ServerDetailResponse {
  server: MCPServer & {
    provider: {
      providerId: string
      providerName: string
      primaryDomain: string
    }
  }
  latestScore: ScoreSnapshot
}

export interface ServerEvidenceResponse {
  evidence: Array<{
    evidenceId: string
    type: string
    url?: string
    capturedAt: string
    confidence: number
  }>
  claims: ExtractedClaim[]
}

export interface ServerDriftResponse {
  items: DriftEvent[]
}

export interface GraphNode {
  id: string
  type: string
  label: string
  props: Record<string, any>
}

export interface GraphEdge {
  from: string
  to: string
  type: string
}

export interface ServerGraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface ProviderPortfolioResponse {
  provider: Provider
  servers: Array<{
    serverId: string
    serverSlug: string
    serverName: string
    trustScore: number
    tier: string
    scoreDelta24h: number
    flags: string[]
  }>
}

export interface ServerStory {
  serverId: string
  serverSlug: string
  serverName: string
  providerName: string
  title: string
  narrative: string
  highlights: string[]
  benefits: string[]
  researchPoints: string[]
  trustScore: number
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number
  featuredAt: string
}
