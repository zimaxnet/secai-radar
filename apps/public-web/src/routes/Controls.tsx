import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getControls, importControls, isDemoMode } from '../api'
import { DOMAINS } from '../demoData'
import { ColumnDef, flexRender, getCoreRowModel, useReactTable, getSortedRowModel, SortingState } from '@tanstack/react-table'
import { z } from 'zod'
import GlassCard from '../components/ui/GlassCard'
import PageHeader from '../components/ui/PageHeader'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface Props { tenantId: string }
interface ControlRow { [k: string]: any }

const REQUIRED_HEADERS = [
  'ControlID', 'Domain', 'ControlTitle', 'ControlDescription', 'Question', 'RequiredEvidence',
  'Status', 'Owner', 'Frequency', 'ScoreNumeric', 'Weight', 'Notes', 'SourceRef', 'Tags', 'UpdatedAt'
] as const

const headerSchema = z.array(z.string()).refine(arr => {
  if (arr.length < REQUIRED_HEADERS.length) return false
  return REQUIRED_HEADERS.every((h, i) => arr[i] === h)
}, { message: `CSV header must be: ${REQUIRED_HEADERS.join(',')}` })

const STATUS_COLORS: Record<string, string> = {
  Complete: '#10b981',
  InProgress: '#f59e0b',
  NotStarted: '#ef4444'
}

