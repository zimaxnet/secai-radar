/**
 * Evidence pack upload + list UI (T-113, T-207): upload file, list packs with status; show "validated" when approved.
 */
import { useState, useEffect, useCallback } from 'react'
import { uploadEvidencePack, getEvidencePacks } from '../../api/private'

const DEMO_WORKSPACE_ID = 'ws-demo-00000001'

type PackRow = { packId: string; serverId: string; status: string; submittedAt?: string; validatedAt?: string; validatedBy?: string; confidence?: number }

export default function RegistryEvidence() {
  const [serverId, setServerId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [lastResult, setLastResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [packs, setPacks] = useState<PackRow[]>([])
  const [loadingList, setLoadingList] = useState(false)

  const loadPacks = useCallback(async () => {
    setLoadingList(true)
    try {
      const { items } = await getEvidencePacks(undefined, DEMO_WORKSPACE_ID)
      setPacks(items as PackRow[])
    } finally {
      setLoadingList(false)
    }
  }, [])

  useEffect(() => {
    loadPacks()
  }, [loadPacks])

  const handleSubmit = async () => {
    if (!serverId.trim()) return
    setSubmitting(true)
    setError(null)
    setLastResult(null)
    try {
      const res = await uploadEvidencePack(serverId.trim(), file ?? undefined, DEMO_WORKSPACE_ID)
      if (res?.packId) {
        setLastResult(`Pack ${res.packId} uploaded — status: ${res.status ?? 'Submitted'}`)
        setServerId('')
        setFile(null)
        await loadPacks()
      } else {
        setError('Upload failed or server not found')
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-white mb-4">Evidence packs</h1>
      <p className="text-slate-400 text-sm mb-4">Upload evidence for a server (ID or slug). Validated packs show approval status.</p>

      <div className="flex flex-wrap gap-2 mb-4 items-end">
        <div>
          <label className="block text-xs text-slate-500 mb-1">Server ID or slug</label>
          <input
            type="text"
            placeholder="e.g. filesystem or s100000000000001"
            value={serverId}
            onChange={(e) => setServerId(e.target.value)}
            className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white placeholder-slate-500 w-56"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1">File (optional)</label>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white text-sm"
          />
        </div>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={submitting || !serverId.trim()}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {submitting ? 'Uploading…' : 'Upload'}
        </button>
      </div>
      {error && <p className="text-red-400 text-sm mb-2">{error}</p>}
      {lastResult && <p className="text-green-400 text-sm mb-4">{lastResult}</p>}

      <div className="mt-6">
        <h2 className="text-lg font-medium text-white mb-2">Evidence packs in this workspace</h2>
        {loadingList ? (
          <p className="text-slate-500 text-sm">Loading…</p>
        ) : packs.length === 0 ? (
          <p className="text-slate-500 text-sm">No evidence packs yet. Upload one above.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-700">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-800 text-slate-300 text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Pack ID</th>
                  <th className="px-4 py-2 font-medium">Server</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Submitted</th>
                  <th className="px-4 py-2 font-medium">Validated</th>
                </tr>
              </thead>
              <tbody className="text-slate-400 divide-y divide-slate-700">
                {packs.map((p) => (
                  <tr key={p.packId} className="bg-slate-800/50">
                    <td className="px-4 py-2 font-mono text-slate-300">{p.packId}</td>
                    <td className="px-4 py-2">{p.serverId}</td>
                    <td className="px-4 py-2">
                      <span className={p.status === 'Validated' ? 'text-emerald-400' : p.status === 'Rejected' ? 'text-red-400' : 'text-amber-400'}>
                        {p.status}
                      </span>
                      {p.confidence != null && <span className="ml-1 text-slate-500">(conf {p.confidence})</span>}
                    </td>
                    <td className="px-4 py-2">{p.submittedAt ? new Date(p.submittedAt).toLocaleString() : '—'}</td>
                    <td className="px-4 py-2">{p.validatedAt ? new Date(p.validatedAt).toLocaleString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
