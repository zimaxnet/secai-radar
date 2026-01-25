/**
 * TypeScript types for automation pipeline and agent roles
 * Based on Step 3: Automation Blueprint specification
 */

// ============================================================================
// Agent Roles
// ============================================================================

export interface ScoutOutput {
  runId: string
  timestamp: string
  sourceRecords: RawSourceRecord[]
  metadata: {
    sourcesChecked: string[]
    totalRecords: number
    parserVersion: string
  }
}

export interface RawSourceRecord {
  sourceName: string
  sourceUrl: string
  retrievedAt: string
  rawContent: string
  rawContentHash: string
  parserVersion: string
  extractedFields: {
    name?: string
    repoUrl?: string
    endpointUrl?: string
    provider?: string
    description?: string
    [key: string]: any
  }
}

export interface CuratorOutput {
  runId: string
  timestamp: string
  canonicalProviders: CanonicalProvider[]
  canonicalServers: CanonicalServer[]
  canonicalEndpoints: CanonicalEndpoint[]
  dedupeResults: DedupeResult[]
}

export interface CanonicalProvider {
  providerId: string // hash(legalName + primaryDomain)
  legalName: string
  primaryDomain: string
  aliases: string[]
  createdAt: string
  updatedAt: string
}

export interface CanonicalServer {
  serverId: string // hash(providerId + primaryIdentifier)
  providerId: string
  primaryIdentifier: string // repo URL, endpoint domain, or product page URL
  normalizedName: string
  aliases: string[]
  deploymentType: 'Remote' | 'Local' | 'Hybrid' | 'Unknown'
  categories: string[]
  tags: string[]
  createdAt: string
  updatedAt: string
}

export interface CanonicalEndpoint {
  endpointId: string
  serverId: string
  normalizedUrl: string
  scheme: string
  host: string
  path: string
  aliases: string[]
  createdAt: string
  updatedAt: string
}

export interface DedupeResult {
  type: 'provider' | 'server' | 'endpoint'
  canonicalId: string
  mergedIds: string[]
  confidence: number // 0-1
  requiresReview: boolean
}

export interface EvidenceMinerOutput {
  runId: string
  timestamp: string
  evidenceItems: EvidenceItem[]
  extractedClaims: ExtractedClaim[]
}

export interface EvidenceItem {
  evidenceId: string
  serverId: string
  type: 'docs' | 'repo' | 'report' | 'config' | 'logs'
  url?: string // public
  blobRef?: string // private
  capturedAt: string
  confidence: 1 | 2 | 3
  hash: string // content hash for drift detection
  sourceUrl: string
  parserVersion: string
}

export interface ExtractedClaim {
  claimId: string
  evidenceId: string
  claimType: 'authModel' | 'tokenTTL' | 'hostingPosture' | 'toolAgency' | 'auditStatement' | 'dataHandling' | 'securityPosture'
  value: string
  confidence: 1 | 2 | 3
  citation: string // quote snippet or URL reference
  extractedAt: string
}

export interface ScorerOutput {
  runId: string
  timestamp: string
  scores: ServerScore[]
  methodologyVersion: string
}

export interface ServerScore {
  serverId: string
  assessedAt: string
  domainScores: {
    d1: number // Authentication (0-5)
    d2: number // Authorization (0-5)
    d3: number // Data Protection (0-5)
    d4: number // Audit & Logging (0-5)
    d5: number // Operational Security (0-5)
    d6: number // Compliance (0-5)
  }
  trustScore: number // 0-100 (weighted)
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number // 0-3
  enterpriseFit: 'Regulated' | 'Standard' | 'Experimental'
  failFastFlags: string[]
  riskFlags: string[]
  explanation: {
    topFactorsIncreasing: Array<{ factor: string; evidenceLink: string }>
    topGapsLowering: Array<{ gap: string; evidenceLink: string | null }>
    recommendedMitigations: string[]
  }
}

