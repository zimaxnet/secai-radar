/**
 * MCP (Model Context Protocol) API Client
 * Based on Step 2: Content Objects + Feed Specs specification
 * 
 * NOTE: This file is maintained for backward compatibility.
 * New code should use the public API client from './public.ts'
 */

import type {
  DailyTrustBrief,
  MCPServerRecord,
  DailyTiersSnapshot,
} from '../types/mcp'
import * as PublicAPI from './public'

// const API = import.meta.env.VITE_API_BASE || '/api' // Unused - using PublicAPI functions

/**
 * Get daily trust brief for a specific date
 * GET /api/v1/public/mcp/daily/{date}
 * 
 * @deprecated Use PublicAPI.getDailyBrief() instead
 */
export async function getDailyBrief(date: string): Promise<DailyTrustBrief | null> {
  const brief = await PublicAPI.getDailyBrief(date)
  if (!brief) return null
  
  // Convert DailyBrief (dataModel) to DailyTrustBrief (mcp)
  return {
    date: brief.date,
    headline: brief.headline,
    narrativeLong: brief.narrativeLong,
    narrativeShort: brief.narrativeShort,
    highlights: brief.highlights || [],
    topMovers: brief.topMovers || [],
    topDowngrades: brief.topDowngrades || [],
    newEntrants: brief.newEntrants || [],
    notableDrift: (brief.notableDrift || []).map((d: any) => ({
      serverId: d.serverId || '',
      serverName: d.serverName || '',
      providerName: d.providerName || '',
      permalink: d.permalink || '',
      eventType: d.eventType || 'DocsChanged',
      summary: d.summary || '',
      detectedAt: d.detectedAt || new Date().toISOString(),
    })),
    tipOfTheDay: brief.tipOfTheDay || '',
    methodologyVersion: brief.methodologyVersion || 'v1.0',
    generatedAt: brief.generatedAt || new Date().toISOString(),
    permalink: brief.permalink || `/mcp/daily/${date}`,
  }
}

/**
 * Get MCP server record by ID or slug
 * GET /api/v1/public/mcp/servers/{serverId}
 * 
 * @deprecated Use PublicAPI.getServerDetail() instead
 */
export async function getMCPServer(serverIdOrSlug: string): Promise<MCPServerRecord | null> {
  const detail = await PublicAPI.getServerDetail(serverIdOrSlug)
  if (!detail) return null
  
  // Convert ServerDetailResponse to MCPServerRecord format
  return {
    serverId: detail.server.serverId,
    serverSlug: detail.server.serverSlug,
    serverName: detail.server.serverName,
    providerId: detail.server.provider.providerId,
    providerSlug: detail.server.provider.primaryDomain.split('.')[0],
    providerName: detail.server.provider.providerName,
    category: detail.server.categoryPrimary,
    tags: detail.server.tags,
    deploymentType: detail.server.deploymentType,
    authModel: detail.server.authModel === 'OAuthOIDC' ? 'OAuth/OIDC' : 
               detail.server.authModel === 'APIKey' ? 'API key' : 
               detail.server.authModel,
    toolAgency: detail.server.toolAgency,
    trustScore: detail.latestScore.trustScore,
    tier: detail.latestScore.tier,
    evidenceConfidence: detail.latestScore.evidenceConfidence,
    evidenceConfidenceLabel: `${detail.latestScore.evidenceConfidence}/3`,
    failFastFlags: detail.latestScore.failFastFlags,
    riskFlags: detail.latestScore.riskFlags,
    lastAssessedAt: detail.latestScore.assessedAt,
    lastVerifiedAt: detail.latestScore.evidenceConfidence >= 2 ? detail.latestScore.assessedAt : null,
    scoreDelta24h: 0, // Would need to calculate from history
    scoreDelta7d: 0, // Would need to calculate from history
    driftEvents7d: 0, // Would need to fetch separately
    publicEvidenceLinks: [], // Would need to fetch separately
  }
}

/**
 * Get MCP rankings with filters
 * GET /api/v1/public/mcp/rankings?filters=...&sort=trustScore&window=7d&page=1
 * 
 * @deprecated Use PublicAPI.getRankings() instead
 */
