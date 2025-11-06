import { useEffect, useState } from 'react'
import { getGaps, getAIRecommendation } from '../api'

interface Props { tenantId: string }

export default function Gaps({ tenantId }: Props) {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(false)
  const [aiRecommendations, setAiRecommendations] = useState<Record<string, { loading: boolean; text?: string; error?: string }>>({})

  useEffect(() => {
    let mounted = true
    setLoading(true)
    getGaps(tenantId, aiEnabled).then(d => {
      if (!mounted) return
      setItems(d.items || [])
      // If AI is enabled, items may already have AIRecommendation
      if (d.aiEnabled && d.items) {
        const recommendations: Record<string, { loading: boolean; text?: string }> = {}
        d.items.forEach((it: any) => {
          if (it.AIRecommendation) {
            recommendations[it.ControlID] = { loading: false, text: it.AIRecommendation }
          }
        })
        setAiRecommendations(recommendations)
      }
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId, aiEnabled])

  const loadAIRecommendation = async (controlId: string) => {
    if (aiRecommendations[controlId]) return // Already loaded
    
    setAiRecommendations(prev => ({ ...prev, [controlId]: { loading: true } }))
    try {
      const result = await getAIRecommendation(tenantId, controlId)
      setAiRecommendations(prev => ({
        ...prev,
        [controlId]: { loading: false, text: result.recommendation }
      }))
    } catch (error: any) {
      setAiRecommendations(prev => ({
        ...prev,
        [controlId]: { loading: false, error: error.message || 'Failed to load AI recommendation' }
      }))
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Gaps</h2>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={aiEnabled}
            onChange={(e) => setAiEnabled(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm text-gray-700">Enable AI Recommendations</span>
        </label>
      </div>
      <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 p-2 rounded">
        Tip: prioritize tuning existing tools (raise ConfigScore) before recommending net-new.
      </p>
      {loading && <div className="text-gray-500">Loading…</div>}
      <div className="space-y-3">
        {items.map(it => {
          const hasGaps = (it.HardGaps?.length || 0) + (it.SoftGaps?.length || 0) > 0
          const rec = aiRecommendations[it.ControlID]
          const showAIButton = aiEnabled && hasGaps && !rec?.text && !rec?.loading
          
          return (
            <div key={it.ControlID} className="rounded border bg-white p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">{it.ControlID}</div>
                <div className="text-sm text-gray-600">Coverage: {(it.Coverage*100).toFixed(1)}%</div>
              </div>
              <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <div className="text-sm font-semibold text-gray-700">Hard Gaps</div>
                  <ul className="list-disc list-inside text-sm text-gray-800">
                    {it.HardGaps?.length ? it.HardGaps.map((g:any, idx:number)=>(
                      <li key={idx}>{g.capabilityId} (w={g.weight})</li>
                    )) : <li className="text-gray-500">None</li>}
                  </ul>
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-700">Soft Gaps</div>
                  <ul className="list-disc list-inside text-sm text-gray-800">
                    {it.SoftGaps?.length ? it.SoftGaps.map((g:any, idx:number)=>(
                      <li key={idx}>{g.capabilityId} best={g.best?.toFixed(2)} min={g.min?.toFixed(2)} tool={g.tool || 'n/a'}</li>
                    )) : <li className="text-gray-500">None</li>}
                  </ul>
                </div>
              </div>
              
              {/* AI Recommendations Section */}
              {aiEnabled && hasGaps && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  {showAIButton && (
                    <button
                      onClick={() => loadAIRecommendation(it.ControlID)}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Get AI Recommendation →
                    </button>
                  )}
                  {rec?.loading && (
                    <div className="text-sm text-gray-500">Generating AI recommendation...</div>
                  )}
                  {rec?.text && (
                    <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded">
                      <div className="text-xs font-semibold text-blue-900 mb-1">AI Recommendation</div>
                      <div className="text-sm text-gray-800 whitespace-pre-wrap">{rec.text}</div>
                    </div>
                  )}
                  {rec?.error && (
                    <div className="mt-2 text-sm text-red-600">Error: {rec.error}</div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
