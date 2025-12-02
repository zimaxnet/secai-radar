import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getReport, generateVisualization, craftVisualizationPrompt, isDemoMode } from '../api'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'

interface Props { tenantId: string }

export default function Report({ tenantId }: Props) {
  const [report, setReport] = useState<any>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [includeAI, setIncludeAI] = useState(true)
  const [activeTab, setActiveTab] = useState<'summary' | 'gaps' | 'export'>('summary')
  const [visualPrompt, setVisualPrompt] = useState('')
  const [generatingVisual, setGeneratingVisual] = useState(false)
  const [visualResult, setVisualResult] = useState<any>(null)
  const [craftingPrompt, setCraftingPrompt] = useState(false)
  const [craftedPromptData, setCraftedPromptData] = useState<any>(null)
  const [visualStyle, setVisualStyle] = useState<'diagram' | 'infographic' | 'chart' | 'architecture'>('infographic')
  const [useAgentCrafting, setUseAgentCrafting] = useState(true)

  // Auto-load report on mount
  useEffect(() => {
    generateReport()
  }, [tenantId])

  const generateReport = async () => {
    setGenerating(true)
    setError(null)
    try {
      const data = await getReport(tenantId, includeAI)
      setReport(data)
    } catch (err: any) {
      setError(err.message || 'Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  // Craft visualization prompt using Elena Bridges agent
  const handleCraftPrompt = async () => {
    if (!visualPrompt.trim()) return
    setCraftingPrompt(true)
    setCraftedPromptData(null)
    try {
      const result = await craftVisualizationPrompt(visualPrompt, {
        style: visualStyle,
        contextType: 'assessment',
        assessmentData: report
      })
      setCraftedPromptData(result)
    } catch (err: any) {
      console.error('Error crafting prompt:', err)
    } finally {
      setCraftingPrompt(false)
    }
  }

  const handleGenerateVisual = async () => {
    if (!visualPrompt.trim()) return
    setGeneratingVisual(true)
    setVisualResult(null)
    
    try {
      let promptToUse = visualPrompt
      
      // Use agent-crafted prompt if enabled
      if (useAgentCrafting) {
        const craftedResult = await craftVisualizationPrompt(visualPrompt, {
          style: visualStyle,
          contextType: 'assessment',
          assessmentData: report
        })
        if (craftedResult?.crafted_prompt) {
          promptToUse = craftedResult.crafted_prompt
          setCraftedPromptData(craftedResult)
        }
      }
      
      const result = await generateVisualization(promptToUse, { style: visualStyle })
      setVisualResult(result)
    } catch (err: any) {
      setVisualResult({ success: false, error: err.message })
    } finally {
      setGeneratingVisual(false)
    }
  }

  const downloadReport = () => {
    if (!report) return
    
    const reportText = `
SecAI Framework Assessment Report
${tenantId}
Generated: ${new Date().toISOString()}

${report.executiveSummary ? `EXECUTIVE SUMMARY\n${report.executiveSummary}\n\n` : ''}

ASSESSMENT SUMMARY
Total Controls: ${report.summary?.totalControls || 0}
Controls with Gaps: ${report.summary?.totalGaps || 0}
Critical Gaps: ${report.summary?.criticalGaps || 0}

DOMAIN BREAKDOWN
${report.summary?.byDomain?.map((d: any) => 
  `${d.domain}: ${d.complete}/${d.total} complete (${Math.round((d.complete / d.total) * 100)}%)`
).join('\n') || 'No data'}

GAPS IDENTIFIED
${report.gaps?.map((g: any) => 
  `${g.ControlID}: ${(g.Coverage * 100).toFixed(0)}% coverage - ${g.HardGaps?.length || 0} hard gaps, ${g.SoftGaps?.length || 0} soft gaps`
).join('\n') || 'No gaps identified'}
    `.trim()

    const blob = new Blob([reportText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `secai-assessment-${tenantId}-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Chart colors
  const STATUS_COLORS = { complete: '#10b981', inProgress: '#f59e0b', notStarted: '#ef4444' }

  // Prepare chart data
  const statusData = report?.summary?.byDomain ? [
    { name: 'Complete', value: report.summary.byDomain.reduce((sum: number, d: any) => sum + d.complete, 0), color: STATUS_COLORS.complete },
    { name: 'In Progress', value: report.summary.byDomain.reduce((sum: number, d: any) => sum + d.inProgress, 0), color: STATUS_COLORS.inProgress },
    { name: 'Not Started', value: report.summary.byDomain.reduce((sum: number, d: any) => sum + d.notStarted, 0), color: STATUS_COLORS.notStarted }
  ] : []

  const domainBarData = report?.summary?.byDomain?.map((d: any) => ({
    domain: d.domain,
    complete: d.complete,
    inProgress: d.inProgress,
    notStarted: d.notStarted,
    total: d.total
  })) || []

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Assessment Report" 
        subtitle={`Comprehensive security assessment for ${tenantId}`}
        action={
          <div className="flex items-center gap-3">
            {isDemoMode() && (
              <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-medium border border-yellow-500/30">
                Demo Mode
              </span>
            )}
            <button
              onClick={generateReport}
              disabled={generating}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-600/50 transition-colors flex items-center gap-2"
            >
              {generating ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh Report
                </>
              )}
            </button>
          </div>
        }
      />

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex gap-1 bg-slate-900/50 p-1 rounded-lg border border-white/5 w-fit">
        {(['summary', 'gaps', 'export'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' 
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {generating ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <div className="h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 animate-pulse">Analyzing security posture...</p>
        </div>
      ) : report && (
        <>
          {/* Summary Tab */}
          {activeTab === 'summary' && (
            <div className="grid grid-cols-12 gap-6">
              {/* KPI Cards */}
              <div className="col-span-12 grid grid-cols-4 gap-4">
                <GlassCard className="p-6">
                  <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Total Controls</div>
                  <div className="text-4xl font-bold text-white">{report.summary?.totalControls || 0}</div>
                </GlassCard>
                <GlassCard className="p-6">
                  <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">With Gaps</div>
                  <div className="text-4xl font-bold text-orange-400">{report.summary?.totalGaps || 0}</div>
                </GlassCard>
                <GlassCard className="p-6">
                  <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Critical Gaps</div>
                  <div className="text-4xl font-bold text-red-400">{report.summary?.criticalGaps || 0}</div>
                </GlassCard>
                <GlassCard className="p-6">
                  <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">Compliance Rate</div>
                  <div className="text-4xl font-bold text-green-400">
                    {report.summary?.totalControls 
                      ? Math.round(((report.summary.totalControls - report.summary.totalGaps) / report.summary.totalControls) * 100)
                      : 0}%
                  </div>
                </GlassCard>
              </div>

              {/* Charts Row */}
              <div className="col-span-5">
                <GlassCard className="p-6 h-[350px]">
                  <h3 className="text-slate-300 font-semibold mb-4">Control Status Distribution</h3>
                  <ResponsiveContainer width="100%" height="85%">
                    <PieChart>
                      <Pie
                        data={statusData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(Number(percent || 0) * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {statusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        labelStyle={{ color: '#f1f5f9' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </GlassCard>
              </div>

              <div className="col-span-7">
                <GlassCard className="p-6 h-[350px]">
                  <h3 className="text-slate-300 font-semibold mb-4">Coverage by Domain</h3>
                  <ResponsiveContainer width="100%" height="85%">
                    <BarChart data={domainBarData} layout="vertical">
                      <XAxis type="number" stroke="#64748b" />
                      <YAxis type="category" dataKey="domain" stroke="#64748b" width={60} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        labelStyle={{ color: '#f1f5f9' }}
                      />
                      <Legend />
                      <Bar dataKey="complete" stackId="a" fill={STATUS_COLORS.complete} name="Complete" />
                      <Bar dataKey="inProgress" stackId="a" fill={STATUS_COLORS.inProgress} name="In Progress" />
                      <Bar dataKey="notStarted" stackId="a" fill={STATUS_COLORS.notStarted} name="Not Started" />
                    </BarChart>
                  </ResponsiveContainer>
                </GlassCard>
              </div>

              {/* Executive Summary */}
              {report.executiveSummary && (
                <div className="col-span-12">
                  <GlassCard className="p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                      <h3 className="text-slate-300 font-semibold">AI-Generated Executive Summary</h3>
                    </div>
                    <div className="prose prose-invert prose-sm max-w-none">
                      <div className="whitespace-pre-wrap text-slate-300 leading-relaxed" 
                           dangerouslySetInnerHTML={{ __html: report.executiveSummary.replace(/##\s*(.*)/g, '<h3 class="text-lg font-semibold text-white mt-4 mb-2">$1</h3>').replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>') }} />
                    </div>
                  </GlassCard>
                </div>
              )}
            </div>
          )}

          {/* Gaps Tab */}
          {activeTab === 'gaps' && (
            <div className="space-y-4">
              <GlassCard className="p-6">
                <h3 className="text-slate-300 font-semibold mb-4">Controls with Gaps ({report.gaps?.length || 0})</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-slate-400 font-medium text-sm">Control ID</th>
                        <th className="text-left py-3 px-4 text-slate-400 font-medium text-sm">Title</th>
                        <th className="text-left py-3 px-4 text-slate-400 font-medium text-sm">Domain</th>
                        <th className="text-center py-3 px-4 text-slate-400 font-medium text-sm">Coverage</th>
                        <th className="text-center py-3 px-4 text-slate-400 font-medium text-sm">Hard Gaps</th>
                        <th className="text-center py-3 px-4 text-slate-400 font-medium text-sm">Soft Gaps</th>
                        <th className="text-center py-3 px-4 text-slate-400 font-medium text-sm">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.gaps?.map((gap: any, idx: number) => (
                        <tr key={gap.ControlID || idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                          <td className="py-3 px-4 font-mono text-blue-400 text-sm">{gap.ControlID}</td>
                          <td className="py-3 px-4 text-slate-200 text-sm max-w-xs truncate">{gap.ControlTitle}</td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">{gap.DomainPartition || gap.Domain}</span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <div className="flex items-center justify-center gap-2">
                              <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full ${gap.Coverage >= 0.7 ? 'bg-green-500' : gap.Coverage >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                  style={{ width: `${gap.Coverage * 100}%` }}
                                />
                              </div>
                              <span className="text-xs text-slate-400">{(gap.Coverage * 100).toFixed(0)}%</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-center">
                            {gap.HardGaps?.length > 0 && (
                              <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">{gap.HardGaps.length}</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {gap.SoftGaps?.length > 0 && (
                              <span className="px-2 py-1 bg-orange-500/20 text-orange-400 rounded text-xs">{gap.SoftGaps.length}</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <Link 
                              to={`/tenant/${tenantId}/gaps`}
                              className="text-blue-400 hover:text-blue-300 text-sm"
                            >
                              View →
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </GlassCard>
            </div>
          )}

          {/* Export Tab */}
          {activeTab === 'export' && (
            <div className="grid grid-cols-2 gap-6">
              <GlassCard className="p-6">
                <h3 className="text-slate-300 font-semibold mb-4">Export Options</h3>
                <div className="space-y-4">
                  <label className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors">
                    <input
                      type="checkbox"
                      checked={includeAI}
                      onChange={e => setIncludeAI(e.target.checked)}
                      className="rounded bg-slate-700 border-slate-600 text-blue-500"
                    />
                    <span className="text-slate-300 text-sm">Include AI-generated executive summary</span>
                  </label>
                  
                  <div className="flex gap-3 pt-4">
                    <button
                      onClick={downloadReport}
                      className="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download TXT
                    </button>
                    <button
                      onClick={() => {
                        const json = JSON.stringify(report, null, 2)
                        const blob = new Blob([json], { type: 'application/json' })
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.href = url
                        a.download = `secai-assessment-${tenantId}-${new Date().toISOString().split('T')[0]}.json`
                        document.body.appendChild(a)
                        a.click()
                        document.body.removeChild(a)
                        URL.revokeObjectURL(url)
                      }}
                      className="flex-1 px-4 py-3 bg-slate-700 text-white rounded-lg font-medium hover:bg-slate-600 transition-colors flex items-center justify-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                      Download JSON
                    </button>
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <h3 className="text-slate-300 font-semibold mb-4">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">✨ Nano Banana Pro</span>
                  <span className="text-slate-500 text-sm font-normal ml-2">Agent-Powered Visuals</span>
                </h3>
                
                {/* Agent Info Badge */}
                <div className="flex items-center gap-2 mb-4 p-2 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/20">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-sm font-bold">
                    EB
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-purple-300">Elena Bridges</div>
                    <div className="text-xs text-slate-500">Business Impact Strategist crafts your prompts</div>
                  </div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useAgentCrafting}
                      onChange={e => setUseAgentCrafting(e.target.checked)}
                      className="rounded bg-slate-700 border-slate-600 text-purple-500"
                    />
                    <span className="text-xs text-slate-400">Agent assist</span>
                  </label>
                </div>

                <p className="text-slate-500 text-sm mb-3">
                  Describe what you want to visualize. Elena will enhance your prompt with assessment context.
                </p>
                
                {/* Style Selector */}
                <div className="flex gap-2 mb-3">
                  {(['diagram', 'infographic', 'chart', 'architecture'] as const).map(style => (
                    <button
                      key={style}
                      onClick={() => setVisualStyle(style)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        visualStyle === style
                          ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                          : 'bg-slate-800/50 text-slate-400 border border-white/5 hover:bg-slate-800'
                      }`}
                    >
                      {style.charAt(0).toUpperCase() + style.slice(1)}
                    </button>
                  ))}
                </div>

                <textarea
                  value={visualPrompt}
                  onChange={e => setVisualPrompt(e.target.value)}
                  placeholder="e.g., Show our security posture across all domains with compliance rates and gap counts..."
                  className="w-full h-20 px-4 py-3 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 resize-none"
                />

                {/* Action Buttons */}
                <div className="flex gap-2 mt-3">
                  {useAgentCrafting && (
                    <button
                      onClick={handleCraftPrompt}
                      disabled={craftingPrompt || !visualPrompt.trim()}
                      className="flex-1 px-4 py-2.5 bg-slate-700 text-white rounded-lg font-medium hover:bg-slate-600 disabled:opacity-50 transition-all flex items-center justify-center gap-2 text-sm"
                    >
                      {craftingPrompt ? (
                        <>
                          <div className="h-4 w-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
                          Crafting...
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                          </svg>
                          Preview Prompt
                        </>
                      )}
                    </button>
                  )}
                  <button
                    onClick={handleGenerateVisual}
                    disabled={generatingVisual || !visualPrompt.trim()}
                    className={`${useAgentCrafting ? 'flex-1' : 'w-full'} px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2 text-sm`}
                  >
                    {generatingVisual ? (
                      <>
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        {useAgentCrafting ? 'Elena is crafting...' : 'Generating...'}
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        Generate
                      </>
                    )}
                  </button>
                </div>

                {/* Crafted Prompt Preview */}
                {craftedPromptData && (
                  <div className="mt-4 p-3 bg-purple-500/5 rounded-lg border border-purple-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <span className="text-[10px] text-purple-400">EB</span>
                      </div>
                      <span className="text-xs font-medium text-purple-300">Elena's Crafted Prompt</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed max-h-32 overflow-y-auto">
                      {craftedPromptData.crafted_prompt}
                    </p>
                  </div>
                )}

                {/* Generated Visualization */}
                {visualResult && (
                  <div className="mt-4 p-4 bg-slate-800/50 rounded-lg border border-white/10">
                    {visualResult.success && visualResult.imageData ? (
                      <>
                        <img 
                          src={`data:${visualResult.mimeType};base64,${visualResult.imageData}`}
                          alt="Generated visualization"
                          className="w-full rounded-lg"
                        />
                        {craftedPromptData && (
                          <div className="mt-2 text-xs text-slate-500 flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Crafted by {craftedPromptData.agent_role}
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-slate-400 text-sm">
                        {visualResult.error || visualResult.textResponse || 'Unable to generate image. Please try a different prompt.'}
                      </div>
                    )}
                  </div>
                )}
              </GlassCard>
            </div>
          )}
        </>
      )}
    </div>
  )
}
