import { useEffect, useState } from 'react'
import { getGaps, postTools } from '../src/api'

interface Props { tenantId: string }

export default function Tools({ tenantId }: Props) {
  const [vendorToolId, setVendorToolId] = useState('')
  const [enabled, setEnabled] = useState(true)
  const [configScore, setConfigScore] = useState(0.8)
  const [message, setMessage] = useState('')

  const submit = async () => {
    setMessage('')
    const res = await postTools(tenantId, { vendorToolId, Enabled: enabled, ConfigScore: configScore })
    if (res?.ok) setMessage('Saved!')
    else setMessage('Error saving tool')
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Tools</h2>
      <div className="grid gap-3 max-w-xl">
        <label className="grid gap-1">
          <span className="text-sm text-gray-700">Vendor Tool ID</span>
          <input className="border rounded p-2" value={vendorToolId} onChange={e=>setVendorToolId(e.target.value)} placeholder="e.g., wiz-cspm" />
        </label>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={enabled} onChange={e=>setEnabled(e.target.checked)} />
          <span className="text-sm text-gray-700">Enabled</span>
        </label>
        <label className="grid gap-1">
          <span className="text-sm text-gray-700">Config Score (0..1)</span>
          <input type="number" min={0} max={1} step={0.05} className="border rounded p-2" value={configScore} onChange={e=>setConfigScore(parseFloat(e.target.value))} />
        </label>
        <div>
          <button onClick={submit} className="px-3 py-2 bg-blue-600 text-white rounded">Save</button>
        </div>
        {message && <div className="text-sm text-green-700">{message}</div>}
      </div>
    </div>
  )
}