export default function Controls({ tenantId }: Props) {
  const [rows, setRows] = useState<ControlRow[]>([])
  const [csv, setCsv] = useState('')
  const [loading, setLoading] = useState(false)
  const [params, setParams] = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const [okMsg, setOkMsg] = useState<string | null>(null)
  const [sorting, setSorting] = useState<SortingState>([])
  const [showImport, setShowImport] = useState(false)

  const domain = params.get('domain') || ''
  const status = params.get('status') || ''
  const q = params.get('q') || ''

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    getControls(tenantId, { domain: domain || undefined, status: status || undefined, q: q || undefined })
      .then(d => {
        if (!mounted) return
        // Handle both API response formats
        const items = d.items || []
        setRows(items.map((item: any) => ({
          ...item,
          // Normalize field names for demo data vs API data
          RowKey: item.RowKey || item.ControlID,
          Domain: item.Domain || item.DomainCode,
          ControlTitle: item.ControlTitle,
          Status: item.Status
        })))
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

  // Summary stats
  const stats = useMemo(() => {
    const complete = rows.filter(r => r.Status === 'Complete').length
    const inProgress = rows.filter(r => r.Status === 'InProgress').length
    const notStarted = rows.filter(r => r.Status === 'NotStarted').length
    return { complete, inProgress, notStarted, total: rows.length }
  }, [rows])

  const pieData = [
    { name: 'Complete', value: stats.complete, color: STATUS_COLORS.Complete },
    { name: 'In Progress', value: stats.inProgress, color: STATUS_COLORS.InProgress },
    { name: 'Not Started', value: stats.notStarted, color: STATUS_COLORS.NotStarted }
  ].filter(d => d.value > 0)

  const columns = useMemo<ColumnDef<ControlRow>[]>(() => ([
    {
      header: 'Control ID',
      accessorKey: 'RowKey',
      cell: ({ row }) => {
        const controlId = row.original.RowKey || row.original.ControlID;
        return (
          <Link
            to={`/tenant/${tenantId}/control/${controlId}`}
            className="text-blue-400 hover:text-blue-300 font-mono text-sm font-medium"
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
        const domainCode = row.original.Domain || row.original.DomainCode || row.original.PartitionKey?.split('|')[1] || '';
        return (
          <Link
            to={`/tenant/${tenantId}/domain/${domainCode}`}
            className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300 hover:bg-slate-700 transition-colors"
          >
            {domainCode}
          </Link>
        );
      }
    },
    {
      header: 'Title',
      accessorKey: 'ControlTitle',
      cell: ({ row }) => (
        <span className="text-slate-200 text-sm line-clamp-1 max-w-xs">{row.original.ControlTitle}</span>
      )
    },
    {
      header: 'Status',
      accessorKey: 'Status',
      cell: ({ row }) => {
        const s = row.original.Status || 'NotStarted'
        const colors: Record<string, string> = {
          Complete: 'bg-green-500/20 text-green-400 border-green-500/30',
          InProgress: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
          NotStarted: 'bg-red-500/20 text-red-400 border-red-500/30'
        }
        return (
          <span className={`px-2 py-1 rounded text-xs font-medium border ${colors[s] || colors.NotStarted}`}>
            {s === 'InProgress' ? 'In Progress' : s === 'NotStarted' ? 'Not Started' : s}
          </span>
        )
      }
    },
    {
      header: 'Criticality',
      accessorKey: 'Criticality',
      cell: ({ row }) => {
        const c = row.original.Criticality || 'Medium'
        const colors: Record<string, string> = {
          High: 'text-red-400',
          Medium: 'text-yellow-400',
          Low: 'text-green-400'
        }
        return <span className={`text-xs ${colors[c] || colors.Medium}`}>{c}</span>
      }
    },
    {
      header: 'Reference',
      accessorKey: 'SourceRef',
      cell: ({ row }) => {
        const ref = row.original.SourceRef;
        if (!ref || !ref.trim()) return <span className="text-slate-600">-</span>;
        if (ref.trim().startsWith('http://') || ref.trim().startsWith('https://')) {
          return (
            <a
              href={ref.trim()}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 text-xs"
              title={ref.trim()}
            >
              🔗 Link
            </a>
          );
        }
        return <span className="text-xs text-slate-500 truncate max-w-[100px]">{ref}</span>;
      }
    },
  ]), [tenantId])

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: { sorting }
  })

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
      const headerLine = (csv.split(/\r?\n/).find(l => l.trim().length > 0) || '').trim()
      const headerArr = headerLine.split(',').map(s => s.trim())
      const parsed = headerSchema.safeParse(headerArr)
      if (!parsed.success) {
        setError(parsed.error.issues[0]?.message || 'Invalid CSV header')
        setLoading(false)
        return
      }

      await importControls(tenantId, csv)

      try {
        const data = await getControls(tenantId, { domain: domain || undefined, status: status || undefined, q: q || undefined })
        setRows(data.items || [])
        setCsv('')
        setOkMsg('Imported successfully')
        setShowImport(false)
      } catch (refreshError) {
        setError(`Import succeeded, but failed to refresh data: ${refreshError instanceof Error ? refreshError.message : 'Unknown error'}`)
      }
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : 'Failed to import controls')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Controls"
        subtitle="View and manage all security controls across domains"
        action={
          <div className="flex items-center gap-3">
            {isDemoMode() && (
              <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-medium border border-yellow-500/30">
                Demo Mode
              </span>
            )}
            <button
              onClick={() => setShowImport(!showImport)}
              className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg font-medium hover:bg-slate-700 transition-colors flex items-center gap-2 border border-white/10"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Import CSV
            </button>
          </div>
        }
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-5 gap-4">
        <GlassCard className="p-5">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">Total</div>
          <div className="text-3xl font-bold text-white">{stats.total}</div>
        </GlassCard>
        <GlassCard className="p-5">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">Complete</div>
          <div className="text-3xl font-bold text-green-400">{stats.complete}</div>
        </GlassCard>
        <GlassCard className="p-5">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">In Progress</div>
          <div className="text-3xl font-bold text-yellow-400">{stats.inProgress}</div>
        </GlassCard>
        <GlassCard className="p-5">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">Not Started</div>
          <div className="text-3xl font-bold text-red-400">{stats.notStarted}</div>
        </GlassCard>
        <GlassCard className="p-5 flex items-center justify-center">
          <div className="h-[80px] w-[80px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={20} outerRadius={35} paddingAngle={2} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Domain</label>
            <select
              className="w-full px-3 py-2 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500 text-sm"
              value={domain}
              onChange={e => setFilter('domain', e.target.value)}
            >
              <option value="">All Domains</option>
              {Object.entries(DOMAINS).map(([code, name]) => (
                <option key={code} value={code}>{code} - {name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Status</label>
            <select
              className="w-full px-3 py-2 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500 text-sm"
              value={status}
              onChange={e => setFilter('status', e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="Complete">Complete</option>
              <option value="InProgress">In Progress</option>
              <option value="NotStarted">Not Started</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="block text-xs text-slate-500 mb-1">Search</label>
            <input
              className="w-full px-3 py-2 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500 text-sm placeholder-slate-500"
              placeholder="Search by ID or title..."
              value={q}
              onChange={e => setFilter('q', e.target.value)}
            />
          </div>
        </div>
      </GlassCard>

      {/* Import Form */}
      {showImport && (
        <GlassCard className="p-6">
          <h3 className="text-slate-300 font-semibold mb-4">Import Controls from CSV</h3>
          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">{error}</div>
          )}
          {okMsg && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">{okMsg}</div>
          )}
          <textarea
            className="w-full h-40 px-4 py-3 bg-slate-800/50 border border-white/10 rounded-lg text-slate-200 font-mono text-sm focus:outline-none focus:border-blue-500 resize-none"
            value={csv}
            onChange={e => setCsv(e.target.value)}
            placeholder={`Paste CSV here. Header must be:\n${REQUIRED_HEADERS.join(',')}`}
          />
          <div className="flex gap-3 mt-4">
            <button
              onClick={submitCsv}
              disabled={loading || !csv.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Importing...' : 'Import CSV'}
            </button>
            <button
              onClick={() => setShowImport(false)}
              className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg font-medium hover:bg-slate-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </GlassCard>
      )}

      {/* Controls Table */}
      <GlassCard className="overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : rows.length === 0 ? (
          <div className="text-center py-20 text-slate-500">
            No controls found. Try adjusting your filters or import controls via CSV.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                {table.getHeaderGroups().map(hg => (
                  <tr key={hg.id} className="border-b border-white/10">
                    {hg.headers.map(h => (
                      <th
                        key={h.id}
                        onClick={h.column.getToggleSortingHandler()}
                        className="text-left py-4 px-4 text-slate-400 font-medium text-xs uppercase tracking-wider cursor-pointer hover:text-white transition-colors"
                      >
                        <div className="flex items-center gap-1">
                          {flexRender(h.column.columnDef.header, h.getContext())}
                          {{
                            asc: ' ↑',
                            desc: ' ↓',
                          }[h.column.getIsSorted() as string] ?? null}
                        </div>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map(r => (
                  <tr key={r.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    {r.getVisibleCells().map(c => (
                      <td key={c.id} className="py-3 px-4">
                        {flexRender(c.column.columnDef.cell, c.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="p-4 border-t border-white/10 text-sm text-slate-500">
          Showing {rows.length} control{rows.length !== 1 ? 's' : ''}
          {(domain || status || q) && ' (filtered)'}
        </div>
      </GlassCard>

      {/* Quick Navigation */}
      <GlassCard className="p-6">
        <h3 className="text-slate-300 font-semibold mb-4">Quick Navigation by Domain</h3>
        <div className="grid grid-cols-4 gap-3">
          {Object.entries(DOMAINS).map(([code, name]) => {
            const count = rows.filter(r => (r.Domain || r.DomainCode) === code).length
            return (
              <Link
                key={code}
                to={`/tenant/${tenantId}/domain/${code}`}
                className="p-3 bg-slate-800/50 hover:bg-slate-800 rounded-lg border border-white/5 hover:border-white/10 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-blue-400 font-medium group-hover:text-blue-300">{code}</span>
                  <span className="text-xs text-slate-500">{count > 0 ? `${count} controls` : ''}</span>
                </div>
                <div className="text-xs text-slate-500 mt-1 truncate">{name}</div>
              </Link>
            )
          })}
        </div>
      </GlassCard>
    </div>
  )
}
