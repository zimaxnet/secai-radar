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

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Dashboard</h2>
      {loading && <div className="text-gray-500">Loading…</div>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {byDomain.map((d) => (
          <div key={d.domain} className="rounded-lg border bg-white p-4">
            <div className="text-sm text-gray-500">{d.domain}</div>
            <div className="mt-2 text-2xl font-bold">{d.complete}/{d.total}</div>
            <div className="text-xs text-gray-500">complete</div>
          </div>
        ))}
      </div>

      <div className="h-80 rounded-lg border bg-white p-2">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="domain" />
            <PolarRadiusAxis />
            <Radar name="Complete" dataKey="Complete" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.6} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
