/**
 * MCP Rankings Dashboard (/mcp/rankings)
 * 
 * Purpose: filtered exploration + "trust-first" sorting.
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getRankings, type RankingsParams } from '../../api/public'
import { trackPageView } from '../../utils/analytics'

interface RankingItem {
  rank: number
  server: string
  serverSlug: string
  provider: string
  providerSlug: string
  category: string
  trustScore: number
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number
  scoreDelta24h: number
  scoreDelta7d: number
  lastVerified: string
  flags: string[]
}

export default function Rankings() {
  const [rankings, setRankings] = useState<RankingItem[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table')
  const [sortBy, setSortBy] = useState<'trustScore' | 'evidenceConfidence' | 'scoreDelta24h'>('trustScore')
  const [filters, setFilters] = useState({
    official: false,
    community: false,
    vendor: false,
    evidenceConfidence: 'all' as string,
    flags: [] as string[],
  })

  useEffect(() => {
    // Track page view
    trackPageView('/mcp/rankings')

    // Fetch rankings from API
    const fetchRankings = async () => {
      setLoading(true)
      try {
        const params: RankingsParams = {
          sort: sortBy,
          page: 1,
          pageSize: 50,
        }

        // Apply filters
        if (filters.evidenceConfidence !== 'all') {
          params.evidenceConfidence = parseInt(filters.evidenceConfidence) as 0 | 1 | 2 | 3
        }

        const result = await getRankings(params)
        
        setRankings(result.items.map((item: any, index: number) => ({
          rank: index + 1,
          server: item.serverName || item.server,
          serverSlug: item.serverSlug || item.serverId || '',
          provider: item.providerName || item.provider,
          providerSlug: item.providerSlug || item.providerId || '',
          category: item.categoryPrimary || item.category || 'Unknown',
          trustScore: item.trustScore || 0,
          tier: item.tier || 'D',
          evidenceConfidence: item.evidenceConfidence || 0,
          scoreDelta24h: item.scoreDelta24h || 0,
          scoreDelta7d: item.scoreDelta7d || 0,
          lastVerified: item.lastAssessedAt || item.assessedAt || '',
          flags: item.riskFlags || item.flags || [],
        })))

        // Track filter usage (if trackFilter function exists)
        // TODO: Implement trackFilter if needed
      } catch (error) {
        console.error('Error fetching rankings:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRankings()
  }, [filters, sortBy])

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'A': return 'text-green-400 bg-green-500/20'
      case 'B': return 'text-blue-400 bg-blue-500/20'
      case 'C': return 'text-yellow-400 bg-yellow-500/20'
      case 'D': return 'text-red-400 bg-red-500/20'
      default: return 'text-slate-400 bg-slate-500/20'
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">MCP Rankings</h1>
          <p className="text-slate-400">Trust-first exploration of MCP servers</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('table')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewMode === 'table' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Table
          </button>
          <button
            onClick={() => setViewMode('cards')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              viewMode === 'cards' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Cards
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Rail Filters */}
        <div className="lg:col-span-1">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-6">
            <h2 className="text-lg font-semibold text-white">Filters</h2>

            {/* Source Type */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Source Type</h3>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input type="checkbox" className="rounded" />
                  Official
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input type="checkbox" className="rounded" />
                  Community
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input type="checkbox" className="rounded" />
                  Vendor
                </label>
              </div>
            </div>

            {/* Evidence Confidence */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Evidence Confidence</h3>
              <select
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300"
                value={filters.evidenceConfidence}
                onChange={(e) => setFilters({ ...filters, evidenceConfidence: e.target.value })}
              >
                <option value="all">All</option>
                <option value="3">High (3)</option>
                <option value="2">Medium (2)</option>
                <option value="1">Low (1)</option>
                <option value="0">None (0)</option>
              </select>
            </div>

            {/* Flags */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Risk Flags</h3>
              <div className="space-y-2">
                {['Static keys required', 'Opaque proxy custody', 'No audit trail', 'Write tools by default'].map((flag) => (
                  <label key={flag} className="flex items-center gap-2 text-sm text-slate-300">
                    <input type="checkbox" className="rounded" />
                    {flag}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {/* Sort Controls */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-400">Sort by:</span>
              <select
                className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="trustScore">Trust Score</option>
                <option value="evidenceConfidence">Evidence Confidence</option>
                <option value="scoreDelta24h">Score Delta (24h)</option>
              </select>
            </div>
            <div className="text-sm text-slate-400">
              Showing {rankings.length} servers
            </div>
          </div>

          {/* Rankings Table */}
          {viewMode === 'table' && (
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Rank</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Server</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Provider</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Trust Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Evidence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Δ 24h</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Last Verified</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Flags</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {rankings.map((item) => (
                    <tr key={item.rank} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-slate-400">#{item.rank}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {item.serverSlug ? (
                          <Link to={`/mcp/servers/${item.serverSlug}`} className="text-white hover:text-blue-400 font-medium">
                            {item.server}
                          </Link>
                        ) : (
                          <span className="text-white font-medium">{item.server}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link to={`/mcp/providers/${item.providerSlug}`} className="text-slate-400 hover:text-white">
                          {item.provider}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-400">{item.category}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-white font-semibold">{item.trustScore}</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getTierColor(item.tier)}`}>
                            {item.tier}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-slate-400">{item.evidenceConfidence}/3</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {item.scoreDelta24h > 0 ? (
                          <span className="text-green-400">+{item.scoreDelta24h}</span>
                        ) : item.scoreDelta24h < 0 ? (
                          <span className="text-red-400">{item.scoreDelta24h}</span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                        {new Date(item.lastVerified).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {item.flags.length > 0 ? (
                          <div className="flex gap-1">
                            {item.flags.map((flag, idx) => (
                              <span key={idx} className="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded">
                                {flag}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-slate-500">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
