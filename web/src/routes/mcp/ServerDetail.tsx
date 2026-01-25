/**
 * MCP Server Detail (/mcp/servers/{serverSlug})
 * 
 * Purpose: full transparency - why scored, what changed, and what evidence exists.
 */

import { useParams, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'

interface ServerData {
  id: string
  name: string
  slug: string
  provider: string
  providerSlug: string
  trustScore: number
  tier: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence: number
  lastVerified: string
  enterpriseFit: 'Regulated' | 'Standard' | 'Experimental'
  domainBreakdown: { domain: string; score: number }[]
  failFastChecklist: { item: string; pass: boolean }[]
  flags: Array<{ name: string; severity: string; mitigation: string }>
}

export default function ServerDetail() {
  const { serverSlug } = useParams<{ serverSlug: string }>()
  const [server, setServer] = useState<ServerData | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'evidence' | 'drift' | 'graph' | 'response'>('overview')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual API calls
    // GET /api/v1/public/mcp/servers/{serverId}
    // GET /api/v1/public/mcp/servers/{serverId}/evidence
    // GET /api/v1/public/mcp/servers/{serverId}/drift?window=90d
    // GET /api/v1/public/mcp/servers/{serverId}/graph

    // Mock data
    setTimeout(() => {
      setServer({
        id: '1',
        name: 'GitHub MCP',
        slug: serverSlug || 'github-mcp',
        provider: 'GitHub',
        providerSlug: 'github',
        trustScore: 87,
        tier: 'A',
        evidenceConfidence: 3,
        lastVerified: '2026-01-23T10:30:00Z',
        enterpriseFit: 'Standard',
        domainBreakdown: [
          { domain: 'D1: Authentication', score: 92 },
          { domain: 'D2: Authorization', score: 88 },
          { domain: 'D3: Data Protection', score: 85 },
          { domain: 'D4: Audit & Logging', score: 90 },
          { domain: 'D5: Operational Security', score: 82 },
          { domain: 'D6: Compliance', score: 78 },
        ],
        failFastChecklist: [
          { item: 'Static keys required', pass: true },
          { item: 'Opaque proxy custody', pass: true },
          { item: 'No audit trail claim', pass: true },
          { item: 'Write tools enabled by default', pass: false },
        ],
        flags: [
          { name: 'Write tools enabled by default', severity: 'medium', mitigation: 'Configure tool permissions explicitly' },
        ],
      })
      setLoading(false)
    }, 500)
  }, [serverSlug])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    )
  }

  if (!server) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-white mb-2">Server Not Found</h2>
        <p className="text-slate-400 mb-4">The requested server could not be found.</p>
        <Link to="/mcp/rankings" className="text-blue-400 hover:text-blue-300">
          Browse all servers →
        </Link>
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
    <div className="space-y-6">
      {/* Hero Header */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold text-white">{server.name}</h1>
              <span className={`px-3 py-1 rounded-lg text-sm font-semibold border ${getTierColor(server.tier)}`}>
                Tier {server.tier}
              </span>
            </div>
            <Link to={`/mcp/providers/${server.providerSlug}`} className="text-lg text-slate-400 hover:text-white transition-colors">
              {server.provider}
            </Link>
            <div className="flex items-center gap-6 mt-4">
              <div>
                <div className="text-3xl font-bold text-white">{server.trustScore}</div>
                <div className="text-sm text-slate-400">Trust Score</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-white">{server.evidenceConfidence}/3</div>
                <div className="text-sm text-slate-400">Evidence Confidence</div>
              </div>
              <div>
                <div className="text-sm font-medium text-slate-400">Last Verified</div>
                <div className="text-sm text-slate-300">{new Date(server.lastVerified).toLocaleString()}</div>
              </div>
              <div>
                <span className="px-3 py-1 bg-slate-800 rounded-lg text-sm text-slate-300">
                  {server.enterpriseFit}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <nav className="flex gap-1">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'evidence', label: 'Evidence' },
            { id: 'drift', label: 'Drift Timeline' },
            { id: 'graph', label: 'Trust Graph' },
            { id: 'response', label: 'Provider Response' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-white hover:border-slate-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Domain Breakdown */}
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">Domain Breakdown</h2>
              <div className="space-y-3">
                {server.domainBreakdown.map((domain, idx) => (
                  <div key={idx}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-300">{domain.domain}</span>
                      <span className="text-sm font-semibold text-white">{domain.score}</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${domain.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Fail-Fast Checklist */}
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">Fail-Fast Checklist</h2>
              <div className="space-y-2">
                {server.failFastChecklist.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                    {item.pass ? (
                      <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                    <span className={`text-sm ${item.pass ? 'text-green-400' : 'text-red-400'}`}>
                      {item.item}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Flags & Mitigations */}
            {server.flags.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Key Flags & Recommended Mitigations</h2>
                <div className="space-y-3">
                  {server.flags.map((flag, idx) => (
                    <div key={idx} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-medium text-white">{flag.name}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          flag.severity === 'high' ? 'bg-red-500/20 text-red-400' :
                          flag.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {flag.severity}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">{flag.mitigation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="text-center py-12">
            <p className="text-slate-400">Evidence tab - Coming soon</p>
            <p className="text-sm text-slate-500 mt-2">Will show evidence list, extracted claims, and citations</p>
          </div>
        )}

        {activeTab === 'drift' && (
          <div className="text-center py-12">
            <p className="text-slate-400">Drift Timeline tab - Coming soon</p>
            <p className="text-sm text-slate-500 mt-2">Will show timeline of changes, tools added/removed, auth changes, etc.</p>
          </div>
        )}

        {activeTab === 'graph' && (
          <div className="text-center py-12">
            <p className="text-slate-400">Trust Graph Explorer tab - Coming soon</p>
            <p className="text-sm text-slate-500 mt-2">Will show interactive graph: Server → Tools → Scopes → Data Domains → Evidence</p>
          </div>
        )}

        {activeTab === 'response' && (
          <div className="text-center py-12">
            <p className="text-slate-400">Provider Response tab - Coming soon</p>
            <p className="text-sm text-slate-500 mt-2">Will show vendor right-to-respond statement and submission status</p>
          </div>
        )}
      </div>
    </div>
  )
}
