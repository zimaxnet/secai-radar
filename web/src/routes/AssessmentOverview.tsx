import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getSummary, getDomains, getGaps } from '../api'

interface Props { tenantId: string }

export default function AssessmentOverview({ tenantId }: Props) {
  const [summary, setSummary] = useState<any>(null)
  const [domains, setDomains] = useState<any[]>([])
  const [gaps, setGaps] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)

    Promise.all([
      getSummary(tenantId),
      getDomains(),
      getGaps(tenantId)
    ]).then(([summaryData, domainsData, gapsData]) => {
      if (!mounted) return
      setSummary(summaryData)
      setDomains(domainsData || [])
      setGaps(gapsData)
    }).finally(() => {
      if (mounted) setLoading(false)
    })

    return () => { mounted = false }
  }, [tenantId])

  if (loading) {
    return <div className="text-gray-500">Loading assessment overview...</div>
  }

  const totalControls = summary?.byDomain?.reduce((sum: number, d: any) => sum + (d.total || 0), 0) || 0
  const completeControls = summary?.byDomain?.reduce((sum: number, d: any) => sum + (d.complete || 0), 0) || 0
  const inProgressControls = summary?.byDomain?.reduce((sum: number, d: any) => sum + (d.inProgress || 0), 0) || 0
  const progressPercent = totalControls > 0 ? (completeControls / totalControls) * 100 : 0
  const totalGaps = gaps?.items?.length || 0
  const domainsWithData = summary?.byDomain?.filter((d: any) => (d.total || 0) > 0) || []
  const completeDomains = summary?.byDomain?.filter((d: any) => d.total > 0 && d.complete === d.total).length || 0

  // Determine assessment status
  let assessmentStatus = 'not_started'
  if (progressPercent === 100) assessmentStatus = 'complete'
  else if (progressPercent > 0) assessmentStatus = 'in_progress'

  // Find next recommended action
  const getNextAction = () => {
    if (totalControls === 0) {
      return { text: 'Import controls to begin assessment', action: `/tenant/${tenantId}/controls`, label: 'Import Controls' }
    }
    // Find first domain with incomplete controls
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
    <div className="space-y-6">
      {/* Assessment Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg p-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <Link to="/assessments" className="text-blue-200 hover:text-white text-sm mb-2 inline-block">
              ← Back to Assessments
            </Link>
            <h1 className="text-4xl font-bold mb-2">{tenantId} Assessment</h1>
            <p className="text-blue-100">SecAI Framework Security Assessment</p>
          </div>
          <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
            assessmentStatus === 'complete' ? 'bg-green-500' :
            assessmentStatus === 'in_progress' ? 'bg-blue-500' :
            'bg-gray-500'
          }`}>
            {assessmentStatus === 'complete' ? 'Complete' :
             assessmentStatus === 'in_progress' ? 'In Progress' :
             'Not Started'}
          </span>
        </div>

        {/* Overall Progress */}
        <div className="mt-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-blue-100">Overall Progress</span>
            <span className="font-bold text-lg">{Math.round(progressPercent)}%</span>
          </div>
          <div className="w-full bg-blue-900 rounded-full h-4">
            <div
              className="bg-white rounded-full h-4 transition-all"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500 mb-1">Controls</div>
          <div className="text-2xl font-bold text-gray-900">{completeControls} / {totalControls}</div>
          <div className="text-xs text-gray-500 mt-1">complete</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500 mb-1">Domains</div>
          <div className="text-2xl font-bold text-gray-900">{completeDomains} / {domainsWithData.length}</div>
          <div className="text-xs text-gray-500 mt-1">complete</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500 mb-1">Gaps</div>
          <div className="text-2xl font-bold text-gray-900">{totalGaps}</div>
          <div className="text-xs text-gray-500 mt-1">identified</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500 mb-1">Status</div>
          <div className="text-2xl font-bold text-gray-900">
            {inProgressControls > 0 ? '⏳' : completeControls > 0 ? '✓' : '○'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {inProgressControls > 0 ? 'In Progress' : completeControls > 0 ? 'Active' : 'Not Started'}
          </div>
        </div>
      </div>

      {/* Next Action */}
      {nextAction && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-blue-900 mb-1">Recommended Next Action</div>
              <div className="text-lg text-blue-800">{nextAction.text}</div>
            </div>
            <Link
              to={nextAction.action}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              {nextAction.label} →
            </Link>
          </div>
        </div>
      )}

      {/* Domain Progress */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Security Domains</h2>
        <p className="text-sm text-gray-600 mb-6">
          Work through each security domain to complete your assessment. Click a domain to view controls, 
          enter observations, and track progress.
        </p>
        
        {domainsWithData.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📋</div>
            <p className="text-gray-600 mb-4">No controls imported yet.</p>
            <Link
              to={`/tenant/${tenantId}/controls`}
              className="text-blue-600 hover:underline font-semibold"
            >
              Import controls to begin →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {summary?.byDomain?.map((domain: any) => {
              const domainProgress = domain.total > 0 ? (domain.complete / domain.total) * 100 : 0
              const isComplete = domain.total > 0 && domain.complete === domain.total
              const hasControls = (domain.total || 0) > 0
              
              return (
                <Link
                  key={domain.domain}
                  to={`/tenant/${tenantId}/domain/${domain.domain}`}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isComplete 
                      ? 'border-green-300 bg-green-50' 
                      : hasControls 
                        ? 'border-blue-200 bg-white hover:border-blue-500 hover:shadow-md' 
                        : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-semibold text-gray-900">{domain.domain}</div>
                    {isComplete && <span className="text-green-600">✓</span>}
                  </div>
                  <div className="mb-2">
                    <div className="text-sm text-gray-600">
                      {domain.complete} / {domain.total} controls
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`rounded-full h-2 transition-all ${
                        isComplete ? 'bg-green-600' : 'bg-blue-600'
                      }`}
                      style={{ width: `${domainProgress}%` }}
                    />
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        <Link
          to={`/tenant/${tenantId}/controls`}
          className="bg-white rounded-lg border p-4 hover:border-blue-500 hover:shadow-md transition-all"
        >
          <div className="text-lg font-semibold text-gray-900 mb-2">📋 Controls</div>
          <div className="text-sm text-gray-600">View and manage all controls</div>
        </Link>
        <Link
          to={`/tenant/${tenantId}/gaps`}
          className="bg-white rounded-lg border p-4 hover:border-blue-500 hover:shadow-md transition-all"
        >
          <div className="text-lg font-semibold text-gray-900 mb-2">⚠️ Gaps</div>
          <div className="text-sm text-gray-600">Review identified security gaps</div>
        </Link>
        <Link
          to={`/tenant/${tenantId}/tools`}
          className="bg-white rounded-lg border p-4 hover:border-blue-500 hover:shadow-md transition-all"
        >
          <div className="text-lg font-semibold text-gray-900 mb-2">🔧 Tools</div>
          <div className="text-sm text-gray-600">Manage security tool inventory</div>
        </Link>
        <Link
          to={`/tenant/${tenantId}/report`}
          className="bg-white rounded-lg border p-4 hover:border-blue-500 hover:shadow-md transition-all"
        >
          <div className="text-lg font-semibold text-gray-900 mb-2">📊 Report</div>
          <div className="text-sm text-gray-600">Generate assessment report</div>
        </Link>
      </div>
    </div>
  )
}

