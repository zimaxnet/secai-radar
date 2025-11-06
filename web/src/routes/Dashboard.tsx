import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
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

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">SecAI Radar Dashboard</h1>
        <p className="text-blue-100">Security assessment overview by domain</p>
      </div>

      {loading && <div className="text-gray-500">Loading…</div>}

      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Security Domains</h2>
        <p className="text-sm text-gray-600 mb-4">
          Click on any domain to view controls, enter observations, see gaps, and track progress for that security domain.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {byDomain.map((d) => {
            const progressPercent = d.total > 0 ? (d.complete / d.total) * 100 : 0
            return (
              <Link
                key={d.domain}
                to={`/tenant/${tenantId}/domain/${d.domain}`}
                className="rounded-lg border-2 border-gray-200 bg-white p-5 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer group"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="text-lg font-bold text-gray-900">{d.domain}</div>
                  <div className="text-xs text-gray-500 group-hover:text-blue-600">→</div>
                </div>
                <div className="mb-3">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-gray-900">{d.complete}</span>
                    <span className="text-sm text-gray-500">/ {d.total}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">controls complete</div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div 
                    className="bg-blue-600 rounded-full h-2 transition-all"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
                <div className="flex gap-3 text-xs text-gray-600">
                  <span>✓ {d.complete}</span>
                  <span>⏳ {d.inProgress}</span>
                  <span>○ {d.notStarted}</span>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs font-medium text-blue-600 group-hover:text-blue-800">
                    View Domain Assessment →
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      </div>

      {byDomain.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Progress Overview</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="domain" />
                <PolarRadiusAxis />
                <Radar name="Complete" dataKey="Complete" stroke="#2563eb" fill="#2563eb" fillOpacity={0.6} />
                <Radar name="InProgress" dataKey="InProgress" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
