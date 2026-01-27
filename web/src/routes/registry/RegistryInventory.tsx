/**
 * Registry inventory UI (T-111): list servers, add by slug/id, show latest trust score.
 */
import { useState, useEffect } from 'react'
import { getRegistryServers, addRegistryServer } from '../../api/private'

const DEMO_WORKSPACE_ID = 'ws-demo-00000001'

export default function RegistryInventory() {
  const [data, setData] = useState<{ servers: any[]; total: number }>({ servers: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [addSlug, setAddSlug] = useState('')
  const [addOwner, setAddOwner] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ok = true
    setLoading(true)
    getRegistryServers(DEMO_WORKSPACE_ID).then((r) => {
      if (ok) setData(r)
    }).finally(() => { if (ok) setLoading(false) })
    return () => { ok = false }
  }, [])

  const handleAdd = async () => {
    if (!addSlug.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const res = await addRegistryServer(
        { serverId: addSlug.trim(), owner: addOwner.trim() || undefined },
        DEMO_WORKSPACE_ID
      )
      if (res?.serverId) {
        setAddSlug('')
        setAddOwner('')
        const next = await getRegistryServers(DEMO_WORKSPACE_ID)
        setData(next)
      } else {
        setError('Add failed or server not found')
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <p className="text-slate-400">Loading inventory…</p>
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-white mb-4">Workspace inventory</h1>
      <p className="text-slate-400 text-sm mb-4">Servers in this workspace. Add by server ID or slug from the public registry.</p>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          placeholder="Server ID or slug"
          value={addSlug}
          onChange={(e) => setAddSlug(e.target.value)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white placeholder-slate-500 w-48"
        />
        <input
          type="text"
          placeholder="Owner (optional)"
          value={addOwner}
          onChange={(e) => setAddOwner(e.target.value)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white placeholder-slate-500 w-40"
        />
        <button
          type="button"
          onClick={handleAdd}
          disabled={submitting || !addSlug.trim()}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {submitting ? 'Adding…' : 'Add'}
        </button>
      </div>
      {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

      <ul className="space-y-2">
        {data.servers.length === 0 && <li className="text-slate-500">No servers in inventory.</li>}
        {data.servers.map((s: any) => (
          <li key={s.inventoryId ?? s.serverId} className="flex items-center gap-4 rounded-lg bg-slate-800/50 border border-slate-700/50 px-4 py-3">
            <span className="font-medium text-white">{s.serverName ?? s.serverSlug ?? s.serverId}</span>
            <span className="text-slate-400 text-sm">{s.serverId}</span>
            {s.status && <span className="text-slate-500 text-sm">{s.status}</span>}
          </li>
        ))}
      </ul>
    </div>
  )
}
