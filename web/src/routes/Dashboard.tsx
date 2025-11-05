import { useEffect, useMemo, useState } from 'react'
import { getSummary } from '../api'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'

interface Props { tenantId: string }

export default function Dashboard({ tenantId }: Props) {
  const [byDomain, setByDomain] = useState<Array<{domain:string,total:number,complete:number,inProgress:number,notStarted:number}>>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    getSummary(tenantId).then((d) => {
      if (!mounted) return
      setByDomain(d.byDomain || [])
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId])

  const radarData = useMemo(() => {
    return byDomain.map(d => ({ domain: d.domain, Complete: d.complete, InProgress: d.inProgress, NotStarted: d.notStarted }))
  }, [byDomain])

  const totalStats = useMemo(() => {
    return byDomain.reduce((acc, d) => ({
      total: acc.total + d.total,
      complete: acc.complete + d.complete,
      inProgress: acc.inProgress + d.inProgress,
      notStarted: acc.notStarted + d.notStarted,
    }), { total: 0, complete: 0, inProgress: 0, notStarted: 0 })
  }, [byDomain])

  const overallPercentage = totalStats.total > 0 ? Math.round((totalStats.complete / totalStats.total) * 100) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600">Security assessment overview</p>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="spinner"></div>
          <span className="ml-3 text-slate-600">Loading...</span>
        </div>
      )}

      {!loading && (
        <>
          {/* Overall Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Controls</p>
                  <p className="mt-2 text-3xl font-semibold text-slate-900">{totalStats.total}</p>
                </div>
                <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Complete</p>
                  <p className="mt-2 text-3xl font-semibold text-green-600">{totalStats.complete}</p>
                  <p className="mt-1 text-xs text-slate-500">{overallPercentage}% compliance</p>
                </div>
                <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">In Progress</p>
                  <p className="mt-2 text-3xl font-semibold text-yellow-600">{totalStats.inProgress}</p>
                </div>
                <div className="w-12 h-12 bg-yellow-50 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Not Started</p>
                  <p className="mt-2 text-3xl font-semibold text-red-600">{totalStats.notStarted}</p>
                </div>
                <div className="w-12 h-12 bg-red-50 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Domain Cards */}
          {byDomain.length > 0 && (
            <>
              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-4">By Domain</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {byDomain.map((d) => {
                    const percentage = d.total > 0 ? Math.round((d.complete / d.total) * 100) : 0
                    return (
                      <div key={d.domain} className="card p-5">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-sm font-semibold text-slate-900">{d.domain}</h3>
                            <p className="mt-1 text-xs text-slate-500">Controls assessed</p>
                          </div>
                          <span className={`badge ${percentage >= 80 ? 'badge-success' : percentage >= 50 ? 'badge-warning' : 'badge-error'}`}>
                            {percentage}%
                          </span>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-slate-600">Complete</span>
                            <span className="font-medium text-green-600">{d.complete}/{d.total}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-slate-600">In Progress</span>
                            <span className="font-medium text-yellow-600">{d.inProgress}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-slate-600">Not Started</span>
                            <span className="font-medium text-red-600">{d.notStarted}</span>
                          </div>
                          <div className="mt-3 h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-600 transition-all"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Radar Chart */}
              {radarData.length > 0 && (
                <div className="card p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">Compliance Overview</h2>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#e2e8f0" />
                        <PolarAngleAxis
                          dataKey="domain"
                          tick={{ fill: '#64748b', fontSize: 12 }}
                        />
                        <PolarRadiusAxis
                          angle={90}
                          domain={[0, 'dataMax']}
                          tick={{ fill: '#64748b', fontSize: 10 }}
                        />
                        <Radar
                          name="Complete"
                          dataKey="Complete"
                          stroke="#10b981"
                          fill="#10b981"
                          fillOpacity={0.6}
                          strokeWidth={2}
                        />
                        <Radar
                          name="In Progress"
                          dataKey="InProgress"
                          stroke="#f59e0b"
                          fill="#f59e0b"
                          fillOpacity={0.4}
                          strokeWidth={2}
                        />
                        <Radar
                          name="Not Started"
                          dataKey="NotStarted"
                          stroke="#ef4444"
                          fill="#ef4444"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}
