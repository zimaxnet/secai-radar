import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getAgent, getAgentObservability, runEvaluation } from '../api'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props { tenantId: string }

interface Agent {
  agent_id: string
  entra_agent_id: string | null
  name: string
  role: string
  status: string
  blueprint: string
  capabilities: string[]
  collections: string[]
  last_active_at: string | null
  created_at: string
  updated_at: string
  metadata: Record<string, any>
}

export default function AgentDetail({ tenantId }: Props) {
  const { agentId } = useParams<{ agentId: string }>()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<any>(null)
  const [evaluationScores, setEvaluationScores] = useState<any>(null)

  useEffect(() => {
    if (!agentId) return

    Promise.all([
      getAgent(agentId),
      getAgentObservability(agentId, '24h')
    ]).then(([agentData, metricsData]) => {
      setAgent(agentData)
      setMetrics(metricsData)
      setLoading(false)
    }).catch(err => {
      console.error('Failed to load agent:', err)
      setLoading(false)
    })
  }, [agentId])

  const statusColors: Record<string, string> = {
    active: 'bg-green-500/20 text-green-400 border-green-500/30',
    idle: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    quarantined: 'bg-red-500/20 text-red-400 border-red-500/30',
    disabled: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    error: 'bg-orange-500/20 text-orange-400 border-orange-500/30'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse text-blue-400">Loading agent details...</div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="space-y-8">
        <PageHeader title="Agent Not Found" subtitle="The requested agent could not be found." />
        <Link to={`/tenant/${tenantId}/agents`} className="text-blue-400 hover:text-blue-300">
          ← Back to Registry
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <PageHeader 
          title={agent.name} 
          subtitle={agent.role}
        />
        <Link
          to={`/tenant/${tenantId}/agents`}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
        >
          ← Back to Registry
        </Link>
      </div>

      {/* Agent Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-6 lg:col-span-2">
          <div className="space-y-4">
            <div>
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Agent Information</div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">Agent ID:</span>
                  <span className="text-white font-mono text-sm">{agent.agent_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Entra Agent ID:</span>
                  <span className="text-white font-mono text-sm">{agent.entra_agent_id || 'Not assigned'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Blueprint:</span>
                  <span className="text-white">{agent.blueprint}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Status:</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${statusColors[agent.status] || statusColors.disabled}`}>
                    {agent.status}
                  </span>
                </div>
              </div>
            </div>

            <div>
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Capabilities</div>
              <div className="flex flex-wrap gap-2">
                {agent.capabilities.map((cap) => (
                  <span key={cap} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                    {cap}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Collections</div>
              <div className="flex flex-wrap gap-2">
                {agent.collections.map((col) => (
                  <span key={col} className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
                    {col}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Activity Timeline</div>
          <div className="space-y-3">
            <div>
              <div className="text-xs text-slate-500 mb-1">Created</div>
              <div className="text-sm text-white">
                {new Date(agent.created_at).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-xs text-slate-500 mb-1">Last Updated</div>
              <div className="text-sm text-white">
                {new Date(agent.updated_at).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-xs text-slate-500 mb-1">Last Active</div>
              <div className="text-sm text-white">
                {agent.last_active_at ? new Date(agent.last_active_at).toLocaleString() : 'Never'}
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Performance Metrics */}
      {metrics && (
        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Performance Metrics</div>
          <div className="h-64">
            {metrics.response_time ? (
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
      )}

      {/* Evaluation Scores */}
      {evaluationScores && (
        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Evaluation Scores</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(evaluationScores.scores || {}).map(([type, score]: [string, any]) => (
              <div key={type} className="text-center">
                <div className="text-3xl font-bold text-blue-400 mb-1">
                  {(score * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-400 capitalize">
                  {type.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Link to Observability */}
      <div className="flex justify-end">
        <Link
          to={`/tenant/${tenantId}/observability?agent=${agentId}`}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          View Full Observability →
        </Link>
      </div>
    </div>
  )
}

