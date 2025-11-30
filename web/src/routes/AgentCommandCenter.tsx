import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAgents, getAgentObservability } from '../api'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

interface Props { tenantId: string }

interface Agent {
  agent_id: string
  name: string
  role: string
  status: string
  blueprint: string
  capabilities: string[]
  collections: string[]
  last_active_at: string | null
}

export default function AgentCommandCenter({ tenantId }: Props) {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<any>(null)
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h')

  useEffect(() => {
    let mounted = true
    setLoading(true)
    
    Promise.all([
      getAgents(),
      getAgentObservability(undefined, selectedTimeRange)
    ]).then(([agentsData, metricsData]) => {
      if (!mounted) return
      setAgents(agentsData.agents || [])
      setMetrics(metricsData)
    }).finally(() => {
      if (mounted) setLoading(false)
    })
    
    // Poll for updates every 30 seconds
    const interval = setInterval(() => {
      if (mounted) {
        getAgents().then(data => {
          if (mounted) setAgents(data.agents || [])
        })
      }
    }, 30000)
    
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [selectedTimeRange])

  const agentStatusCounts = {
    active: agents.filter(a => a.status === 'active').length,
    idle: agents.filter(a => a.status === 'idle').length,
    quarantined: agents.filter(a => a.status === 'quarantined').length,
    error: agents.filter(a => a.status === 'error').length
  }

  const recentActivity = agents
    .filter(a => a.last_active_at)
    .sort((a, b) => {
      const timeA = new Date(a.last_active_at || 0).getTime()
      const timeB = new Date(b.last_active_at || 0).getTime()
      return timeB - timeA
    })
    .slice(0, 5)

  return (
    <div className="space-y-8">
      <PageHeader 
        title="Agent Command Center" 
        subtitle="Real-time agent governance, monitoring, and control."
      />

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse text-blue-400">Loading agent data...</div>
        </div>
      )}

      {!loading && (
        <>
          {/* Agent Health Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Active Agents</div>
              <div className="text-4xl font-bold text-green-400">{agentStatusCounts.active}</div>
              <div className="text-xs text-slate-500 mt-2">Currently operational</div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Idle Agents</div>
              <div className="text-4xl font-bold text-yellow-400">{agentStatusCounts.idle}</div>
              <div className="text-xs text-slate-500 mt-2">Awaiting tasks</div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Quarantined</div>
              <div className="text-4xl font-bold text-red-400">{agentStatusCounts.quarantined}</div>
              <div className="text-xs text-slate-500 mt-2">Isolated for review</div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Total Agents</div>
              <div className="text-4xl font-bold text-white">{agents.length}</div>
              <div className="text-xs text-slate-500 mt-2">Registered in system</div>
            </GlassCard>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="text-slate-400 text-sm font-medium uppercase tracking-wider">Response Time Trend</div>
                <select
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="bg-slate-800 border border-slate-700 rounded px-3 py-1 text-sm text-slate-300"
                >
                  <option value="1h">Last Hour</option>
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                </select>
              </div>
              <div className="h-64">
                {metrics?.response_time ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metrics.response_time}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="time" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Line type="monotone" dataKey="avg_ms" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-500">
                    No metrics data available
                  </div>
                )}
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Agent Activity</div>
              <div className="h-64">
                {metrics?.activity ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={metrics.activity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="agent_id" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                      <Bar dataKey="actions" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-500">
                    No activity data available
                  </div>
                )}
              </div>
            </GlassCard>
          </div>

          {/* Recent Activity Feed */}
          <GlassCard className="p-6">
            <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Recent Activity</div>
            <div className="space-y-3">
              {recentActivity.length > 0 ? (
                recentActivity.map((agent) => (
                  <div key={agent.agent_id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`h-2 w-2 rounded-full ${
                        agent.status === 'active' ? 'bg-green-400' :
                        agent.status === 'idle' ? 'bg-yellow-400' :
                        agent.status === 'quarantined' ? 'bg-red-400' :
                        'bg-slate-500'
                      }`} />
                      <div>
                        <div className="font-medium text-white">{agent.name}</div>
                        <div className="text-xs text-slate-400">{agent.role}</div>
                      </div>
                    </div>
                    <div className="text-xs text-slate-500">
                      {agent.last_active_at ? new Date(agent.last_active_at).toLocaleString() : 'Never'}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-slate-500 py-8">No recent activity</div>
              )}
            </div>
          </GlassCard>

          {/* Agent Registry Link */}
          <div className="flex justify-end">
            <Link
              to={`/tenant/${tenantId}/agents/registry`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              View Full Registry →
            </Link>
          </div>
        </>
      )}
    </div>
  )
}

