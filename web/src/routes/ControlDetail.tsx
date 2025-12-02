import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getControl, getAIRecommendation, getEvidence, uploadEvidence, getGaps } from '../api'
import PageHeader from '../components/ui/PageHeader'
import GlassCard from '../components/ui/GlassCard'

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

  useEffect(() => {
    if (!controlId) return
    let mounted = true
    setLoading(true)

    getControl(tenantId, controlId).then((c: any) => {
      if (!mounted) return
      setControl(c)
      if (c?.Notes || c?.Observations) setObservations(c.Notes || c.Observations || '')
    })

    getGaps(tenantId).then(d => {
      if (!mounted) return
      const controlGaps = d.items?.find((g: any) => g.ControlID === controlId)
      setGaps(controlGaps)
    })

    getEvidence(tenantId, controlId).then(d => {
      if (!mounted) return
      setEvidence(d.items || [])
    }).catch(() => setEvidence([]))

    setLoading(false)
    return () => { mounted = false }
  }, [tenantId, controlId])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !controlId) return

    setUploading(true)
    try {
      await uploadEvidence(tenantId, controlId, file)
      const d = await getEvidence(tenantId, controlId)
      setEvidence(d.items || [])
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
      alert(`Failed to load AI recommendation: ${error.message}`)
    }
  }

  if (loading || !control) {
    return <div className="flex items-center justify-center h-96 text-blue-400 animate-pulse">Initializing Control Assessment...</div>
  }

  const domain = control.Domain || control.PartitionKey?.split('|')[1] || 'Unknown'
  const coverage = gaps?.Coverage || 0
  const hardGaps = gaps?.HardGaps || []
  const softGaps = gaps?.SoftGaps || []

  return (
    <div className="space-y-8 pb-24">
      <PageHeader 
        title={control.ControlID} 
        subtitle={control.ControlTitle}
        parentLink={{ to: `/tenant/${tenantId}/domain/${domain}`, label: `Back to ${domain}` }}
        action={
          <div className="flex items-center gap-3">
            <div className="text-right mr-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider">Coverage</div>
              <div className={`text-2xl font-bold ${coverage >= 0.7 ? 'text-green-400' : 'text-orange-400'}`}>
                {(coverage * 100).toFixed(0)}%
              </div>
            </div>
            <div className="h-12 w-12 rounded-full border-4 border-slate-800 flex items-center justify-center bg-slate-900 relative">
               <svg className="absolute inset-0 h-full w-full -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-800"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className={coverage >= 0.7 ? 'text-green-500' : 'text-orange-500'}
                  strokeDasharray={`${coverage * 100}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="4"
                />
              </svg>
            </div>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* LEFT COLUMN: Assessment */}
        <div className="lg:col-span-7 space-y-6">
          <GlassCard className="p-6">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">Assessment Data</h3>
            
            {/* Status Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                <label className="block text-xs text-slate-500 mb-1">Status</label>
                <select 
                  className="w-full bg-transparent text-white border-none focus:ring-0 p-0 font-medium"
                  defaultValue={control.Status || 'NotStarted'}
                >
                  <option value="NotStarted">Not Started</option>
                  <option value="InProgress">In Progress</option>
                  <option value="Complete">Complete</option>
                </select>
              </div>
              <div className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                <label className="block text-xs text-slate-500 mb-1">Owner</label>
                <input 
                  type="text" 
                  defaultValue={control.Owner} 
                  className="w-full bg-transparent text-white border-none focus:ring-0 p-0 font-medium"
                  placeholder="Unassigned" 
                />
              </div>
            </div>

            {/* Observations */}
            <div className="mb-6">
              <label className="block text-xs text-slate-500 mb-2 uppercase tracking-wider">Notes & Findings</label>
              <textarea
                className="w-full h-32 bg-slate-900/50 border border-white/10 rounded-lg p-4 text-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                value={observations}
                onChange={e => setObservations(e.target.value)}
                placeholder="Enter assessment notes..."
              />
            </div>

            {/* Evidence Drop Zone */}
            <div>
              <div className="flex justify-between items-end mb-2">
                <label className="block text-xs text-slate-500 uppercase tracking-wider">Evidence Files</label>
                <span className="text-xs text-slate-500">{evidence.length} files attached</span>
              </div>
              
              <div className="border-2 border-dashed border-slate-700 rounded-xl p-6 text-center hover:border-blue-500/50 hover:bg-blue-500/5 transition-all relative group">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="pointer-events-none">
                  <div className="mx-auto h-10 w-10 text-slate-500 mb-2 group-hover:text-blue-400 transition-colors">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                  </div>
                  <p className="text-sm text-slate-300 font-medium">Drop files here or click to upload</p>
                  <p className="text-xs text-slate-500 mt-1">PDF, PNG, JPG, CSV (Max 10MB)</p>
                </div>
                {uploading && (
                  <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center rounded-xl">
                    <div className="text-blue-400 font-medium animate-pulse">Uploading...</div>
                  </div>
                )}
              </div>

              {/* File List */}
              <div className="mt-4 space-y-2">
                {evidence.map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-white/5 hover:border-white/10 transition-all">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-400">
                        {item.fileName.split('.').pop()?.toUpperCase()}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-slate-200">{item.fileName}</div>
                        <div className="text-xs text-slate-500">
                          {(item.size / 1024).toFixed(1)} KB • {new Date(item.uploadedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    {item.downloadUrl && (
                      <a href={item.downloadUrl} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm font-medium px-3 py-1 rounded hover:bg-blue-500/10 transition-colors">
                        Download
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>

        {/* RIGHT COLUMN: Context */}
        <div className="lg:col-span-5 space-y-6">
          {/* Context Card */}
          <GlassCard className="p-6 bg-blue-900/10 border-blue-500/20">
            <h3 className="text-sm font-medium text-blue-400 uppercase tracking-wider mb-3">Control Context</h3>
            <p className="text-slate-300 text-sm leading-relaxed mb-4">{control.ControlDescription}</p>
            
            {control.Question && (
              <div className="bg-blue-950/50 p-4 rounded-lg border border-blue-500/10">
                <div className="text-xs text-blue-400 font-medium mb-1">Validation Question</div>
                <p className="text-sm text-slate-300 italic">"{control.Question}"</p>
              </div>
            )}

            {control.SourceRef && (
              <div className="mt-4 flex justify-between items-center text-xs">
                <span className="text-slate-500">Framework Ref</span>
                <span className="font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded">{control.SourceRef}</span>
              </div>
            )}
          </GlassCard>

          {/* Gaps Card */}
          {(hardGaps.length > 0 || softGaps.length > 0) && (
            <GlassCard className="p-6 border-red-500/20 bg-red-900/5">
               <div className="flex items-center gap-2 mb-4">
                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                <h3 className="text-sm font-medium text-red-400 uppercase tracking-wider">Detected Gaps</h3>
              </div>
              
              <div className="space-y-3">
                {hardGaps.map((g: any, i: number) => (
                  <div key={i} className="p-3 rounded bg-red-500/10 border border-red-500/20">
                    <div className="text-red-200 font-medium text-sm">{g.capabilityId}</div>
                    <div className="text-xs text-red-400 mt-1">Critical Missing Capability</div>
                  </div>
                ))}
                {softGaps.map((g: any, i: number) => (
                  <div key={i} className="p-3 rounded bg-orange-500/10 border border-orange-500/20">
                    <div className="text-orange-200 font-medium text-sm">{g.capabilityId}</div>
                    <div className="text-xs text-orange-400 mt-1">Configuration Weakness ({g.best?.toFixed(1)}/{g.min?.toFixed(1)})</div>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {/* AI Insight */}
          <GlassCard className="p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-3 opacity-10">
              <svg className="w-24 h-24 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/><path d="M12 6a1 1 0 0 0-1 1v4.59L7.71 14.88a1 1 0 0 0 1.41 1.41L13 12.41V7a1 1 0 0 0-1-1z"/></svg>
            </div>
            
            <h3 className="text-sm font-medium text-purple-400 uppercase tracking-wider mb-3">AI Insight</h3>
            
            {aiRecommendation ? (
              <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap relative z-10">
                {aiRecommendation}
              </div>
            ) : (
              <div className="text-center py-4 relative z-10">
                <p className="text-sm text-slate-500 mb-3">Need help implementing this control?</p>
                <button
                  onClick={loadAIRecommendation}
                  className="px-4 py-2 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded-lg border border-purple-500/30 transition-all text-sm font-medium"
                >
                  Generate AI Guidance
                </button>
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
