import { useEffect, useState } from 'react'
import { getGaps } from '../api'

interface Props { tenantId: string }

export default function Gaps({ tenantId }: Props) {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    getGaps(tenantId).then(d => {
      if (!mounted) return
      setItems(d.items || [])
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Security Gaps</h1>
        <p className="mt-1 text-sm text-slate-600">Capability coverage analysis and gap identification</p>
      </div>

      <div className="alert alert-info">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="font-medium">Prioritization Tip</p>
            <p className="text-sm mt-1">Prioritize tuning existing tools (raise ConfigScore) before recommending new tools. This often provides better ROI.</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="spinner"></div>
          <span className="ml-3 text-slate-600">Loading gaps analysis...</span>
        </div>
      ) : items.length === 0 ? (
        <div className="card p-12 text-center">
          <svg className="w-12 h-12 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-slate-600 font-medium">No gaps found</p>
          <p className="text-sm text-slate-500 mt-1">All controls have adequate capability coverage</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((it) => {
            const coveragePercent = (it.Coverage * 100).toFixed(1)
            const hasHardGaps = it.HardGaps?.length > 0
            const hasSoftGaps = it.SoftGaps?.length > 0
            
            return (
              <div key={it.ControlID} className="card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{it.ControlID}</h3>
                    <p className="text-sm text-slate-600 mt-1">Domain: {it.DomainPartition?.split('|')[1] || 'N/A'}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-semibold text-slate-900">{coveragePercent}%</div>
                    <div className="text-xs text-slate-500">Coverage</div>
                    <div className={`mt-2 badge ${parseFloat(coveragePercent) >= 80 ? 'badge-success' : parseFloat(coveragePercent) >= 50 ? 'badge-warning' : 'badge-error'}`}>
                      {parseFloat(coveragePercent) >= 80 ? 'Good' : parseFloat(coveragePercent) >= 50 ? 'Fair' : 'Poor'}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  {/* Hard Gaps */}
                  <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex items-center mb-3">
                      <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <h4 className="text-sm font-semibold text-red-900">Hard Gaps</h4>
                      <span className="ml-auto badge badge-error">{it.HardGaps?.length || 0}</span>
                    </div>
                    {hasHardGaps ? (
                      <ul className="space-y-2">
                        {it.HardGaps.map((g: any, idx: number) => (
                          <li key={idx} className="text-sm text-red-800">
                            <span className="font-medium">{g.capabilityId}</span>
                            <span className="text-red-600 ml-2">(weight: {g.weight})</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-red-700">No hard gaps found</p>
                    )}
                  </div>

                  {/* Soft Gaps */}
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                    <div className="flex items-center mb-3">
                      <svg className="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <h4 className="text-sm font-semibold text-yellow-900">Soft Gaps</h4>
                      <span className="ml-auto badge badge-warning">{it.SoftGaps?.length || 0}</span>
                    </div>
                    {hasSoftGaps ? (
                      <ul className="space-y-2">
                        {it.SoftGaps.map((g: any, idx: number) => (
                          <li key={idx} className="text-sm text-yellow-800">
                            <div className="flex items-start justify-between">
                              <span className="font-medium">{g.capabilityId}</span>
                              <span className="text-xs text-yellow-600 ml-2">
                                {g.best?.toFixed(2)} / {g.min?.toFixed(2)}
                              </span>
                            </div>
                            {g.tool && (
                              <p className="text-xs text-yellow-700 mt-1">Tool: {g.tool}</p>
                            )}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-yellow-700">No soft gaps found</p>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
