import { useState, useEffect } from 'react'
import { postTools, getToolsInventory, isDemoMode } from '../api'
import { CAPABILITIES } from '../demoData'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

interface Props { tenantId: string }

interface Tool {
  id: string
  name: string
  vendor: string
  capabilities: string[]
  enabled: boolean
  configScore: number
}

export default function Tools({ tenantId }: Props) {
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [vendorToolId, setVendorToolId] = useState('')
  const [enabled, setEnabled] = useState(true)
  const [configScore, setConfigScore] = useState(0.8)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)
  const [saving, setSaving] = useState(false)
  const [activeView, setActiveView] = useState<'grid' | 'matrix'>('grid')

  useEffect(() => {
    loadTools()
  }, [tenantId])

  const loadTools = async () => {
    setLoading(true)
    try {
      const data = await getToolsInventory(tenantId)
      setTools(data.tools || [])
    } catch (err) {
      console.error('Failed to load tools:', err)
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    if (!vendorToolId.trim()) {
      setMessage({ text: 'Vendor Tool ID is required', type: 'error' })
      return
    }
    
    setMessage(null)
    setSaving(true)
    
    try {
      await postTools(tenantId, { vendorToolId, Enabled: enabled, ConfigScore: configScore })
      setMessage({ text: 'Tool configuration saved successfully', type: 'success' })
      setVendorToolId('')
      setEnabled(true)
      setConfigScore(0.8)
      setShowAddForm(false)
      loadTools()
    } catch (err) {
      setMessage({ text: 'Failed to save tool configuration', type: 'error' })
    } finally {
      setSaving(false)
    }
  }

  // Calculate capability coverage
  const capabilityCoverage = CAPABILITIES.map(cap => {
    const coveringTools = tools.filter(t => t.enabled && t.capabilities.includes(cap.id))
    const avgScore = coveringTools.length > 0 
      ? coveringTools.reduce((sum, t) => sum + t.configScore, 0) / coveringTools.length 
      : 0
    return {
      capability: cap.name,
      id: cap.id,
      coverage: coveringTools.length,
      avgScore: avgScore * 100,
      tools: coveringTools.map(t => t.name)
    }
  }).filter(c => c.coverage > 0)

  // Vendor summary
  const vendorSummary = tools.reduce((acc: Record<string, { count: number; enabled: number; avgScore: number }>, tool) => {
    if (!acc[tool.vendor]) {
      acc[tool.vendor] = { count: 0, enabled: 0, avgScore: 0 }
    }
    acc[tool.vendor].count++
    if (tool.enabled) {
      acc[tool.vendor].enabled++
      acc[tool.vendor].avgScore += tool.configScore
    }
    return acc
  }, {})

  Object.keys(vendorSummary).forEach(vendor => {
    if (vendorSummary[vendor].enabled > 0) {
      vendorSummary[vendor].avgScore /= vendorSummary[vendor].enabled
    }
  })

  const vendorData = Object.entries(vendorSummary).map(([vendor, data]) => ({
    vendor,
    tools: data.count,
    enabled: data.enabled,
    avgScore: Math.round(data.avgScore * 100)
  }))

  // Radar chart data for selected tool
  const getToolRadarData = (tool: Tool) => {
    return tool.capabilities.map(capId => ({
      capability: CAPABILITIES.find(c => c.id === capId)?.name || capId,
      strength: tool.configScore * 100
    }))
  }

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Security Tools Inventory" 
        subtitle="Manage and monitor your security tool stack coverage"
        action={
          <div className="flex items-center gap-3">
            {isDemoMode() && (
              <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-medium border border-yellow-500/30">
                Demo Mode
              </span>
            )}
            <div className="flex gap-1 bg-slate-900/50 p-1 rounded-lg border border-white/5">
              <button
                onClick={() => setActiveView('grid')}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                  activeView === 'grid' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Grid
              </button>
              <button
                onClick={() => setActiveView('matrix')}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                  activeView === 'matrix' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Matrix
              </button>
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Tool
            </button>
          </div>
        }
      />

      {message && (
        <div className={`p-4 rounded-xl border ${
          message.type === 'success' 
            ? 'bg-green-500/10 border-green-500/30 text-green-400' 
            : 'bg-red-500/10 border-red-500/30 text-red-400'
        }`}>
          {message.text}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Total Tools</div>
          <div className="text-4xl font-bold text-white">{tools.length}</div>
        </GlassCard>
        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Active</div>
          <div className="text-4xl font-bold text-green-400">{tools.filter(t => t.enabled).length}</div>
        </GlassCard>
        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Vendors</div>
          <div className="text-4xl font-bold text-blue-400">{Object.keys(vendorSummary).length}</div>
        </GlassCard>
        <GlassCard className="p-6">
          <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Avg Config Score</div>
          <div className="text-4xl font-bold text-cyan-400">
            {Math.round(tools.filter(t => t.enabled).reduce((sum, t) => sum + t.configScore, 0) / Math.max(tools.filter(t => t.enabled).length, 1) * 100)}%
          </div>
        </GlassCard>
      </div>

      {/* Add Tool Form */}
      {showAddForm && (
        <GlassCard className="p-6">
          <h3 className="text-slate-300 font-semibold mb-4">Add Tool Configuration</h3>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">
                Vendor Tool ID <span className="text-red-500">*</span>
              </label>
              <select
                className="w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                value={vendorToolId}
                onChange={e => setVendorToolId(e.target.value)}
              >
                <option value="">Select a tool...</option>
                {tools.filter(t => !t.enabled).map(t => (
                  <option key={t.id} value={t.id}>{t.name} ({t.vendor})</option>
                ))}
                <option value="custom">Custom Tool ID...</option>
              </select>
              {vendorToolId === 'custom' && (
                <input
                  className="mt-2 w-full px-4 py-3 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                  placeholder="Enter custom tool ID"
                  onChange={e => setVendorToolId(e.target.value)}
                />
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">
                Configuration Score
              </label>
              <div className="space-y-2">
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={configScore}
                  onChange={e => setConfigScore(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between text-xs text-slate-500">
                  <span>0%</span>
                  <span className="text-lg font-bold text-white">{Math.round(configScore * 100)}%</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
            <div className="flex items-end gap-4">
              <label className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors flex-1">
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={e => setEnabled(e.target.checked)}
                  className="rounded bg-slate-700 border-slate-600 text-blue-500"
                />
                <span className="text-slate-300 text-sm">Enabled</span>
              </label>
              <button
                onClick={submit}
                disabled={saving || !vendorToolId.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </GlassCard>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* Grid View */}
          {activeView === 'grid' && (
            <div className="grid grid-cols-12 gap-6">
              {/* Tools Grid */}
              <div className="col-span-8">
                <div className="grid grid-cols-3 gap-4">
                  {tools.map(tool => (
                    <GlassCard 
                      key={tool.id}
                      hoverEffect
                      className={`p-5 cursor-pointer transition-all ${
                        selectedTool?.id === tool.id ? 'ring-2 ring-blue-500' : ''
                      } ${!tool.enabled ? 'opacity-50' : ''}`}
                      onClick={() => setSelectedTool(tool)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                          <span className="text-lg font-bold text-blue-400">{tool.name.charAt(0)}</span>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          tool.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-400'
                        }`}>
                          {tool.enabled ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <h4 className="font-semibold text-white mb-1 truncate">{tool.name}</h4>
                      <p className="text-sm text-slate-500 mb-3">{tool.vendor}</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${
                              tool.configScore >= 0.8 ? 'bg-green-500' : 
                              tool.configScore >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${tool.configScore * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400">{Math.round(tool.configScore * 100)}%</span>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-1">
                        {tool.capabilities.slice(0, 3).map(cap => (
                          <span key={cap} className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-400">
                            {CAPABILITIES.find(c => c.id === cap)?.name || cap}
                          </span>
                        ))}
                        {tool.capabilities.length > 3 && (
                          <span className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-400">
                            +{tool.capabilities.length - 3}
                          </span>
                        )}
                      </div>
                    </GlassCard>
                  ))}
                </div>
              </div>

              {/* Tool Detail / Charts */}
              <div className="col-span-4 space-y-4">
                {selectedTool ? (
                  <GlassCard className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                        <span className="text-xl font-bold text-blue-400">{selectedTool.name.charAt(0)}</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-white">{selectedTool.name}</h3>
                        <p className="text-sm text-slate-500">{selectedTool.vendor}</p>
                      </div>
                    </div>
                    <div className="h-[200px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={getToolRadarData(selectedTool)}>
                          <PolarGrid stroke="#334155" />
                          <PolarAngleAxis dataKey="capability" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                          <Radar name="Strength" dataKey="strength" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-4 space-y-2">
                      <h4 className="text-sm font-medium text-slate-400">Capabilities</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedTool.capabilities.map(cap => (
                          <span key={cap} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">
                            {CAPABILITIES.find(c => c.id === cap)?.name || cap}
                          </span>
                        ))}
                      </div>
                    </div>
                  </GlassCard>
                ) : (
                  <GlassCard className="p-6">
                    <h3 className="font-semibold text-slate-300 mb-4">Vendor Distribution</h3>
                    <div className="h-[250px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={vendorData} layout="vertical">
                          <XAxis type="number" stroke="#64748b" />
                          <YAxis type="category" dataKey="vendor" stroke="#64748b" width={80} tick={{ fontSize: 10 }} />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                            labelStyle={{ color: '#f1f5f9' }}
                          />
                          <Bar dataKey="enabled" fill="#3b82f6" name="Active Tools" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </GlassCard>
                )}

                <GlassCard className="p-6">
                  <h3 className="font-semibold text-slate-300 mb-4">Top Capabilities Covered</h3>
                  <div className="space-y-3">
                    {capabilityCoverage.slice(0, 8).map(cap => (
                      <div key={cap.id} className="flex items-center gap-3">
                        <span className="text-xs text-slate-400 w-24 truncate">{cap.capability}</span>
                        <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                            style={{ width: `${cap.avgScore}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-400 w-8">{cap.coverage}</span>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </div>
            </div>
          )}

          {/* Matrix View */}
          {activeView === 'matrix' && (
            <GlassCard className="p-6 overflow-x-auto">
              <h3 className="font-semibold text-slate-300 mb-4">Tool-Capability Coverage Matrix</h3>
              <table className="w-full min-w-[800px]">
                <thead>
                  <tr>
                    <th className="text-left py-2 px-3 text-slate-400 font-medium text-xs sticky left-0 bg-slate-900/95">Tool</th>
                    {CAPABILITIES.filter(c => tools.some(t => t.capabilities.includes(c.id))).map(cap => (
                      <th key={cap.id} className="py-2 px-2 text-slate-400 font-medium text-xs text-center" style={{ minWidth: '50px' }}>
                        <div className="transform -rotate-45 origin-center whitespace-nowrap text-[10px]">
                          {cap.name}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tools.filter(t => t.enabled).map(tool => (
                    <tr key={tool.id} className="border-t border-white/5 hover:bg-white/5">
                      <td className="py-2 px-3 text-sm text-slate-200 sticky left-0 bg-slate-900/95">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{tool.name}</span>
                          <span className="text-xs text-slate-500">({Math.round(tool.configScore * 100)}%)</span>
                        </div>
                      </td>
                      {CAPABILITIES.filter(c => tools.some(t => t.capabilities.includes(c.id))).map(cap => (
                        <td key={cap.id} className="py-2 px-2 text-center">
                          {tool.capabilities.includes(cap.id) ? (
                            <div 
                              className="h-6 w-6 mx-auto rounded flex items-center justify-center"
                              style={{ 
                                backgroundColor: `rgba(59, 130, 246, ${tool.configScore})`,
                                border: '1px solid rgba(59, 130, 246, 0.3)'
                              }}
                              title={`${tool.name} - ${cap.name}: ${Math.round(tool.configScore * 100)}%`}
                            >
                              <span className="text-[10px] text-white font-medium">{Math.round(tool.configScore * 100)}</span>
                            </div>
                          ) : (
                            <div className="h-6 w-6 mx-auto rounded bg-slate-800/50" />
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-4 flex items-center gap-4 text-xs text-slate-500">
                <span>Legend:</span>
                <div className="flex items-center gap-1">
                  <div className="h-4 w-4 rounded" style={{ backgroundColor: 'rgba(59, 130, 246, 0.3)' }} />
                  <span>Low (30%)</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-4 w-4 rounded" style={{ backgroundColor: 'rgba(59, 130, 246, 0.6)' }} />
                  <span>Medium (60%)</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-4 w-4 rounded" style={{ backgroundColor: 'rgba(59, 130, 246, 0.9)' }} />
                  <span>High (90%)</span>
                </div>
              </div>
            </GlassCard>
          )}
        </>
      )}
    </div>
  )
}