export interface DriftSentinelOutput {
  runId: string
  timestamp: string
  driftEvents: DriftEvent[]
  scoreDeltas: Array<{
    serverId: string
    scoreDelta: number
    tierChange?: { old: string; new: string }
  }>
  flagDeltas: Array<{
    serverId: string
    flagsAdded: string[]
    flagsRemoved: string[]
  }>
  notableDrift: DriftEvent[] // Selected for Daily Brief
}

export interface DriftEvent {
  eventId: string
  serverId: string
  eventType: 'ToolsAdded' | 'ToolsRemoved' | 'AuthChanged' | 'ScopeChanged' | 'EndpointChanged' | 'DocsChanged' | 'EvidenceAdded' | 'EvidenceRemoved' | 'ScoreChanged' | 'FlagChanged'
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
  summary: string
  detectedAt: string
  previousValue?: any
  newValue?: any
  evidenceLink?: string
}

export interface PublisherOutput {
  runId: string
  timestamp: string
  publishedArtifacts: {
    rankings: boolean
    pages: boolean
    dailyBrief: boolean
    rssFeed: boolean
    jsonFeed: boolean
  }
  stagingSwapCompleted: boolean
}

export interface SageMeridianOutput {
  runId: string
  timestamp: string
  dailyBrief: {
    date: string
    headline: string
    narrativeLong: string
    narrativeShort: string
    highlights: string[]
    tipOfTheDay: string
  }
  socialVariants: {
    xThread: string[]
    linkedInPost: string
    redditPost: string
    hnPost?: string
  }
  visualPrompts: {
    dailyCard: string
    moverCard?: string
    downgradeCard?: string
    driftCard?: string
  }
}

export interface OutboxItem {
  outboxId: string
  channel: 'x' | 'linkedin' | 'reddit' | 'hn' | 'mastodon' | 'bluesky'
  content: string
  media?: string[] // image URLs
  links: string[]
  policy: {
    rateLimit: number
    cadence: 'daily' | 'weekly' | 'major-events-only'
  }
  status: 'queued' | 'sent' | 'failed'
  createdAt: string
  sentAt?: string
  errorMessage?: string
}

// ============================================================================
// Pipeline Run
// ============================================================================

export interface PipelineRun {
  runId: string // YYYY-MM-DD + source version hashes
  date: string // YYYY-MM-DD
  startedAt: string
  completedAt?: string
  status: 'running' | 'completed' | 'failed' | 'partial'
  stages: PipelineStage[]
  deliverables: {
    rankingsUpdated: boolean
    driftEventsComputed: boolean
    dailyBriefGenerated: boolean
    feedItemsPublished: boolean
    outboxCreated: boolean
  }
  errors?: string[]
}

export interface PipelineStage {
  stageName: 'scout' | 'curator' | 'evidenceMiner' | 'scorer' | 'driftSentinel' | 'publisher' | 'sageMeridian'
  startedAt: string
  completedAt?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  output?: any
  error?: string
}

// ============================================================================
// Source Connectors
// ============================================================================

export interface SourceConnector {
  sourceName: string
  tier: 1 | 2 // Tier 1 = daily, Tier 2 = rotating
  enabled: boolean
  lastRunAt?: string
  nextRunAt?: string
  config: {
    url: string
    parserVersion: string
    rateLimit?: number
    respectRobotsTxt?: boolean
  }
}

// ============================================================================
// Guardrails
// ============================================================================

export interface GuardrailCheck {
  checkId: string
  type: 'accuracy' | 'fairness' | 'security' | 'human-review'
  status: 'pass' | 'fail' | 'warning'
  message: string
  timestamp: string
}

export interface HumanReviewQueue {
  reviewId: string
  type: 'provider-merge' | 'critical-downgrade' | 'vendor-dispute'
  entityId: string
  entityType: 'provider' | 'server'
  reason: string
  confidence: number
  createdAt: string
  reviewedAt?: string
  reviewedBy?: string
  decision?: 'approved' | 'rejected' | 'deferred'
}
