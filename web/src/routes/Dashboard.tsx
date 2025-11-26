import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { getSummary, getGaps } from '../api'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'

interface Props { tenantId: string }

export default function Dashboard({ tenantId }: Props) {
  const [byDomain, setByDomain] = useState<Array<{domain:string,total:number,complete:number,inProgress:number,notStarted:number}>>([])
  const [totalGaps, setTotalGaps] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    Promise.all([
      getSummary(tenantId),
      getGaps(tenantId)
    ]).then(([summary, gaps]) => {
      if (!mounted) return
      setByDomain(summary.byDomain || [])
      setTotalGaps(gaps.items?.length || 0)
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId])

  const radarData = useMemo(() => {
    return byDomain.map(d => ({ 
      domain: d.domain, 
      // Normalize to 100 for chart
      Coverage: d.total > 0 ? (d.complete / d.total) * 100 : 0,
      full: 100
    }))
  }, [byDomain])

  const overallProgress = useMemo(() => {
    const total = byDomain.reduce((sum, d) => sum + d.total, 0)
    const complete = byDomain.reduce((sum, d) => sum + d.complete, 0)
    return total > 0 ? Math.round((complete / total) * 100) : 0
  }, [byDomain])

  return (
    <div className="space-y-8">
      <PageHeader 
        title="Command Center" 
        subtitle="Real-time security posture and threat assessment."
      />

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse text-blue-400">Initializing Command Center...</div>
        </div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Top Row: KPI Cards */}
          <div className="lg:col-span-3">
            <GlassCard className="h-full p-6 flex flex-col justify-between">
              <div>
                <div className="text-slate-400 text-sm font-medium uppercase tracking-wider">Security Score</div>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-white text-glow">{overallProgress}</span>
                  <span className="text-xl text-slate-500">/ 100</span>
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-blue-600 to-cyan-400 h-full rounded-full shadow-[0_0_10px_rgba(56,189,248,0.5)]" 
                  style={{ width: `${overallProgress}%` }}
                />
              </div>
            </GlassCard>
          </div>

          <div className="lg:col-span-3">
            <GlassCard className="h-full p-6 flex flex-col justify-between">
              <div>
                <div className="text-slate-400 text-sm font-medium uppercase tracking-wider">Active Gaps</div>
                <div className="mt-2 text-5xl font-bold text-white text-glow">{totalGaps}</div>
              </div>
              <div className="text-sm text-red-400 mt-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                Requires Attention
              </div>
            </GlassCard>
          </div>

          <div className="lg:col-span-6">
            <GlassCard className="h-full p-6 flex items-center justify-between relative overflow-hidden">
              <div className="relative z-10">
                <div className="text-slate-400 text-sm font-medium uppercase tracking-wider">AI Threat Analysis</div>
                <div className="mt-2 text-2xl font-semibold text-white max-w-md">
                  {totalGaps > 0 
                    ? `${totalGaps} security gaps detected. AI recommends prioritizing Identity and Network controls.` 
                    : "System secure. AI monitoring active for anomalies."}
                </div>
                <Link to={`/tenant/${tenantId}/gaps`} className="inline-block mt-4 text-blue-400 hover:text-blue-300 text-sm font-medium">
                  View Remediation Plan →
                </Link>
              </div>
              {/* Abstract wave graphic decoration */}
              <div className="absolute right-0 top-0 bottom-0 w-1/2 bg-gradient-to-l from-blue-500/10 to-transparent" />
            </GlassCard>
          </div>

          {/* Middle Row: Radar & Domains */}
          <div className="lg:col-span-5 h-[500px]" data-tour="radar-chart">
            <GlassCard className="h-full p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="text-slate-400 text-sm font-medium uppercase tracking-wider">Coverage Radar</div>
              </div>
              <div className="h-[400px] w-full -ml-4">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="domain" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                      name="Coverage"
                      dataKey="Coverage"
                      stroke="#3b82f6"
                      strokeWidth={3}
                      fill="#3b82f6"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </GlassCard>
          </div>

          <div className="lg:col-span-7 h-[500px] overflow-y-auto" data-tour="domain-breakdown">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {byDomain.map((d) => {
                const progress = d.total > 0 ? Math.round((d.complete / d.total) * 100) : 0
                return (
                  <Link key={d.domain} to={`/tenant/${tenantId}/domain/${d.domain}`}>
                    <GlassCard hoverEffect className="p-5">
                      <div className="flex justify-between items-start mb-4">
                        <div className="h-10 w-10 rounded-lg bg-slate-800 flex items-center justify-center font-bold text-blue-400 border border-slate-700">
                          {d.domain}
                        </div>
                        <div className={`text-lg font-bold ${progress === 100 ? 'text-green-400' : 'text-white'}`}>
                          {progress}%
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs text-slate-400">
                          <span>Controls</span>
                          <span className="text-slate-300">{d.complete}/{d.total}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${progress === 100 ? 'bg-green-500' : 'bg-blue-500'}`} 
                            style={{ width: `${progress}%` }} 
                          />
                        </div>
                      </div>
                    </GlassCard>
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
