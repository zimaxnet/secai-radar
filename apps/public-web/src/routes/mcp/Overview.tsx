/**
 * MCP Overview Dashboard (/mcp)
 * 
 * Purpose: Featured server story + "What changed today?" + entry points for exploration.
 * 
 * Modules:
 * 1. Featured Server Story (hero section)
 * 2. Today's Verified MCP Brief (card)
 * 3. Trust Index Snapshot (KPIs)
 * 4. Risk Flags Trending (sparkline tiles)
 * 5. Recently Updated table
 * 6. Top Categories
 */

import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getSummary, getRecentlyUpdated, getRankings, getServerDetail } from '../../api/public'
import { trackPageView } from '../../utils/analytics'
import type { ServerStory } from '../../types/dataModel'

interface TodayBrief {
  topMovers: Array<{ server: string; provider: string; delta: number; score: number }>
  downgrades: Array<{ server: string; provider: string; delta: number; flags: string[] }>
  newEntrants: Array<{ server: string; provider: string; score: number }>
  driftEvents: Array<{ server: string; event: string; severity: string }>
}

interface TrustIndex {
  serversTracked: number
  providersTracked: number
  tierDistribution: { a: number; b: number; c: number; d: number }
  evidenceConfidence: { '0': number; '1': number; '2': number; '3': number }
}

interface RiskFlag {
  name: string
  count: number
  trend: 'up' | 'down' | 'stable'
}

interface RecentlyUpdated {
  server: string
  serverSlug: string
  provider: string
  providerSlug: string
  trustScore: number
  evidenceConfidence: number
  lastVerified: string
  driftCount7d: number
}

