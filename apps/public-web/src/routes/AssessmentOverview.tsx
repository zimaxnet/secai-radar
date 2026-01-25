import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getSummary, getDomains, getGaps } from '../api'
import PageHeader from '../components/ui/PageHeader'
import GlassCard from '../components/ui/GlassCard'

interface Props { tenantId: string }

export default function AssessmentOverview({ tenantId }: Props) {
  const [summary, setSummary] = useState<any>(null)
  const [gaps, setGaps] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)

    Promise.all([
      getSummary(tenantId),
      getDomains(),
      getGaps(tenantId)
    ]).then(([summaryData, , gapsData]) => {
      if (!mounted) return
      setSummary(summaryData)
      setGaps(gapsData)
    }).finally(() => {
      if (mounted) setLoading(false)
    })

    return () => { mounted = false }
  }, [tenantId])

  if (loading) {
    return <div className="flex items-center justify-center py-20 text-blue-400 animate-pulse">Loading assessment overview...</div>
  }

  const totalControls = summary?.byDomain?.reduce((sum: number, d: any) => sum + (d.total || 0), 0) || 0
  const completeControls = summary?.byDomain?.reduce((sum: number, d: any) => sum + (d.complete || 0), 0) || 0
  const inProgressControls = summary?.byDomain?.reduce((sum: number, d: any) => sum + (d.inProgress || 0), 0) || 0
  const progressPercent = totalControls > 0 ? (completeControls / totalControls) * 100 : 0
  const totalGaps = gaps?.items?.length || 0
  const domainsWithData = summary?.byDomain?.filter((d: any) => (d.total || 0) > 0) || []
  const completeDomains = summary?.byDomain?.filter((d: any) => d.total > 0 && d.complete === d.total).length || 0

  let assessmentStatus = 'not_started'
  if (progressPercent === 100) assessmentStatus = 'complete'
  else if (progressPercent > 0) assessmentStatus = 'in_progress'

  const getNextAction = () => {
    if (totalControls === 0) {
      return { text: 'Import controls to begin assessment', action: `/tenant/${tenantId}/controls`, label: 'Import Controls' }
    }
    const nextDomain = summary?.byDomain?.find((d: any) => d.total > 0 && d.complete < d.total)
    if (nextDomain) {
      return { text: `Continue with ${nextDomain.domain} domain`, action: `/tenant/${tenantId}/domain/${nextDomain.domain}`, label: 'Continue Assessment' }
    }
    if (totalGaps > 0) {
      return { text: 'Review identified gaps', action: `/tenant/${tenantId}/gaps`, label: 'Review Gaps' }
    }
    if (progressPercent === 100) {
      return { text: 'Generate final assessment report', action: `/tenant/${tenantId}/report`, label: 'Generate Report' }
    }
    return { text: 'Assessment setup complete', action: `/tenant/${tenantId}/dashboard`, label: 'View Dashboard' }
  }

  const nextAction = getNextAction()

  return (
    <div className="space-y-8">
      <PageHeader 
        title="Assessment Overview" 
        subtitle="Track your progress across all security domains."
        action={
          <div className={`px-4 py-2 rounded-full text-sm font-semibold border ${
            assessmentStatus === 'complete' ? 'bg-green-500/20 text-green-400 border-green-500/50' :
            assessmentStatus === 'in_progress' ? 'bg-blue-500/20 text-blue-400 border-blue-500/50' :
            'bg-slate-800 text-slate-400 border-slate-700'
          }`}>
            {assessmentStatus === 'complete' ? 'Assessment Complete' :
             assessmentStatus === 'in_progress' ? 'In Progress' :
             'Not Started'}
          </div>
        }
      />

      {/* Progress Bar */}
      <GlassCard className="p-8 bg-gradient-to-r from-blue-900/40 to-slate-900/40 border-blue-500/30">
        <div className="flex justify-between items-end mb-4">
          <div>
            <div className="text-sm text-blue-400 uppercase tracking-wider font-medium mb-1">Overall Completion</div>
            <div className="text-3xl font-bold text-white">{Math.round(progressPercent)}%</div>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">{completeControls} of {totalControls} Controls</div>
          </div>
        </div>
        <div className="w-full bg-slate-800/50 h-4 rounded-full overflow-hidden border border-white/5">
          <div
            className="bg-gradient-to-r from-blue-600 to-cyan-400 h-full rounded-full shadow-[0_0_15px_rgba(56,189,248,0.6)] transition-all duration-1000 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </GlassCard>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="p-6 flex flex-col items-center justify-center text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider mb-2">Domains Active</div>
          <div className="text-4xl font-bold text-white mb-1">{completeDomains} <span className="text-slate-600 text-2xl">/ {domainsWithData.length}</span></div>
          <div className="text-xs text-green-400">Fully Compliant</div>
        </GlassCard>
        
        <GlassCard className="p-6 flex flex-col items-center justify-center text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider mb-2">Risk Exposure</div>
          <div className="text-4xl font-bold text-white mb-1">{totalGaps}</div>
          <div className="text-xs text-red-400">Identified Gaps</div>
        </GlassCard>

        <GlassCard className="p-6 flex flex-col items-center justify-center text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider mb-2">Current Status</div>
          <div className="text-4xl font-bold text-white mb-1">
            {inProgressControls > 0 ? 'Active' : completeControls > 0 ? 'Stable' : 'Idle'}
          </div>
          <div className="text-xs text-blue-400">
            {inProgressControls} Controls In Progress
          </div>
        </GlassCard>
      </div>

      {/* Next Action */}
      {nextAction && (
        <GlassCard className="p-8 flex flex-col md:flex-row items-center justify-between gap-6 border-blue-500/30 bg-blue-900/10">
          <div>
            <div className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-1">Recommended Next Step</div>
            <div className="text-xl text-white font-medium">{nextAction.text}</div>
          </div>
          <Link
            to={nextAction.action}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-semibold shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all transform hover:scale-105"
          >
            {nextAction.label} →
          </Link>
        </GlassCard>
      )}

      {/* Domain Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4 px-2">Domain Breakdown</h2>
        
        {domainsWithData.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-slate-700 rounded-xl">
            <div className="text-4xl mb-4 opacity-50">📋</div>
            <p className="text-slate-400 mb-4">No controls imported yet.</p>
            <Link to={`/tenant/${tenantId}/controls`} className="text-blue-400 hover:text-blue-300 font-medium">
              Import controls to begin →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {summary?.byDomain?.map((domain: any) => {
              const domainProgress = domain.total > 0 ? (domain.complete / domain.total) * 100 : 0
              const isComplete = domain.total > 0 && domain.complete === domain.total
              
              return (
                <Link key={domain.domain} to={`/tenant/${tenantId}/domain/${domain.domain}`}>
                  <GlassCard hoverEffect className="p-5 group">
                    <div className="flex justify-between items-start mb-4">
                      <div className="h-10 w-10 rounded bg-slate-800 flex items-center justify-center font-bold text-slate-300 group-hover:text-white group-hover:bg-blue-600 transition-all">
                        {domain.domain}
                      </div>
                      {isComplete && <span className="text-green-400">✓</span>}
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-slate-400">
                        <span>Completion</span>
                        <span>{Math.round(domainProgress)}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${isComplete ? 'bg-green-500' : 'bg-blue-500'}`}
                          style={{ width: `${domainProgress}%` }}
                        />
                      </div>
                    </div>
                  </GlassCard>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
