import { useEffect, useMemo, useState } from 'react'
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
  return REQUIRED_HEADERS.every((h, i) => arr[i] === h)
}, { message: `CSV header must be: ${REQUIRED_HEADERS.join(',')}` })

const getStatusBadge = (status: string) => {
  const statusLower = status?.toLowerCase() || ''
  if (statusLower === 'complete') return 'badge-success'
  if (statusLower === 'inprogress' || statusLower === 'in progress') return 'badge-warning'
  if (statusLower === 'notstarted' || statusLower === 'not started') return 'badge-error'
  return 'badge-neutral'
}

export default function Controls({ tenantId }: Props) {
  const [rows, setRows] = useState<ControlRow[]>([])
  const [csv, setCsv] = useState('')
  const [loading, setLoading] = useState(false)
  const [params, setParams] = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const [okMsg, setOkMsg] = useState<string | null>(null)
  const [showImport, setShowImport] = useState(false)

  const domain = params.get('domain') || ''
  const status = params.get('status') || ''
  const q = params.get('q') || ''

  useEffect(() => {
    let mounted = true
    setLoading(true)
    getControls(tenantId, { domain: domain || undefined, status: status || undefined, q: q || undefined }).then(d => {
      if (!mounted) return
      setRows(d.items || [])
    }).finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tenantId, domain, status, q])

  const columns = useMemo<ColumnDef<ControlRow>[]>(() => ([
    { 
      header: 'Control ID', 
      accessorKey: 'RowKey',
      cell: (info) => <span className="font-mono text-sm">{info.getValue() as string}</span>
    },
    { 
      header: 'Domain', 
      accessorKey: 'Domain',
      cell: (info) => <span className="badge badge-neutral">{info.getValue() as string}</span>
    },
    { 
      header: 'Title', 
      accessorKey: 'ControlTitle',
      cell: (info) => <span className="text-slate-900">{info.getValue() as string}</span>
    },
    { 
      header: 'Status', 
      accessorKey: 'Status',
      cell: (info) => {
        const status = info.getValue() as string
        return <span className={`badge ${getStatusBadge(status)}`}>{status}</span>
      }
    },
    { 
      header: 'Owner', 
      accessorKey: 'Owner',
      cell: (info) => <span className="text-slate-600">{info.getValue() as string || '-'}</span>
    },
  ]), [])

  const table = useReactTable({ 
    data: rows, 
    columns, 
    getCoreRowModel: getCoreRowModel() 
  })

  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value); else next.delete(key)
    setParams(next, { replace: true })
  }

  const submitCsv = async () => {
    setError(null); setOkMsg(null)
    const headerLine = (csv.split(/\r?\n/).find(l => l.trim().length > 0) || '').trim()
    const headerArr = headerLine.split(',').map(s => s.trim())
    const parsed = headerSchema.safeParse(headerArr)
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message || 'Invalid CSV header')
      return
    }
    try {
      await importControls(tenantId, csv)
      setCsv('')
      setOkMsg('Controls imported successfully')
      setShowImport(false)
      // Refresh data
      const d = await getControls(tenantId, { domain: domain || undefined, status: status || undefined, q: q || undefined })
      setRows(d.items || [])
    } catch (err) {
      setError('Failed to import controls')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Controls</h1>
          <p className="mt-1 text-sm text-slate-600">Security control assessment and management</p>
        </div>
        <button
          onClick={() => setShowImport(!showImport)}
          className="btn-secondary"
        >
          {showImport ? 'Cancel Import' : 'Import CSV'}
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Domain</label>
            <input
              className="input-field"
              placeholder="e.g., NET"
              value={domain}
              onChange={e => setFilter('domain', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
            <input
              className="input-field"
              placeholder="Complete, InProgress, NotStarted"
              value={status}
              onChange={e => setFilter('status', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Search</label>
            <input
              className="input-field"
              placeholder="Search controls..."
              value={q}
              onChange={e => setFilter('q', e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Import Section */}
      {showImport && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Import Controls</h2>
          {error && <div className="alert alert-error mb-4">{error}</div>}
          {okMsg && <div className="alert alert-success mb-4">{okMsg}</div>}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                CSV Content
                <span className="ml-2 text-xs text-slate-500">(Header: {REQUIRED_HEADERS.join(', ')})</span>
              </label>
              <textarea
                className="w-full h-48 input-field font-mono text-xs"
                value={csv}
                onChange={e => setCsv(e.target.value)}
                placeholder={`Paste CSV here. Header must be:\n${REQUIRED_HEADERS.join(',')}`}
              />
            </div>
            <div className="flex items-center gap-3">
              <button onClick={submitCsv} className="btn-primary" disabled={!csv.trim()}>
                Import Controls
              </button>
              <button onClick={() => { setCsv(''); setError(null); setOkMsg(null) }} className="btn-secondary">
                Clear
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Control List</h2>
            <span className="text-sm text-slate-600">{rows.length} controls</span>
          </div>
        </div>
        {loading ? (
          <div className="card-body">
            <div className="flex items-center justify-center py-12">
              <div className="spinner"></div>
              <span className="ml-3 text-slate-600">Loading...</span>
            </div>
          </div>
        ) : rows.length === 0 ? (
          <div className="card-body">
            <div className="text-center py-12">
              <p className="text-slate-600">No controls found</p>
              <p className="text-sm text-slate-500 mt-1">Try adjusting your filters</p>
            </div>
          </div>
        ) : (
          <div className="table-container">
            <table className="w-full">
              <thead className="table-header">
                {table.getHeaderGroups().map(hg => (
                  <tr key={hg.id}>
                    {hg.headers.map(h => (
                      <th key={h.id} className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                        {flexRender(h.column.columnDef.header, h.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {table.getRowModel().rows.map(r => (
                  <tr key={r.id} className="table-row">
                    {r.getVisibleCells().map(c => (
                      <td key={c.id} className="px-6 py-4 whitespace-nowrap text-sm">
                        {flexRender(c.column.columnDef.cell, c.getContext())}
                      </td>
                    ))}
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
