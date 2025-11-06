import { useState } from 'react'
import { Link } from 'react-router-dom'

interface Props { tenantId: string }

export default function Report({ tenantId }: Props) {
  const [report, setReport] = useState<any>(null)
  const [generating, setGenerating] = useState(false)
  const [includeAI, setIncludeAI] = useState(true)

  const generateReport = async () => {
    setGenerating(true)
    try {
      const response = await fetch(`/api/tenant/${tenantId}/report?includeAI=${includeAI}`)
      const data = await response.json()
      setReport(data)
    } catch (error: any) {
      alert(`Failed to generate report: ${error.message}`)
    } finally {
      setGenerating(false)
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
  `${d.domain}: ${d.complete}/${d.total} complete`
).join('\n') || 'No data'}

GAPS
${report.gaps?.map((g: any) => 
  `${g.ControlID}: ${g.Coverage * 100}% coverage - ${g.HardGaps?.length || 0} hard gaps, ${g.SoftGaps?.length || 0} soft gaps`
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg p-6">
        <Link to={`/tenant/${tenantId}/assessment`} className="text-blue-200 hover:text-white text-sm mb-2 inline-block">
          ← Back to Assessment Overview
        </Link>
        <h1 className="text-3xl font-bold mb-2">Assessment Report</h1>
        <p className="text-blue-100">Generate comprehensive assessment report for {tenantId}</p>
      </div>

      {/* Report Generation */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Report</h2>
        <div className="space-y-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={includeAI}
              onChange={e => setIncludeAI(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-700">Include AI-generated executive summary</span>
          </label>
          <button
            onClick={generateReport}
            disabled={generating}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
          >
            {generating ? 'Generating Report...' : 'Generate Report'}
          </button>
        </div>
      </div>

      {/* Report Display */}
      {report && (
        <div className="space-y-6">
          {/* Executive Summary */}
          {report.executiveSummary && (
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Executive Summary</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{report.executiveSummary}</p>
              </div>
            </div>
          )}

          {/* Assessment Summary */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Assessment Summary</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Total Controls</div>
                <div className="text-2xl font-bold text-gray-900">{report.summary?.totalControls || 0}</div>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Controls with Gaps</div>
                <div className="text-2xl font-bold text-red-900">{report.summary?.totalGaps || 0}</div>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Critical Gaps</div>
                <div className="text-2xl font-bold text-orange-900">{report.summary?.criticalGaps || 0}</div>
              </div>
            </div>
          </div>

          {/* Domain Breakdown */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Domain Breakdown</h2>
            <div className="space-y-2">
              {report.summary?.byDomain?.map((domain: any) => {
                const progress = domain.total > 0 ? (domain.complete / domain.total) * 100 : 0
                return (
                  <div key={domain.domain} className="p-3 bg-gray-50 rounded border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-900">{domain.domain}</span>
                      <span className="text-sm text-gray-600">{domain.complete} / {domain.total} complete</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 rounded-full h-2"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Gaps Summary */}
          {report.gaps && report.gaps.length > 0 && (
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Gaps Summary</h2>
              <div className="space-y-3">
                {report.gaps.slice(0, 10).map((gap: any, idx: number) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-900">{gap.ControlID}</span>
                      <span className="text-sm text-gray-600">Coverage: {(gap.Coverage * 100).toFixed(1)}%</span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Hard gaps: {gap.HardGaps?.length || 0} • Soft gaps: {gap.SoftGaps?.length || 0}
                    </div>
                  </div>
                ))}
                {report.gaps.length > 10 && (
                  <div className="text-sm text-gray-500 text-center">
                    ... and {report.gaps.length - 10} more controls with gaps
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Download Actions */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Report</h2>
            <div className="flex gap-4">
              <button
                onClick={downloadReport}
                className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
              >
                Download Report (TXT)
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
                className="px-6 py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700"
              >
                Download JSON
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

