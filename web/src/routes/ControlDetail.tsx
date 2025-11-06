import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getControl, getAIRecommendation, getEvidence, uploadEvidence, getGaps } from '../api'

interface Props { tenantId: string }

export default function ControlDetail({ tenantId }: Props) {
  const { controlId } = useParams<{ controlId: string }>()
  const [control, setControl] = useState<any>(null)
  const [gaps, setGaps] = useState<any>(null)
  const [evidence, setEvidence] = useState<any[]>([])
  const [aiRecommendation, setAiRecommendation] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [observations, setObservations] = useState('')
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    if (!controlId) return
    let mounted = true
    setLoading(true)

    // Load control details
    getControl(tenantId, controlId).then(c => {
      if (!mounted) return
      setControl(c)
      if (c?.Notes) setObservations(c.Notes)
    })

    // Load gaps for this control
    getGaps(tenantId).then(d => {
      if (!mounted) return
      const controlGaps = d.items?.find((g: any) => g.ControlID === controlId)
      setGaps(controlGaps)
    })

    // Load evidence
    getEvidence(tenantId, controlId).then(d => {
      if (!mounted) return
      setEvidence(d.items || [])
    }).catch(() => {
      // Evidence endpoint might not exist yet
      setEvidence([])
    })

    setLoading(false)
    return () => { mounted = false }
  }, [tenantId, controlId])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !controlId) return

    setUploading(true)
    try {
      await uploadEvidence(tenantId, controlId, file)
      // Reload evidence
      const d = await getEvidence(tenantId, controlId)
      setEvidence(d.items || [])
      setShowUpload(false)
    } catch (error: any) {
      alert(`Upload failed: ${error.message || 'Unknown error'}`)
    } finally {
      setUploading(false)
    }
  }

  const loadAIRecommendation = async () => {
    if (!controlId || aiRecommendation) return
    try {
      const result = await getAIRecommendation(tenantId, controlId)
      setAiRecommendation(result.recommendation)
    } catch (error: any) {
      alert(`Failed to load AI recommendation: ${error.message || 'Unknown error'}`)
    }
  }

  if (loading || !control) {
    return <div className="text-gray-500">Loading control details...</div>
  }

  const domain = control.Domain || control.PartitionKey?.split('|')[1] || 'Unknown'
  const coverage = gaps?.Coverage || 0
  const hardGaps = gaps?.HardGaps || []
  const softGaps = gaps?.SoftGaps || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
            <Link to={`/tenant/${tenantId}/assessment`} className="hover:text-blue-600 hover:underline">
              Assessment
            </Link>
            <span>/</span>
            <Link to={`/tenant/${tenantId}/domain/${domain}`} className="hover:text-blue-600 hover:underline">
              {domain}
            </Link>
            <span>/</span>
            <span className="text-gray-900 font-medium">{control.ControlID}</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mt-2">{control.ControlID}</h1>
          <p className="text-lg text-gray-700 mt-1">{control.ControlTitle}</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">Coverage</div>
          <div className="text-2xl font-bold" style={{ color: coverage >= 0.7 ? 'green' : coverage >= 0.5 ? 'orange' : 'red' }}>
            {(coverage * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Control Description */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h2 className="text-sm font-semibold text-blue-900 mb-2">Description</h2>
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{control.ControlDescription || 'No description available.'}</p>
        {control.Question && (
          <div className="mt-3 pt-3 border-t border-blue-200">
            <div className="text-sm font-semibold text-blue-900 mb-1">Question</div>
            <p className="text-sm text-gray-800">{control.Question}</p>
          </div>
        )}
        {control.SourceRef && (
          <div className="mt-3 pt-3 border-t border-blue-200">
            <div className="text-sm font-semibold text-blue-900 mb-1">Framework Reference</div>
            <a href={control.SourceRef} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
              {control.SourceRef}
            </a>
          </div>
        )}
      </div>

      {/* Capability Breakdown & Gaps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Hard Gaps</h2>
          {hardGaps.length > 0 ? (
            <ul className="space-y-2">
              {hardGaps.map((gap: any, idx: number) => (
                <li key={idx} className="text-sm text-red-700 bg-red-50 p-2 rounded">
                  <span className="font-medium">{gap.capabilityId}</span>
                  <span className="text-gray-600 ml-2">(weight: {gap.weight})</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No hard gaps</p>
          )}
        </div>

        <div className="bg-white border rounded-lg p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Soft Gaps</h2>
          {softGaps.length > 0 ? (
            <ul className="space-y-2">
              {softGaps.map((gap: any, idx: number) => (
                <li key={idx} className="text-sm text-orange-700 bg-orange-50 p-2 rounded">
                  <span className="font-medium">{gap.capabilityId}</span>
                  <span className="text-gray-600 ml-2">
                    current: {gap.best?.toFixed(2)}, needed: {gap.min?.toFixed(2)}
                  </span>
                  {gap.tool && <span className="text-xs text-gray-500 block mt-1">Tool: {gap.tool}</span>}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No soft gaps</p>
          )}
        </div>
      </div>

      {/* AI Recommendations */}
      {(hardGaps.length > 0 || softGaps.length > 0) && (
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900">AI Recommendations</h2>
            {!aiRecommendation && (
              <button
                onClick={loadAIRecommendation}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Generate Recommendation →
              </button>
            )}
          </div>
          {aiRecommendation ? (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded">
              <div className="text-sm text-gray-800 whitespace-pre-wrap">{aiRecommendation}</div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Click to generate AI-powered recommendations</p>
          )}
        </div>
      )}

      {/* Observations/Notes */}
      <div className="bg-white border rounded-lg p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Observations & Notes</h2>
        <textarea
          className="w-full h-32 border rounded p-2 text-sm"
          value={observations}
          onChange={e => setObservations(e.target.value)}
          placeholder="Enter observations, notes, or findings for this control..."
        />
        <div className="mt-2 text-xs text-gray-500">
          Note: Saving observations requires a control update endpoint
        </div>
      </div>

      {/* Evidence */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">Evidence</h2>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {showUpload ? 'Cancel' : '+ Upload Evidence'}
          </button>
        </div>

        {showUpload && (
          <div className="mb-4 p-3 bg-gray-50 border rounded">
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={uploading}
              className="text-sm"
            />
            {uploading && <div className="text-sm text-gray-500 mt-2">Uploading...</div>}
          </div>
        )}

        {evidence.length > 0 ? (
          <div className="space-y-2">
            {evidence.map((item: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">{item.fileName}</div>
                  {item.classification && (
                    <div className="text-xs text-gray-600 mt-1">
                      Type: {item.classification.category} • 
                      Sensitivity: {item.classification.sensitivity_level}
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-1">
                    {item.size ? `${(item.size / 1024).toFixed(1)} KB` : ''}
                    {item.uploadedAt && ` • ${new Date(item.uploadedAt).toLocaleDateString()}`}
                  </div>
                </div>
                {item.downloadUrl && (
                  <a
                    href={item.downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline ml-4"
                  >
                    Download
                  </a>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No evidence uploaded yet</p>
        )}
      </div>

      {/* Control Metadata */}
      <div className="bg-gray-50 border rounded-lg p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-2">Control Metadata</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Status</div>
            <div className="font-medium">{control.Status || 'Not Started'}</div>
          </div>
          <div>
            <div className="text-gray-600">Owner</div>
            <div className="font-medium">{control.Owner || 'Unassigned'}</div>
          </div>
          <div>
            <div className="text-gray-600">Frequency</div>
            <div className="font-medium">{control.Frequency || 'N/A'}</div>
          </div>
          <div>
            <div className="text-gray-600">Domain</div>
            <div className="font-medium">{domain}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

