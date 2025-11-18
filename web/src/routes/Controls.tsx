import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { getControls, importControls } from '../api'
import { useSearchParams } from 'react-router-dom'
import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table'
import { z } from 'zod'

interface Props { tenantId: string }
interface ControlRow { [k:string]: any }

const REQUIRED_HEADERS = [
  'ControlID','Domain','ControlTitle','ControlDescription','Question','RequiredEvidence',
  'Status','Owner','Frequency','ScoreNumeric','Weight','Notes','SourceRef','Tags','UpdatedAt'
] as const

const headerSchema = z.array(z.string()).refine(arr => {
  if (arr.length < REQUIRED_HEADERS.length) return false
  // Require exact order for simplicity
  return REQUIRED_HEADERS.every((h, i) => arr[i] === h)
}, { message: `CSV header must be: ${REQUIRED_HEADERS.join(',')}` })

export default function Controls({ tenantId }: Props) {
  const [rows, setRows] = useState<ControlRow[]>([])
  const [csv, setCsv] = useState('')
  const [loading, setLoading] = useState(false)
  const [params, setParams] = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const [okMsg, setOkMsg] = useState<string | null>(null)

  const domain = params.get('domain') || ''
  const status = params.get('status') || ''
  const q = params.get('q') || ''

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null) // Clear previous errors on new fetch
    getControls(tenantId, { domain: domain || undefined, status: status || undefined, q: q || undefined })
      .then(d => {
        if (!mounted) return
        setRows(d.items || [])
      })
      .catch(err => {
        if (!mounted) return
        setError(err.message || 'Failed to load controls')
        setRows([])
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => { mounted = false }
  }, [tenantId, domain, status, q])

  const columns = useMemo<ColumnDef<ControlRow>[]>(() => ([
    { 
      header: 'ControlID', 
      accessorKey: 'RowKey',
      cell: ({ row }) => {
        const controlId = row.original.RowKey;
        return (
          <Link 
            to={`/tenant/${tenantId}/control/${controlId}`}
            className="text-blue-600 hover:underline font-medium"
          >
            {controlId}
          </Link>
        );
      }
    },
    { 
      header: 'Domain', 
      accessorKey: 'Domain',
      cell: ({ row }) => {
        const domain = row.original.Domain || row.original.PartitionKey?.split('|')[1] || '';
        return (
          <Link 
            to={`/tenant/${tenantId}/domain/${domain}`}
            className="text-blue-600 hover:underline"
          >
            {domain}
          </Link>
        );
      }
    },
    { header: 'Title', accessorKey: 'ControlTitle' },
    { header: 'Status', accessorKey: 'Status' },
    { header: 'Owner', accessorKey: 'Owner' },
    { 
      header: 'Reference', 
      accessorKey: 'SourceRef',
      cell: ({ row }) => {
        const ref = row.original.SourceRef;
        if (!ref || !ref.trim()) return <span className="text-gray-400">-</span>;
        // Check if it's a URL
        if (ref.trim().startsWith('http://') || ref.trim().startsWith('https://')) {
          return (
            <a 
              href={ref.trim()} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-blue-600 hover:underline text-sm"
              title={ref.trim()}
            >
              🔗 Wiki
            </a>
          );
        }
        return <span className="text-sm text-gray-700">{ref}</span>;
      }
    },
  ]), [tenantId])

  const table = useReactTable({ data: rows, columns, getCoreRowModel: getCoreRowModel() })

  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value); else next.delete(key)
    setParams(next, { replace: true })
  }

  const submitCsv = async () => {
    setError(null)
    setOkMsg(null)
    setLoading(true)
    
    try {
      // Validate CSV header
      const headerLine = (csv.split(/\r?\n/).find(l => l.trim().length > 0) || '').trim()
      const headerArr = headerLine.split(',').map(s => s.trim())
      const parsed = headerSchema.safeParse(headerArr)
      if (!parsed.success) {
        setError(parsed.error.issues[0]?.message || 'Invalid CSV header')
        setLoading(false)
        return
      }
      
      // Import controls
      await importControls(tenantId, csv)
      
      // Refresh controls data after successful import
      try {
        const data = await getControls(tenantId, { domain: domain || undefined, status: status || undefined, q: q || undefined })
        setRows(data.items || [])
        setCsv('')
        setOkMsg('Imported successfully')
        // Update params to trigger refresh (this will also trigger useEffect, but we've already updated rows)
        const next = new URLSearchParams(params)
        setParams(next)
      } catch (refreshError) {
        // Import succeeded but refresh failed - show error but keep form open
        setError(`Import succeeded, but failed to refresh data: ${refreshError instanceof Error ? refreshError.message : 'Unknown error'}`)
        // Don't clear CSV or show success message since refresh failed
        // The user can see the error and retry if needed
      }
    } catch (importError) {
      // Import failed - show error, keep form open
      setError(importError instanceof Error ? importError.message : 'Failed to import controls')
      // Don't clear CSV or update params - user can retry
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">Controls</h1>
        <p className="text-blue-100">View and manage all security controls. Click a control ID to see details, or click a domain to view the domain assessment page.</p>
      </div>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="text-sm font-semibold text-blue-900 mb-2">💡 Tip</div>
        <p className="text-sm text-blue-800">
          For a better assessment experience, use the <Link to={`/tenant/${tenantId}/dashboard`} className="font-medium underline">Dashboard</Link> to navigate by domain. 
          Each domain page shows controls with descriptions, framework mappings, and progress tracking.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
        <input className="border rounded p-2" placeholder="Domain (e.g., NET)" value={domain} onChange={e=>setFilter('domain', e.target.value)} />
        <input className="border rounded p-2" placeholder="Status (Complete/InProgress/NotStarted)" value={status} onChange={e=>setFilter('status', e.target.value)} />
        <input className="border rounded p-2 md:col-span-2" placeholder="Search (q)" value={q} onChange={e=>setFilter('q', e.target.value)} />
      </div>
      {loading && <div className="text-gray-500">Loading…</div>}

      <div className="overflow-x-auto rounded border bg-white">
        <table className="w-full text-left">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map(hg => (
              <tr key={hg.id}>
                {hg.headers.map(h => (
                  <th key={h.id} className="p-2 text-sm font-medium text-gray-600">
                    {flexRender(h.column.columnDef.header, h.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(r => (
              <tr key={r.id} className="border-t">
                {r.getVisibleCells().map(c => (
                  <td key={c.id} className="p-2 text-sm text-gray-800">
                    {flexRender(c.column.columnDef.cell, c.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="space-y-2">
        <div className="text-sm text-gray-700 font-medium">Import CSV</div>
        {error && <div className="text-sm text-red-700 bg-red-50 border border-red-200 p-2 rounded">{error}</div>}
        {okMsg && <div className="text-sm text-green-700 bg-green-50 border border-green-200 p-2 rounded">{okMsg}</div>}
        <textarea className="w-full h-40 border rounded p-2 font-mono" value={csv} onChange={e=>setCsv(e.target.value)} placeholder={`Paste CSV here. Header must be:\n${REQUIRED_HEADERS.join(',')}`} />
        <div>
          <button onClick={submitCsv} className="px-3 py-2 bg-blue-600 text-white rounded">Import</button>
        </div>
      </div>
    </div>
  )
}