export async function getMCPRankings(params: {
  filters?: string
  sort?: 'trustScore' | 'evidenceConfidence' | 'scoreDelta24h'
  window?: '24h' | '7d' | '30d'
  page?: number
}): Promise<{ data: MCPServerRecord[]; total: number }> {
  const result = await PublicAPI.getRankings({
    sort: params.sort,
    window: params.window,
    page: params.page,
  })
  
  // Convert RankingItem[] to MCPServerRecord[] format
  const data: MCPServerRecord[] = result.items.map(item => ({
    serverId: item.serverId,
    serverSlug: item.serverSlug,
    serverName: item.serverName,
    providerId: '', // Would need provider lookup
    providerSlug: '',
    providerName: item.providerName,
    category: '',
    tags: [],
    deploymentType: 'Unknown',
    authModel: 'Unknown',
    toolAgency: 'Unknown',
    trustScore: item.trustScore,
    tier: item.tier,
    evidenceConfidence: item.evidenceConfidence,
    evidenceConfidenceLabel: `${item.evidenceConfidence}/3`,
    failFastFlags: item.flags.filter(f => f.startsWith('fail-fast:')),
    riskFlags: item.flags.filter(f => !f.startsWith('fail-fast:')),
    lastAssessedAt: item.lastAssessedAt,
    lastVerifiedAt: item.evidenceConfidence >= 2 ? item.lastAssessedAt : null,
    scoreDelta24h: item.scoreDelta24h,
    scoreDelta7d: 0,
    driftEvents7d: 0,
    publicEvidenceLinks: [],
  }))
  
  return { data, total: result.total }
}

/**
 * Get MCP summary for a time window
 * GET /api/v1/public/mcp/summary?window=24h
 * 
 * @deprecated Use PublicAPI.getSummary() instead
 */
export async function getMCPSummary(window: '24h' | '7d' | '30d' = '24h'): Promise<{
  brief: DailyTrustBrief | null
  snapshot: DailyTiersSnapshot
} | null> {
  const summary = await PublicAPI.getSummary(window)
  if (!summary) return null
  
  // Convert SummaryResponse to expected format
  return {
    brief: null, // Would need to fetch separately
    snapshot: {
      totalServersTracked: summary.serversTracked,
      tierDistribution: {
        a: summary.tierCounts.A,
        b: summary.tierCounts.B,
        c: summary.tierCounts.C,
        d: summary.tierCounts.D,
      },
      evidenceConfidenceDistribution: summary.evidenceConfidenceCounts,
      failFastFlaggedServers: summary.failFastCount,
      date: new Date().toISOString().split('T')[0],
    },
  }
}

/**
 * Get recently updated servers
 * GET /api/v1/public/mcp/recently-updated?limit=50
 * 
 * @deprecated Use PublicAPI.getRecentlyUpdated() instead
 */
export async function getRecentlyUpdated(limit: number = 50): Promise<MCPServerRecord[]> {
  const items = await PublicAPI.getRecentlyUpdated(limit)
  
  // Convert RecentlyUpdatedItem[] to MCPServerRecord[] format
  return items.map(item => ({
    serverId: item.serverId,
    serverSlug: item.serverSlug,
    serverName: item.serverName,
    providerId: '',
    providerSlug: '',
    providerName: item.providerName,
    category: item.categoryPrimary,
    tags: [],
    deploymentType: 'Unknown',
    authModel: 'Unknown',
    toolAgency: 'Unknown',
    trustScore: item.trustScore,
    tier: item.tier,
    evidenceConfidence: item.evidenceConfidence,
    evidenceConfidenceLabel: `${item.evidenceConfidence}/3`,
    failFastFlags: item.flags.filter(f => f.startsWith('fail-fast:')),
    riskFlags: item.flags.filter(f => !f.startsWith('fail-fast:')),
    lastAssessedAt: item.lastAssessedAt,
    lastVerifiedAt: item.evidenceConfidence >= 2 ? item.lastAssessedAt : null,
    scoreDelta24h: item.scoreDelta24h,
    scoreDelta7d: 0,
    driftEvents7d: item.driftEvents7d,
    publicEvidenceLinks: [],
  }))
}

/**
 * Get flag trends
 * GET /api/v1/public/mcp/flag-trends?window=30d
 * 
 * @deprecated This endpoint is not yet in the Step 4 spec, keeping for backward compatibility
 */
export async function getFlagTrends(window: '7d' | '30d' = '30d'): Promise<Array<{
  name: string
  count: number
  trend: 'up' | 'down' | 'stable'
}>> {
  // TODO: Implement when endpoint is available
  // Suppress unused window parameter warning
  void window
  return []
}

/**
 * Get server drift events
 * GET /api/v1/public/mcp/servers/{serverId}/drift?window=90d
 * 
 * @deprecated Use PublicAPI.getServerDrift() instead
 */
export async function getServerDrift(
  serverId: string,
  window: '7d' | '30d' | '90d' = '90d'
): Promise<any[]> {
  const response = await PublicAPI.getServerDrift(serverId, window)
  return response?.items || []
}

/**
 * Get server evidence
 * GET /api/v1/public/mcp/servers/{serverId}/evidence
 * 
 * @deprecated Use PublicAPI.getServerEvidence() instead
 */
export async function getServerEvidence(serverId: string): Promise<any[]> {
  const response = await PublicAPI.getServerEvidence(serverId)
  if (!response) return []
  
  return [
    ...response.evidence,
    ...response.claims,
  ]
}
