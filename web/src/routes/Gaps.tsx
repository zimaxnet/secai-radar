import { useEffect, useState } from 'react'
import { getGaps, getAIRecommendation, getAIUsageSummary } from '../api'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'

interface Props { tenantId: string }

export default function Gaps({ tenantId }: Props) {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(false)
  const [selectedControlId, setSelectedControlId] = useState<string | null>(null)
  const [aiRecommendations, setAiRecommendations] = useState<Record<string, { loading: boolean; text?: string; error?: string }>>({})
  const [usageSummary, setUsageSummary] = useState<any>(null)

  // Fetch Gaps
  useEffect(() => {
    let mounted = true
    setLoading(true)
    getGaps(tenantId, aiEnabled).then(d => {
      if (!mounted) return
      setItems(d.items || [])
      if (d.items?.length > 0 && !selectedControlId) {
        setSelectedControlId(d.items[0].ControlID)
      }
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId, aiEnabled])

  // Fetch AI Usage
  useEffect(() => {
    if (aiEnabled) {
      getAIUsageSummary(tenantId).then(setUsageSummary).catch(console.error)
    }
  }, [aiEnabled, tenantId])

  const loadAIRecommendation = async (controlId: string) => {
    if (aiRecommendations[controlId]) return
    
    setAiRecommendations(prev => ({ ...prev, [controlId]: { loading: true } }))
    try {
      const result = await getAIRecommendation(tenantId, controlId)
      setAiRecommendations(prev => ({
        ...prev,
        [controlId]: { loading: false, text: result.recommendation }
      }))
      // Refresh usage
      getAIUsageSummary(tenantId).then(setUsageSummary).catch(console.error)
    } catch (error: any) {
      setAiRecommendations(prev => ({
        ...prev,
        [controlId]: { loading: false, error: error.message }
      }))
    }
  }

  // Auto-load AI for selected if enabled
  useEffect(() => {
    if (aiEnabled && selectedControlId) {
      loadAIRecommendation(selectedControlId)
    }
  }, [aiEnabled, selectedControlId])

  const selectedItem = items.find(i => i.ControlID === selectedControlId)
  const recommendation = selectedControlId ? aiRecommendations[selectedControlId] : null

  return (
    <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col">
      <PageHeader 
        title="Gap Analysis" 
        subtitle="Identify and remediate security control deficiencies."
        action={
          <div className="flex items-center gap-3 bg-slate-900/50 p-1 rounded-full border border-white/10">
            <button 
              onClick={() => setAiEnabled(!aiEnabled)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                aiEnabled ? 'bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]' : 'text-slate-400 hover:text-white'
              }`}
            >
              {aiEnabled ? 'AI Copilot Active' : 'Enable AI Copilot'}
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-12 gap-6 flex-1 overflow-hidden">
        {/* Left Column: Gaps List */}
        <div className="col-span-5 flex flex-col gap-4 overflow-y-auto pr-2">
          {loading && <div className="text-slate-500 animate-pulse">Scanning for gaps...</div>}
          
          {!loading && items.length === 0 && (
            <div className="text-slate-400 p-8 text-center border border-dashed border-slate-700 rounded-xl">
              No gaps identified. Great job!
            </div>
          )}

          {items.map(item => {
            const isSelected = item.ControlID === selectedControlId
            const hardGaps = item.HardGaps?.length || 0
            const softGaps = item.SoftGaps?.length || 0
            
            return (
              <div 
                key={item.ControlID}
                onClick={() => setSelectedControlId(item.ControlID)}
                className={`
                  cursor-pointer p-4 rounded-xl border transition-all duration-200
                  ${isSelected 
                    ? 'bg-blue-600/10 border-blue-500/50 shadow-[0_0_20px_rgba(37,99,235,0.1)]' 
                    : 'bg-slate-900/40 border-white/5 hover:border-white/10 hover:bg-slate-800/40'}
                `}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`font-mono text-sm ${isSelected ? 'text-blue-400' : 'text-slate-400'}`}>
                    {item.ControlID}
                  </span>
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                    {(item.Coverage * 100).toFixed(0)}% Cov
                  </span>
                </div>
                <div className="font-medium text-slate-200 mb-3 line-clamp-1">{item.ControlTitle || "Untitled Control"}</div>
                <div className="flex gap-2">
                  {hardGaps > 0 && (
                    <span className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 border border-red-500/20">
                      {hardGaps} Hard Gaps
                    </span>
                  )}
                  {softGaps > 0 && (
                    <span className="text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-400 border border-orange-500/20">
                      {softGaps} Soft Gaps
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Right Column: Detail & AI Panel */}
        <div className="col-span-7">
          <GlassCard className="h-full flex flex-col">
            {selectedItem ? (
              <>
                <div className="p-6 border-b border-white/10">
                  <h2 className="text-xl font-bold text-white mb-1">{selectedItem.ControlTitle}</h2>
                  <p className="text-slate-400 text-sm">{selectedItem.ControlID} • {selectedItem.DomainPartition}</p>
                </div>
                
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {/* Gap Details */}
                  <div className="space-y-4">
                    <h3 className="text-sm font-medium text-slate-300 uppercase tracking-wider">Deficiencies</h3>
                    {selectedItem.HardGaps?.map((g: any, i: number) => (
                      <div key={i} className="p-3 rounded bg-red-500/10 border border-red-500/20 flex justify-between items-center">
                        <span className="text-red-200 font-mono text-sm">{g.capabilityId}</span>
                        <span className="text-xs text-red-400">Missing Capability</span>
                      </div>
                    ))}
                    {selectedItem.SoftGaps?.map((g: any, i: number) => (
                      <div key={i} className="p-3 rounded bg-orange-500/10 border border-orange-500/20 flex justify-between items-center">
                        <span className="text-orange-200 font-mono text-sm">{g.capabilityId}</span>
                        <span className="text-xs text-orange-400">Config: {g.best?.toFixed(2)} / {g.min?.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>

                  {/* AI Remediation */}
                  {aiEnabled ? (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                      <div className="flex items-center gap-2 mb-4 mt-8">
                        <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                        <h3 className="text-sm font-medium text-blue-400 uppercase tracking-wider">AI Remediation Plan</h3>
                      </div>
                      
                      <div className="bg-slate-950/50 rounded-xl border border-blue-500/20 p-5">
                        {recommendation?.loading ? (
                          <div className="flex items-center gap-3 text-slate-400">
                            <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                            Analyzing tool capabilities...
                          </div>
                        ) : recommendation?.error ? (
                          <div className="text-red-400 text-sm">{recommendation.error}</div>
                        ) : recommendation?.text ? (
                          <div className="prose prose-invert prose-sm max-w-none">
                            <div className="whitespace-pre-wrap text-slate-300 leading-relaxed">
                              {recommendation.text}
                            </div>
                          </div>
                        ) : (
                          <div className="text-slate-500 text-sm">Select a control to generate insights.</div>
                        )}
                      </div>

                      {/* AI Usage Stats (Mini) */}
                      {usageSummary && (
                        <div className="mt-4 text-xs text-slate-600 flex gap-4">
                          <span>Tokens: {usageSummary.totalTokens}</span>
                          <span>Last Run: {new Date(usageSummary.lastRun).toLocaleTimeString()}</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="mt-12 text-center">
                      <button 
                        onClick={() => setAiEnabled(true)}
                        className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors border border-white/5"
                      >
                        Activate AI Copilot to see remediation steps
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">
                Select a gap to view details
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
