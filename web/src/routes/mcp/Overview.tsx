/**
 * MCP Overview Dashboard (/mcp)
 * 
 * Purpose: "What changed today?" + entry points for exploration.
 * 
 * Modules:
 * 1. Today's Verified MCP Brief (card)
 * 2. Trust Index Snapshot (KPIs)
 * 3. Risk Flags Trending (sparkline tiles)
 * 4. Recently Updated table
 * 5. Top Categories
 */

import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'

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
  const [brief, setBrief] = useState<TodayBrief | null>(null)
  const [trustIndex, setTrustIndex] = useState<TrustIndex | null>(null)
  const [riskFlags, setRiskFlags] = useState<RiskFlag[]>([])
  const [recentlyUpdated, setRecentlyUpdated] = useState<RecentlyUpdated[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual API calls
    // GET /api/v1/public/mcp/summary?window=24h
    // GET /api/v1/public/mcp/recently-updated?limit=50
    // GET /api/v1/public/mcp/flag-trends?window=30d

    // Mock data for now
    setTimeout(() => {
      setBrief({
        topMovers: [
          { server: 'GitHub MCP', provider: 'GitHub', delta: +12, score: 87 },
          { server: 'Slack MCP', provider: 'Slack', delta: +8, score: 82 },
        ],
        downgrades: [
          { server: 'Example MCP', provider: 'Example Corp', delta: -15, flags: ['static-keys'] },
        ],
        newEntrants: [
          { server: 'New Server', provider: 'New Provider', score: 65 },
        ],
        driftEvents: [
          { server: 'GitHub MCP', event: 'New tools added', severity: 'info' },
          { server: 'Slack MCP', event: 'Auth scopes changed', severity: 'warning' },
        ],
      })

      setTrustIndex({
        serversTracked: 142,
        providersTracked: 38,
        tierDistribution: { a: 23, b: 45, c: 52, d: 22 },
        evidenceConfidence: { '0': 12, '1': 28, '2': 67, '3': 35 },
      })

      setRiskFlags([
        { name: 'Static keys required', count: 34, trend: 'up' },
        { name: 'Opaque proxy custody', count: 18, trend: 'stable' },
        { name: 'No audit trail claim', count: 22, trend: 'down' },
        { name: 'Write tools enabled by default', count: 15, trend: 'up' },
        { name: 'Unclear retention/deletion', count: 28, trend: 'stable' },
      ])

      setRecentlyUpdated([
        {
          server: 'GitHub MCP',
          serverSlug: 'github-mcp',
          provider: 'GitHub',
          providerSlug: 'github',
          trustScore: 87,
          evidenceConfidence: 3,
          lastVerified: '2026-01-23T10:30:00Z',
          driftCount7d: 2,
        },
        {
          server: 'Slack MCP',
          serverSlug: 'slack-mcp',
          provider: 'Slack',
          providerSlug: 'slack',
          trustScore: 82,
          evidenceConfidence: 2,
          lastVerified: '2026-01-23T09:15:00Z',
          driftCount7d: 1,
        },
      ])

      setLoading(false)
    }, 500)
  }, [])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Verified MCP Dashboard</h1>
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
