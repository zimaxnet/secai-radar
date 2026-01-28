/**
 * Daily Trust Brief (/mcp/daily/{YYYY-MM-DD})
 * 
 * Purpose: permalinkable story for media syndication
 * Based on Step 2: Content Objects + Feed Specs specification
 */

import { useParams, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import type { DailyTrustBrief } from '../../types/mcp'
import { getDailyBrief } from '../../api/public'
import { trackPageView } from '../../utils/analytics'

export default function DailyBrief() {
  const { date } = useParams<{ date: string }>()
  const [brief, setBrief] = useState<DailyTrustBrief | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0)

  useEffect(() => {
    const briefDate = date || new Date().toISOString().split('T')[0]
    
    // Track page view
    trackPageView(`/mcp/daily/${briefDate}`)

    // Fetch daily brief from API
    const fetchBrief = async () => {
      setLoading(true)
      try {
        const briefData = await getDailyBrief(briefDate)
        
        if (briefData) {
          // Transform API response to DailyTrustBrief format
          setBrief({
            date: briefData.date || briefDate,
            headline: briefData.headline || '',
            narrativeLong: briefData.narrativeLong || briefData.narrativeShort || '',
            narrativeShort: briefData.narrativeShort || '',
            highlights: briefData.highlights || [],
            topMovers: briefData.topMovers || [],
            topDowngrades: briefData.topDowngrades || [],
            newEntrants: briefData.newEntrants || [],
            notableDrift: (briefData.notableDrift || []).map((d: any) => ({
              ...d,
              serverName: d.serverName || d.serverId,
              providerName: d.providerName || '',
              permalink: d.permalink || `/mcp/servers/${d.serverSlug || d.serverId}`,
            })),
            tipOfTheDay: briefData.tipOfTheDay || '',
            methodologyVersion: briefData.methodologyVersion || 'v1.0',
            generatedAt: briefData.generatedAt || new Date().toISOString(),
            permalink: `/mcp/daily/${briefDate}`,
          })
        } else {
          // If API returns null, brief will remain null and show "not found" message
        }
      } catch (error) {
        console.error('Error fetching daily brief:', error)
        setBrief(null)
      } finally {
        setLoading(false)
      }
    }

    fetchBrief()
  }, [date])

  // Cycle through server stories every 5 seconds
  useEffect(() => {
    if (!brief || brief.notableDrift.length === 0) return
    
    const interval = setInterval(() => {
      setCurrentStoryIndex((prev) => (prev + 1) % brief.notableDrift.length)
    }, 5000)
    
    return () => clearInterval(interval)
  }, [brief])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    )
  }

  if (!brief) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-white mb-2">Daily Brief Not Found</h2>
        <p className="text-slate-400 mb-4">No brief available for {date}</p>
        <Link to="/mcp" className="text-blue-400 hover:text-blue-300">
          Return to Overview →
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-4xl font-bold text-white">Daily Trust Brief</h1>
          <span className="px-3 py-1 bg-slate-800 rounded-lg text-sm text-slate-400">
            {brief.date}
          </span>
        </div>
        <p className="text-slate-400">
          Methodology: {brief.methodologyVersion} • Generated: {new Date(brief.generatedAt).toLocaleString()}
        </p>
      </div>

      {/* Headline */}
      <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-white mb-2">{brief.headline}</h2>
      </div>

      {/* Narrative */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Narrative</h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-slate-300 leading-relaxed whitespace-pre-line">{brief.narrativeLong}</p>
        </div>
      </div>

      {/* Highlights */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Highlights</h2>
        <ul className="space-y-2">
          {brief.highlights.map((highlight, idx) => (
            <li key={idx} className="flex items-start gap-3 text-slate-300">
              <span className="text-blue-400 mt-1">•</span>
              <span>{highlight}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Two-Column Layout: Top Movers & Downgrades/Stories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Top Movers */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Top Movers ↑</h2>
          {brief.topMovers.length > 0 ? (
            <div className="space-y-4">
              {brief.topMovers.map((mover, idx) => (
                <div key={idx} className="p-4 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Link to={mover.permalink} className="text-lg font-semibold text-white hover:text-blue-400">
                      {mover.serverName}
                    </Link>
                    <div className="text-green-400 font-bold text-xl">+{mover.scoreDelta}</div>
                  </div>
                  <p className="text-sm text-slate-400 mb-2">{mover.providerName}</p>
                  <div className="flex flex-wrap gap-2">
                    {mover.reasonCodes.map((reason, reasonIdx) => (
                      <span key={reasonIdx} className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
                        {reason}
                      </span>
                    ))}
                    {mover.evidenceConfidenceDelta > 0 && (
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                        Evidence +{mover.evidenceConfidenceDelta}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-center py-8">No movers today</p>
          )}
        </div>

        {/* Right Column: Downgrades or Rotating Server Stories */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          {brief.topDowngrades.length > 0 ? (
            <>
              <h2 className="text-xl font-semibold text-white mb-4">Biggest Downgrades ↓</h2>
              <div className="space-y-4">
                {brief.topDowngrades.map((downgrade, idx) => (
                  <div key={idx} className="p-4 bg-slate-800/50 rounded-lg border border-red-500/20">
                    <div className="flex items-center justify-between mb-2">
                      <Link to={downgrade.permalink} className="text-lg font-semibold text-white hover:text-blue-400">
                        {downgrade.serverName}
                      </Link>
                      <div className="text-red-400 font-bold text-xl">{downgrade.scoreDelta}</div>
                    </div>
                    <p className="text-sm text-slate-400 mb-2">{downgrade.providerName}</p>
                    <div className="flex flex-wrap gap-2">
                      {downgrade.reasonCodes.map((reason, reasonIdx) => (
                        <span key={reasonIdx} className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">
                          {reason}
                        </span>
                      ))}
                      {downgrade.flagChanges.added.length > 0 && (
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs">
                          New flags: {downgrade.flagChanges.added.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : brief.notableDrift.length > 0 ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Server Stories</h2>
                <div className="flex gap-2">
                  {brief.notableDrift.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentStoryIndex(idx)}
                      className={`w-2 h-2 rounded-full transition-colors ${
                        idx === currentStoryIndex ? 'bg-blue-400' : 'bg-slate-600'
                      }`}
                      aria-label={`Go to story ${idx + 1}`}
                    />
                  ))}
                </div>
              </div>
              <div className="min-h-[300px]">
                {brief.notableDrift[currentStoryIndex] && (
                  <div className="space-y-4 animate-fade-in">
                    <div className="p-6 bg-gradient-to-br from-blue-600/10 to-purple-600/10 border border-blue-500/30 rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <Link 
                          to={brief.notableDrift[currentStoryIndex].permalink} 
                          className="text-2xl font-bold text-white hover:text-blue-400 transition-colors"
                        >
                          {brief.notableDrift[currentStoryIndex].serverName}
                        </Link>
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-semibold">
                          {brief.notableDrift[currentStoryIndex].eventType.replace(/([A-Z])/g, ' $1').trim()}
                        </span>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-sm text-slate-400">
                          <span className="px-2 py-1 bg-slate-700/50 rounded">
                            {brief.notableDrift[currentStoryIndex].providerName}
                          </span>
                          <span>•</span>
                          <span>{new Date(brief.notableDrift[currentStoryIndex].detectedAt).toLocaleDateString()}</span>
                        </div>
                        
                        <p className="text-lg text-slate-200 leading-relaxed">
                          {brief.notableDrift[currentStoryIndex].summary}
                        </p>
                        
                        <div className="pt-3 border-t border-slate-700">
                          <p className="text-sm text-slate-400 mb-2">What happened:</p>
                          <p className="text-slate-300">
                            {brief.notableDrift[currentStoryIndex].eventType === 'ToolsAdded' && 
                              `New tools have been added to this server, expanding its capabilities.`}
                            {brief.notableDrift[currentStoryIndex].eventType === 'ToolsRemoved' && 
                              `Tools were removed from this server, which may affect functionality.`}
                            {brief.notableDrift[currentStoryIndex].eventType === 'AuthChanged' && 
                              `Authentication method was updated, which could impact integration.`}
                            {brief.notableDrift[currentStoryIndex].eventType === 'ScopeChanged' && 
                              `The scope of available features or permissions has changed.`}
                            {brief.notableDrift[currentStoryIndex].eventType === 'EndpointChanged' && 
                              `Server endpoint configuration was modified.`}
                            {brief.notableDrift[currentStoryIndex].eventType === 'DocsChanged' && 
                              `Documentation was updated, potentially with important information.`}
                          </p>
                        </div>
                        
                        <Link 
                          to={brief.notableDrift[currentStoryIndex].permalink}
                          className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors text-sm font-medium mt-2"
                        >
                          View full details →
                        </Link>
                      </div>
                    </div>
                    
                    <div className="text-center text-sm text-slate-500">
                      Story {currentStoryIndex + 1} of {brief.notableDrift.length}
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-white mb-4">Biggest Downgrades ↓</h2>
              <p className="text-slate-400 text-center py-8">No downgrades today</p>
            </>
          )}
        </div>
      </div>

      {/* New Entrants */}
      {brief.newEntrants.length > 0 && (
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">New Entrants 🆕</h2>
          <div className="space-y-3">
            {brief.newEntrants.map((entrant, idx) => (
              <div key={idx} className="p-4 bg-slate-800/50 rounded-lg">
                <Link to={entrant.permalink} className="text-lg font-semibold text-white hover:text-blue-400">
                  {entrant.serverName}
                </Link>
                <p className="text-sm text-slate-400">{entrant.providerName}</p>
                <div className="flex gap-4 mt-2 text-sm text-slate-400">
                  <span>Auth: {entrant.authModel}</span>
                  <span>Deployment: {entrant.deploymentType}</span>
                  <span>Evidence: {entrant.evidenceConfidence}/3</span>
                  <span>Score: {entrant.trustScore}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tip of the Day */}
      <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-3">💡 Tip of the Day</h2>
        <p className="text-slate-300 leading-relaxed">{brief.tipOfTheDay}</p>
      </div>

      {/* Links to Server Details */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Explore Servers</h2>
        <div className="flex flex-wrap gap-3">
          {[...brief.topMovers, ...brief.topDowngrades, ...brief.newEntrants].map((item, idx) => (
            <Link
              key={idx}
              to={item.permalink}
              className="px-4 py-2 bg-slate-800 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              {item.serverName}
            </Link>
          ))}
        </div>
      </div>

      {/* Share Links */}
      <div className="text-center text-sm text-slate-400">
        <p>Share this brief: <a href={`https://secairadar.cloud${brief.permalink}`} className="text-blue-400 hover:text-blue-300">{brief.permalink}</a></p>
      </div>
    </div>
  )
}

