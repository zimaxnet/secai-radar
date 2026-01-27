/**
 * Policy UI (T-112): create/list policies, show approval state and expiry.
 */
import { useState, useEffect } from 'react'
import { getPolicies, createPolicy, type CreatePolicyRequest } from '../../api/private'

const DEMO_WORKSPACE_ID = 'ws-demo-00000001'

export default function RegistryPolicies() {
  const [data, setData] = useState<{ policies: any[] }>({ policies: [] })
  const [loading, setLoading] = useState(true)
  const [scopeType, setScopeType] = useState<'server' | 'tool' | 'category'>('server')
  const [scopeValue, setScopeValue] = useState('')
  const [decision, setDecision] = useState<'Allow' | 'Deny' | 'RequireApproval'>('Allow')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let ok = true
    setLoading(true)
    getPolicies(DEMO_WORKSPACE_ID).then((r) => {
      if (ok) setData(r)
    }).finally(() => { if (ok) setLoading(false) })
    return () => { ok = false }
  }, [])

  const handleCreate = async () => {
    if (!scopeValue.trim()) return
    setSubmitting(true)
    try {
      const body: CreatePolicyRequest = {
        scope: { type: scopeType, value: scopeValue.trim() },
        decision,
      }
      const res = await createPolicy(body, DEMO_WORKSPACE_ID)
      if (res?.policyId) {
        setScopeValue('')
        const next = await getPolicies(DEMO_WORKSPACE_ID)
        setData(next)
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p className="text-slate-400">Loading policies…</p>

  return (
    <div>
      <h1 className="text-xl font-semibold text-white mb-4">Policies</h1>
      <p className="text-slate-400 text-sm mb-4">Allow/Deny/RequireApproval by server, tool, or category.</p>

      <div className="flex flex-wrap gap-2 mb-6 items-center">
        <select
          value={scopeType}
          onChange={(e) => setScopeType(e.target.value as any)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white"
        >
          <option value="server">server</option>
          <option value="tool">tool</option>
          <option value="category">category</option>
        </select>
        <input
          type="text"
          placeholder="Scope value"
          value={scopeValue}
          onChange={(e) => setScopeValue(e.target.value)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white placeholder-slate-500 w-40"
        />
        <select
          value={decision}
          onChange={(e) => setDecision(e.target.value as any)}
          className="rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-white"
        >
          <option value="Allow">Allow</option>
          <option value="Deny">Deny</option>
          <option value="RequireApproval">RequireApproval</option>
        </select>
        <button
          type="button"
          onClick={handleCreate}
          disabled={submitting || !scopeValue.trim()}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {submitting ? 'Creating…' : 'Create'}
        </button>
      </div>

      <ul className="space-y-2">
        {data.policies.length === 0 && <li className="text-slate-500">No policies.</li>}
        {data.policies.map((p: any) => (
          <li key={p.policyId} className="rounded-lg bg-slate-800/50 border border-slate-700/50 px-4 py-3 flex flex-wrap gap-2 items-center">
            <span className="font-mono text-sm text-slate-300">{p.policyId}</span>
            <span className="text-white">{p.decision}</span>
            <span className="text-slate-400 text-sm">
              {typeof p.scope === 'object' ? `${p.scope?.type}: ${p.scope?.value}` : JSON.stringify(p.scope)}
            </span>
            {p.expiresAt && <span className="text-slate-500 text-xs">expires {p.expiresAt}</span>}
          </li>
        ))}
      </ul>
    </div>
  )
}
