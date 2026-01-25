/**
 * Calculation rules for daily brief generation
 * Based on Step 2: Content Objects + Feed Specs specification
 */

import type { MCPServerRecord, MoverObject, DowngradeObject, NewEntrantObject } from '../types/mcp'

/**
 * Calculate "Top Movers" selection
 * Rules:
 * - Primary sort: scoreDelta24h desc
 * - Secondary: evidenceConfidenceDelta desc
 * - Exclude noise: ignore deltas < +2 unless evidence confidence increases or fail-fast flags are resolved
 */
export function calculateTopMovers(
  servers: MCPServerRecord[],
  previousScores: Map<string, { score: number; evidenceConfidence: number; failFastFlags: string[] }>,
  maxResults: number = 5
): MoverObject[] {
  const movers: MoverObject[] = []

  for (const server of servers) {
    const previous = previousScores.get(server.serverId)
    if (!previous) continue

    const scoreDelta = server.trustScore - previous.score
    const evidenceDelta = server.evidenceConfidence - previous.evidenceConfidence
    const removedFlags = previous.failFastFlags.filter(f => !server.failFastFlags.includes(f))
    const addedFlags = server.failFastFlags.filter(f => !previous.failFastFlags.includes(f))

    // Exclude noise: ignore deltas < +2 unless evidence confidence increases or fail-fast flags are resolved
    if (scoreDelta < 2 && evidenceDelta <= 0 && removedFlags.length === 0) {
      continue
    }

    if (scoreDelta > 0) {
      const reasonCodes: string[] = []
      if (evidenceDelta > 0) reasonCodes.push('EvidenceAdded')
      if (removedFlags.length > 0) reasonCodes.push('FailFastFlagResolved')
      if (addedFlags.length === 0 && removedFlags.length === 0 && evidenceDelta === 0) {
        reasonCodes.push('AuthClarified', 'ToolListDiffResolved')
      }

      movers.push({
        serverId: server.serverId,
        serverName: server.serverName,
        providerName: server.providerName,
        permalink: `/mcp/servers/${server.serverSlug}`,
        scoreDelta,
        reasonCodes,
        flagChanges: {
          added: addedFlags,
          removed: removedFlags,
        },
        evidenceConfidenceDelta: evidenceDelta,
      })
    }
  }

  // Sort: primary by scoreDelta desc, secondary by evidenceConfidenceDelta desc
  movers.sort((a, b) => {
    if (b.scoreDelta !== a.scoreDelta) {
      return b.scoreDelta - a.scoreDelta
    }
    return b.evidenceConfidenceDelta - a.evidenceConfidenceDelta
  })

  return movers.slice(0, maxResults)
}

/**
 * Calculate "Top Downgrades" selection
 * Rules:
 * - Primary sort: scoreDelta24h asc
 * - Always include any server that gains a fail-fast flag, even if delta small
 * - Secondary: number of new risk flags
 */
export function calculateTopDowngrades(
  servers: MCPServerRecord[],
  previousScores: Map<string, { score: number; riskFlags: string[]; failFastFlags: string[] }>,
  maxResults: number = 5
): DowngradeObject[] {
  const downgrades: DowngradeObject[] = []

  for (const server of servers) {
    const previous = previousScores.get(server.serverId)
    if (!previous) continue

    const scoreDelta = server.trustScore - previous.score
    const addedFailFastFlags = server.failFastFlags.filter(f => !previous.failFastFlags.includes(f))
    const removedFailFastFlags = previous.failFastFlags.filter(f => !server.failFastFlags.includes(f))
    const addedRiskFlags = server.riskFlags.filter(f => !previous.riskFlags.includes(f))
    const removedRiskFlags = previous.riskFlags.filter(f => !server.riskFlags.includes(f))

    // Always include if fail-fast flag added, even if delta is small
    const hasNewFailFastFlag = addedFailFastFlags.length > 0

    if (scoreDelta < 0 || hasNewFailFastFlag) {
      const reasonCodes: string[] = []
      if (hasNewFailFastFlag) reasonCodes.push('NewFailFastFlag')
      if (addedRiskFlags.length > 0) reasonCodes.push('NewRiskFlag')
      if (removedFailFastFlags.length === 0 && addedFailFastFlags.length === 0) {
        reasonCodes.push('EvidenceRemoved', 'ToolScopeExpanded')
      }

      downgrades.push({
        serverId: server.serverId,
        serverName: server.serverName,
        providerName: server.providerName,
        permalink: `/mcp/servers/${server.serverSlug}`,
        scoreDelta: hasNewFailFastFlag && scoreDelta >= 0 ? -1 : scoreDelta, // Ensure negative if fail-fast flag added
        reasonCodes,
        flagChanges: {
          added: [...addedFailFastFlags, ...addedRiskFlags],
          removed: [...removedFailFastFlags, ...removedRiskFlags],
        },
        evidenceConfidenceDelta: 0, // TODO: Calculate if we track previous evidence confidence
      })
    }
  }

  // Sort: primary by scoreDelta asc, secondary by number of new flags desc
  downgrades.sort((a, b) => {
    if (a.scoreDelta !== b.scoreDelta) {
      return a.scoreDelta - b.scoreDelta
    }
    return b.flagChanges.added.length - a.flagChanges.added.length
  })

  return downgrades.slice(0, maxResults)
}

/**
 * Calculate "New Entrants"
 * Servers first observed in last 24h
 */
export function calculateNewEntrants(
  servers: MCPServerRecord[],
  firstObservedThreshold: Date = new Date(Date.now() - 24 * 60 * 60 * 1000),
  maxResults: number = 10
): NewEntrantObject[] {
  const entrants: NewEntrantObject[] = []

  for (const server of servers) {
    const firstObserved = new Date(server.lastAssessedAt)
    if (firstObserved >= firstObservedThreshold) {
      entrants.push({
        serverId: server.serverId,
        serverName: server.serverName,
        providerName: server.providerName,
        permalink: `/mcp/servers/${server.serverSlug}`,
        authModel: server.authModel,
        deploymentType: server.deploymentType,
        evidenceConfidence: server.evidenceConfidence,
        trustScore: server.trustScore,
        firstObservedAt: server.lastAssessedAt,
      })
    }
  }

  // Sort by first observed date desc (most recent first)
  entrants.sort((a, b) => {
    return new Date(b.firstObservedAt).getTime() - new Date(a.firstObservedAt).getTime()
  })

  return entrants.slice(0, maxResults)
}

/**
 * Calculate daily tiers snapshot
 */
export function calculateDailyTiersSnapshot(servers: MCPServerRecord[]): {
  totalServersTracked: number
  tierDistribution: { a: number; b: number; c: number; d: number }
  evidenceConfidenceDistribution: { '0': number; '1': number; '2': number; '3': number }
  failFastFlaggedServers: number
} {
  const tierDistribution = { a: 0, b: 0, c: 0, d: 0 }
  const evidenceConfidenceDistribution = { '0': 0, '1': 0, '2': 0, '3': 0 }
  let failFastFlaggedServers = 0

  for (const server of servers) {
    tierDistribution[server.tier.toLowerCase() as 'a' | 'b' | 'c' | 'd']++
    evidenceConfidenceDistribution[server.evidenceConfidence.toString() as '0' | '1' | '2' | '3']++
    if (server.failFastFlags.length > 0) {
      failFastFlaggedServers++
    }
  }

  return {
    totalServersTracked: servers.length,
    tierDistribution,
    evidenceConfidenceDistribution,
    failFastFlaggedServers,
  }
}
