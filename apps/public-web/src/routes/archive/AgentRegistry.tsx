import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAgents, quarantineAgent, unquarantineAgent } from '../api'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'

interface Props { tenantId: string }

interface Agent {
  agent_id: string
  entra_agent_id?: string | null
  name: string
  role: string
  status: string
  blueprint: string
  capabilities: string[]
  collections: string[]
  last_active_at: string | null
  created_at?: string
}

export default function AgentRegistry({ tenantId }: Props) {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ status?: string; collection?: string }>({})

  useEffect(() => {
    loadAgents()
    
    // Poll for updates
    const interval = setInterval(loadAgents, 30000)
    return () => clearInterval(interval)
  }, [filter])

  const loadAgents = () => {
    getAgents(filter).then(data => {
      setAgents(data.agents || [])
      setLoading(false)
    }).catch(err => {
      console.error('Failed to load agents:', err)
      setLoading(false)
    })
  }

  const handleQuarantine = async (agentId: string, quarantine: boolean) => {
    try {
      if (quarantine) {
        await quarantineAgent(agentId)
      } else {
        await unquarantineAgent(agentId)
      }
      loadAgents()
    } catch (err) {
      console.error('Failed to quarantine/unquarantine:', err)
    }
  }

  const statusColors: Record<string, string> = {
    active: 'bg-green-500/20 text-green-400 border-green-500/30',
    idle: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    quarantined: 'bg-red-500/20 text-red-400 border-red-500/30',
    disabled: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    error: 'bg-orange-500/20 text-orange-400 border-orange-500/30'
  }

  return (
    <div className="space-y-8">
      <PageHeader 
        title="Agent Registry" 
        subtitle="Centralized inventory and management of all AI agents."
      />

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="flex gap-4">
          <select
            value={filter.status || ''}
            onChange={(e) => setFilter({ ...filter, status: e.target.value || undefined })}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-300"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="idle">Idle</option>
            <option value="quarantined">Quarantined</option>
            <option value="disabled">Disabled</option>
            <option value="error">Error</option>
          </select>

          <select
            value={filter.collection || ''}
            onChange={(e) => setFilter({ ...filter, collection: e.target.value || undefined })}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-300"
          >
            <option value="">All Collections</option>
            <option value="secai-core">SecAI Core</option>
            <option value="quarantine">Quarantine</option>
            <option value="assessment-agents">Assessment Agents</option>
          </select>
        </div>
      </GlassCard>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse text-blue-400">Loading agents...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <Link key={agent.agent_id} to={`/tenant/${tenantId}/agent/${agent.agent_id}`}>
              <GlassCard hoverEffect className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="text-lg font-bold text-white mb-1">{agent.name}</div>
                    <div className="text-sm text-slate-400">{agent.role}</div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${statusColors[agent.status] || statusColors.disabled}`}>
                    {agent.status}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="text-xs text-slate-500">
                    <span className="font-medium">Blueprint:</span> {agent.blueprint}
                  </div>
                  <div className="text-xs text-slate-500">
                    <span className="font-medium">Capabilities:</span> {agent.capabilities.length}
                  </div>
                  <div className="text-xs text-slate-500">
                    <span className="font-medium">Collections:</span> {agent.collections.join(', ')}
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-slate-700">
                  {agent.status === 'quarantined' ? (
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        handleQuarantine(agent.agent_id, false)
                      }}
                      className="flex-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded text-xs font-medium transition-colors"
                    >
                      Unquarantine
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        handleQuarantine(agent.agent_id, true)
                      }}
                      className="flex-1 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium transition-colors"
                    >
                      Quarantine
                    </button>
                  )}
                  <span
                    onClick={(e) => {
                      e.preventDefault()
                      window.location.href = `/tenant/${tenantId}/agent/${agent.agent_id}`
                    }}
                    className="flex-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium text-center transition-colors cursor-pointer"
                  >
                    View Details
                  </span>
                </div>
              </GlassCard>
            </Link>
          ))}
        </div>
      )}

      {!loading && agents.length === 0 && (
        <GlassCard className="p-12 text-center">
          <div className="text-slate-400">No agents found matching the filters.</div>
        </GlassCard>
      )}
    </div>
  )
}