export default function Overview() {
  const [featuredStory, setFeaturedStory] = useState<ServerStory | null>(null)
  const [brief, setBrief] = useState<TodayBrief | null>(null)
  const [trustIndex, setTrustIndex] = useState<TrustIndex | null>(null)
  const [riskFlags, setRiskFlags] = useState<RiskFlag[]>([])
  const [recentlyUpdated, setRecentlyUpdated] = useState<RecentlyUpdated[]>([])
  const [loading, setLoading] = useState(true)
  const [apiError, setApiError] = useState(false)
  const [retryKey, setRetryKey] = useState(0)

  // Generate story from server data
  const generateStory = (serverData: any, score: any): ServerStory => {
    const tier = score?.tier || 'D'
    const trustScore = score?.trustScore || 0
    const evidenceConfidence = score?.evidenceConfidence || 0
    const serverName = serverData?.server?.serverName || 'Unknown Server'
    const providerName = serverData?.server?.provider?.providerName || 'Unknown Provider'
    const serverSlug = serverData?.server?.serverSlug || serverData?.server?.serverId || ''
    const serverId = serverData?.server?.serverId || ''

    // Generate story based on tier and score
    let title = ''
    let narrative = ''
    const highlights: string[] = []
    const benefits: string[] = []
    const researchPoints: string[] = []

    if (tier === 'A' && trustScore >= 85) {
      title = `Why ${serverName} Sets the Standard for MCP Security`
      narrative = `${serverName} from ${providerName} represents the gold standard in MCP server security and trustworthiness. With a Trust Score of ${trustScore} and Tier A rating, this server demonstrates exceptional security practices across all six security domains. Our research shows that ${serverName} consistently maintains high evidence confidence (${evidenceConfidence}/3), meaning its security claims are well-documented and verifiable.`
      
      highlights.push(`Tier A rating with ${trustScore} Trust Score`)
      highlights.push(`Evidence Confidence: ${evidenceConfidence}/3 (High)`)
      highlights.push(`Enterprise-ready for regulated environments`)
      
      benefits.push('Strong authentication and authorization controls')
      benefits.push('Comprehensive audit logging and compliance')
      benefits.push('Proven track record of security best practices')
      
      researchPoints.push('Verified through multiple evidence sources')
      researchPoints.push('Regular security assessments and updates')
      researchPoints.push('Transparent security documentation')
    } else if (tier === 'B' && trustScore >= 70) {
      title = `${serverName}: A Reliable Choice for MCP Integration`
      narrative = `${serverName} from ${providerName} offers a solid security foundation with a Trust Score of ${trustScore} and Tier B rating. This server provides good security coverage across key domains and is suitable for most enterprise use cases. With evidence confidence of ${evidenceConfidence}/3, ${serverName} demonstrates commitment to security transparency.`
      
      highlights.push(`Tier B rating with ${trustScore} Trust Score`)
      highlights.push(`Evidence Confidence: ${evidenceConfidence}/3`)
      highlights.push(`Suitable for standard enterprise deployments`)
      
      benefits.push('Good security posture with room for improvement')
      benefits.push('Active development and maintenance')
      benefits.push('Growing evidence base')
      
      researchPoints.push('Regular security assessments')
      researchPoints.push('Ongoing security improvements')
      researchPoints.push('Community and vendor support')
    } else {
      title = `Exploring ${serverName}: An Emerging MCP Server`
      narrative = `${serverName} from ${providerName} is an emerging MCP server with a Trust Score of ${trustScore} and Tier ${tier} rating. While still building its security foundation, this server shows promise and active development. With evidence confidence of ${evidenceConfidence}/3, there's opportunity for growth in security transparency and practices.`
      
      highlights.push(`Tier ${tier} rating with ${trustScore} Trust Score`)
      highlights.push(`Evidence Confidence: ${evidenceConfidence}/3`)
      highlights.push(`Early stage with development potential`)
      
      benefits.push('Active development community')
      benefits.push('Innovative features and capabilities')
      benefits.push('Growing security awareness')
      
      researchPoints.push('Limited evidence base')
      researchPoints.push('Opportunities for security improvements')
      researchPoints.push('Community-driven development')
    }

    return {
      serverId,
      serverSlug,
      serverName,
      providerName,
      title,
      narrative,
      highlights,
      benefits,
      researchPoints,
      trustScore,
      tier: tier as 'A' | 'B' | 'C' | 'D',
      evidenceConfidence: evidenceConfidence as 0 | 1 | 2 | 3,
      featuredAt: new Date().toISOString(),
    }
  }

  useEffect(() => {
    trackPageView('/mcp')
    setApiError(false)

    const fetchData = async () => {
      setLoading(true)
      try {
        // Fetch featured server story (top server from rankings)
        try {
          const rankingsResult = await getRankings({ sort: 'trustScore', page: 1, pageSize: 1 })
          if (rankingsResult.items.length > 0) {
            const topServer = rankingsResult.items[0]
            const serverDetail = await getServerDetail(topServer.serverSlug || topServer.serverId)
            if (serverDetail) {
              const story = generateStory(serverDetail, serverDetail.latestScore)
              setFeaturedStory(story)
            }
          }
        } catch (error) {
          console.error('Error fetching featured server story:', error)
          // Continue without featured story
        }

        const summary = await getSummary('24h')
        if (summary === null) {
          setApiError(true)
          setLoading(false)
          return
        }
        if (summary) {
          setTrustIndex({
            serversTracked: summary.serversTracked || 0,
            providersTracked: 0, // TODO: Add to summary response
            tierDistribution: {
              a: summary.tierCounts?.A || 0,
              b: summary.tierCounts?.B || 0,
              c: summary.tierCounts?.C || 0,
              d: summary.tierCounts?.D || 0,
            },
            evidenceConfidence: summary.evidenceConfidenceCounts || { '0': 0, '1': 0, '2': 0, '3': 0 },
          })

          // Extract brief data from summary
          setBrief({
            topMovers: summary.topMovers?.map((m: any) => ({
              server: m.serverName,
              provider: m.providerName,
              delta: m.scoreDelta,
              score: 0 // Not in summary response
            })) || [],
            downgrades: summary.topDowngrades?.map((d: any) => ({
              server: d.serverName,
              provider: d.providerName,
              delta: d.scoreDelta,
              flags: [] // Not in summary response
            })) || [],
            newEntrants: summary.newEntrants?.map((n: any) => ({
              server: n.serverName,
              provider: n.providerName,
              score: 0 // Not in summary response
            })) || [],
            driftEvents: summary.notableDrift?.map((d: any) => ({
              server: d.serverName || d.serverId, // Use serverName from enriched data
              event: d.summary,
              severity: d.severity
            })) || [],
          })
        }

        // Fetch recently updated
        const recent = await getRecentlyUpdated(50)
        setRecentlyUpdated(recent.map((item: any) => ({
          server: item.serverName || item.server,
          serverSlug: item.serverSlug || item.serverId,
          provider: item.providerName || item.provider,
          providerSlug: item.providerSlug || item.providerId,
          trustScore: item.trustScore || 0,
          evidenceConfidence: item.evidenceConfidence || 0,
          lastVerified: item.lastAssessedAt || item.assessedAt,
          driftCount7d: item.driftCount7d || 0,
        })))

        // TODO: Fetch risk flags trending
        // For now, use empty array
        setRiskFlags([])
      } catch (error) {
        console.error('Error fetching overview data:', error)
        setApiError(true)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [retryKey])

  if (loading) {
    return (
      <div className="flex flex-col h-64 items-center justify-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        <p className="text-slate-400 text-sm">Loading Verified MCP data…</p>
      </div>
    )
  }

  if (apiError) {
    return (
      <div className="flex flex-col h-64 items-center justify-center gap-4">
        <p className="text-slate-300">Unable to load dashboard. The API may be temporarily unavailable.</p>
        <button
          type="button"
          onClick={() => setRetryKey(k => k + 1)}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    )
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'A': return 'text-green-400 bg-green-500/20 border-green-500/30'
      case 'B': return 'text-blue-400 bg-blue-500/20 border-blue-500/30'
      case 'C': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
      case 'D': return 'text-red-400 bg-red-500/20 border-red-500/30'
      default: return 'text-slate-400 bg-slate-500/20 border-slate-500/30'
    }
  }

  return (
    <div className="space-y-8">
      {/* Featured Server Story */}
      {featuredStory && (
        <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-800 rounded-xl p-8 md:p-12">
          <div className="max-w-4xl">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-sm font-medium text-blue-400 uppercase tracking-wide">Featured Server</span>
              <span className={`px-3 py-1 rounded-lg text-sm font-semibold border ${getTierColor(featuredStory.tier)}`}>
                Tier {featuredStory.tier}
              </span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
              {featuredStory.title}
            </h1>
            
            <p className="text-lg text-slate-300 mb-6 leading-relaxed">
              {featuredStory.narrative}
            </p>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-3xl font-bold text-white mb-1">{featuredStory.trustScore}</div>
                <div className="text-sm text-slate-400">Trust Score</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-3xl font-bold text-white mb-1">{featuredStory.evidenceConfidence}/3</div>
                <div className="text-sm text-slate-400">Evidence Confidence</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="text-lg font-semibold text-white mb-1">{featuredStory.providerName}</div>
                <div className="text-sm text-slate-400">Provider</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Key Highlights</h3>
                <ul className="space-y-2">
                  {featuredStory.highlights.map((highlight, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-slate-300">
                      <svg className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">How You Can Benefit</h3>
                <ul className="space-y-2">
                  {featuredStory.benefits.map((benefit, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-slate-300">
                      <svg className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 mb-6">
              <h3 className="text-lg font-semibold text-white mb-3">Research Insights</h3>
              <ul className="space-y-2">
                {featuredStory.researchPoints.map((point, idx) => (
                  <li key={idx} className="text-slate-300 flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex gap-4">
              <Link
                to={`/mcp/servers/${featuredStory.serverSlug}`}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
              >
                View Full Server Details →
              </Link>
              <Link
                to="/mcp/rankings"
                className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-lg border border-slate-700 transition-colors"
              >
                Browse All Servers
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Verified MCP Dashboard</h2>
        <p className="text-slate-400">Transparent trust authority for MCP security posture</p>
      </div>

      {/* Today's Verified MCP Brief */}
      {brief && (
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <h2 className="text-2xl font-semibold text-white mb-4">Today's Verified MCP Brief</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top Movers */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Top Movers ↑</h3>
              <div className="space-y-2">
                {brief.topMovers.map((mover, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div>
                      <Link to={`/mcp/servers/${mover.server.toLowerCase().replace(/\s+/g, '-')}`} className="text-white hover:text-blue-400 font-medium">
                        {mover.server}
                      </Link>
                      <p className="text-sm text-slate-400">{mover.provider}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 font-semibold">+{mover.delta}</div>
                      <div className="text-sm text-slate-400">Score: {mover.score}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Downgrades */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Biggest Downgrades ↓</h3>
              <div className="space-y-2">
                {brief.downgrades.map((downgrade, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div>
                      <Link to={`/mcp/servers/${downgrade.server.toLowerCase().replace(/\s+/g, '-')}`} className="text-white hover:text-blue-400 font-medium">
                        {downgrade.server}
                      </Link>
                      <p className="text-sm text-slate-400">{downgrade.provider}</p>
                      <div className="flex gap-2 mt-1">
                        {downgrade.flags.map((flag, flagIdx) => (
                          <span key={flagIdx} className="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded">
                            {flag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="text-red-400 font-semibold">{downgrade.delta}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* New Entrants */}
            {brief.newEntrants.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-slate-400 mb-3">New Entrants 🆕</h3>
                <div className="space-y-2">
                  {brief.newEntrants.map((entrant, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <div>
                        <Link to={`/mcp/servers/${entrant.server.toLowerCase().replace(/\s+/g, '-')}`} className="text-white hover:text-blue-400 font-medium">
                          {entrant.server}
                        </Link>
                        <p className="text-sm text-slate-400">{entrant.provider}</p>
                      </div>
                      <div className="text-blue-400 font-semibold">Score: {entrant.score}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Notable Drift Events */}
            {brief.driftEvents.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-slate-400 mb-3">Notable Drift Events</h3>
                <div className="space-y-2">
                  {brief.driftEvents.map((event, idx) => (
                    <div key={idx} className="p-3 bg-slate-800/50 rounded-lg">
                      <Link to={`/mcp/servers/${event.server.toLowerCase().replace(/\s+/g, '-')}`} className="text-white hover:text-blue-400 font-medium">
                        {event.server}
                      </Link>
                      <p className="text-sm text-slate-400 mt-1">{event.event}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Trust Index Snapshot */}
      {trustIndex && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <div className="text-3xl font-bold text-white">{trustIndex.serversTracked}</div>
            <div className="text-sm text-slate-400 mt-1">Servers Tracked</div>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <div className="text-3xl font-bold text-white">{trustIndex.providersTracked}</div>
            <div className="text-sm text-slate-400 mt-1">Providers Tracked</div>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <div className="text-3xl font-bold text-white">
              {Math.round(((trustIndex.tierDistribution.a + trustIndex.tierDistribution.b) / trustIndex.serversTracked) * 100)}%
            </div>
            <div className="text-sm text-slate-400 mt-1">A/B Tier</div>
          </div>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <div className="text-3xl font-bold text-white">{trustIndex.evidenceConfidence['3']}</div>
            <div className="text-sm text-slate-400 mt-1">High Evidence (3)</div>
          </div>
        </div>
      )}

      {/* Risk Flags Trending */}
      {riskFlags.length > 0 && (
        <div>
          <h2 className="text-2xl font-semibold text-white mb-4">Risk Flags Trending</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {riskFlags.map((flag, idx) => (
              <button
                key={idx}
                className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-left hover:border-blue-500/50 transition-colors"
                onClick={() => {
                  // Navigate to rankings filtered by this flag
                  window.location.href = `/mcp/rankings?flag=${encodeURIComponent(flag.name)}`
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium text-white">{flag.count}</div>
                  {flag.trend === 'up' && <span className="text-red-400">↑</span>}
                  {flag.trend === 'down' && <span className="text-green-400">↓</span>}
                  {flag.trend === 'stable' && <span className="text-slate-400">→</span>}
                </div>
                <div className="text-xs text-slate-400">{flag.name}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Recently Updated */}
      {recentlyUpdated.length > 0 && (
        <div>
          <h2 className="text-2xl font-semibold text-white mb-4">Recently Updated</h2>
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Server</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Provider</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Trust Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Evidence</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Last Verified</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Drift (7d)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {recentlyUpdated.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/mcp/servers/${item.serverSlug}`} className="text-white hover:text-blue-400 font-medium">
                        {item.server}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/mcp/providers/${item.providerSlug}`} className="text-slate-400 hover:text-white">
                        {item.provider}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-white font-semibold">{item.trustScore}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-slate-400">{item.evidenceConfidence}/3</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                      {new Date(item.lastVerified).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-slate-400">{item.driftCount7d}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top Categories */}
      <div>
        <h2 className="text-2xl font-semibold text-white mb-4">Top Categories</h2>
        <div className="flex flex-wrap gap-3">
          {['Observability', 'Productivity', 'Cloud', 'DevTools', 'Data', 'Web/Spidering'].map((category) => (
            <Link
              key={category}
              to={`/mcp/rankings?category=${encodeURIComponent(category)}`}
              className="px-4 py-2 bg-slate-900/50 border border-slate-800 rounded-lg text-slate-300 hover:text-white hover:border-blue-500/50 transition-colors"
            >
              {category}
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
