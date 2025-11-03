import { useEffect, useState } from 'react'
import { getGaps } from '../api'

interface Props { tenantId: string }

export default function Gaps({ tenantId }: Props) {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    getGaps(tenantId).then(d => {
      if (!mounted) return
      setItems(d.items || [])
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId])

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Gaps</h2>
      <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 p-2 rounded">
        Tip: prioritize tuning existing tools (raise ConfigScore) before recommending net-new.
      </p>
      {loading && <div className="text-gray-500">Loading…</div>}
      <div className="space-y-3">
        {items.map(it => (
          <div key={it.ControlID} className="rounded border bg-white p-3">
            <div className="flex items-center justify-between">
              <div className="font-medium">{it.ControlID}</div>
              <div className="text-sm text-gray-600">Coverage: {(it.Coverage*100).toFixed(1)}%</div>
            </div>
            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <div className="text-sm font-semibold text-gray-700">Hard Gaps</div>
                <ul className="list-disc list-inside text-sm text-gray-800">
                  {it.HardGaps?.length ? it.HardGaps.map((g:any, idx:number)=>(
                    <li key={idx}>{g.capabilityId} (w={g.weight})</li>
                  )) : <li className="text-gray-500">None</li>}
                </ul>
              </div>
              <div>
                <div className="text-sm font-semibold text-gray-700">Soft Gaps</div>
                <ul className="list-disc list-inside text-sm text-gray-800">
                  {it.SoftGaps?.length ? it.SoftGaps.map((g:any, idx:number)=>(
                    <li key={idx}>{g.capabilityId} best={g.best?.toFixed(2)} min={g.min?.toFixed(2)} tool={g.tool || 'n/a'}</li>
                  )) : <li className="text-gray-500">None</li>}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
