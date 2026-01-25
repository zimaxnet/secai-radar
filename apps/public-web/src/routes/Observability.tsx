import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getAgentObservability, getAgents } from '../api'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

interface Props { tenantId: string }

export default function Observability({ tenantId: _tenantId }: Props) {
  // tenantId available for future use
  void _tenantId
  const [searchParams] = useSearchParams()
  const agentFilter = searchParams.get('agent')
  const [agents, setAgents] = useState<any[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('24h')

  useEffect(() => {
    Promise.all([
      getAgents(),
      getAgentObservability(agentFilter || undefined, timeRange)
    ]).then(([agentsData, metricsData]) => {
      setAgents(agentsData.agents || [])
      setMetrics(metricsData)
      setLoading(false)
    }).catch(err => {
      console.error('Failed to load observability data:', err)
      setLoading(false)
    })
  }, [agentFilter, timeRange])

  return (
    <div className="space-y-8">
      <PageHeader 
        title="Agent Observability" 
        subtitle="Comprehensive monitoring, tracing, and evaluation of agent performance."
      />

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="flex gap-4">
          <select
            value={agentFilter || ''}
            onChange={(e) => {
              const params = new URLSearchParams(searchParams)
              if (e.target.value) {
                params.set('agent', e.target.value)
              } else {
                params.delete('agent')
              }
              window.location.search = params.toString()
            }}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-300"
          >
            <option value="">All Agents</option>
            {agents.map(agent => (
              <option key={agent.agent_id} value={agent.agent_id}>
                {agent.name}
              </option>
            ))}
          </select>

          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-300"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </GlassCard>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse text-blue-400">Loading observability data...</div>
        </div>
      ) : (
        <>
          {/* Response Time Chart */}
          <GlassCard className="p-6">
            <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Response Time Trend</div>
            <div className="h-64">
              {metrics?.response_time ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metrics.response_time}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" label={{ value: 'ms', angle: -90, position: 'insideLeft' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                    <Line type="monotone" dataKey="avg_ms" stroke="#3b82f6" strokeWidth={2} name="Avg Response Time" />
                    <Line type="monotone" dataKey="p95_ms" stroke="#8b5cf6" strokeWidth={2} name="P95 Response Time" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  No response time data available
                </div>
              )}
            </div>
          </GlassCard>

          {/* Token Usage Chart */}
          <GlassCard className="p-6">
            <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Token Usage</div>
            <div className="h-64">
              {metrics?.token_usage ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.token_usage}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="agent_id" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                    <Bar dataKey="tokens" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  No token usage data available
                </div>
              )}
            </div>
          </GlassCard>

          {/* Evaluation Scores */}
          <GlassCard className="p-6">
            <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Evaluation Scores</div>
            <div className="h-64">
              {metrics?.evaluation_scores ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metrics.evaluation_scores}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis domain={[0, 1]} stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                    <Line type="monotone" dataKey="groundedness" stroke="#10b981" strokeWidth={2} name="Groundedness" />
                    <Line type="monotone" dataKey="task_adherence" stroke="#3b82f6" strokeWidth={2} name="Task Adherence" />
                    <Line type="monotone" dataKey="tool_accuracy" stroke="#f59e0b" strokeWidth={2} name="Tool Accuracy" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  No evaluation data available
                </div>
              )}
            </div>
          </GlassCard>

          {/* Metrics Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Avg Response Time</div>
              <div className="text-3xl font-bold text-white">
                {metrics?.summary?.avg_response_time_ms ? `${metrics.summary.avg_response_time_ms.toFixed(0)}ms` : 'N/A'}
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Total Tokens</div>
              <div className="text-3xl font-bold text-white">
                {metrics?.summary?.total_tokens ? metrics.summary.total_tokens.toLocaleString() : 'N/A'}
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Avg Groundedness</div>
              <div className="text-3xl font-bold text-white">
                {metrics?.summary?.avg_groundedness ? `${(metrics.summary.avg_groundedness * 100).toFixed(0)}%` : 'N/A'}
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Tool Calls</div>
              <div className="text-3xl font-bold text-white">
                {metrics?.summary?.total_tool_calls ? metrics.summary.total_tool_calls.toLocaleString() : 'N/A'}
              </div>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  )
}

