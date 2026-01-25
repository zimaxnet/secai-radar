import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getControlsByDomain, getGaps, isDemoMode } from '../api'
import { DOMAINS } from '../demoData'
import PageHeader from '../components/ui/PageHeader'
import GlassCard from '../components/ui/GlassCard'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface Props { tenantId: string }

const DOMAIN_DESCRIPTIONS: Record<string, string> = {
  NET: "Network security controls focus on protecting network infrastructure, perimeter defense, traffic filtering, and secure network segmentation.",
  ID: "Identity management controls ensure proper authentication, authorization, account lifecycle management, and identity governance.",
  PA: "Privileged access controls manage elevated permissions, just-in-time access, and privileged account security.",
  DATA: "Data protection controls safeguard sensitive data through encryption, classification, and access controls.",
  ASSET: "Asset management controls track and manage IT assets, inventory, and configuration management.",
  LOG: "Logging and threat detection controls enable security monitoring, SIEM, log retention, and threat intelligence.",
  IR: "Incident response controls define processes for detecting, responding to, and recovering from security incidents.",
  POST: "Posture and vulnerability management controls assess and remediate security vulnerabilities and misconfigurations.",
  END: "Endpoint security controls protect devices, servers, and workstations from threats and unauthorized access.",
  BAK: "Backup and recovery controls ensure data availability, backup integrity, and disaster recovery capabilities.",
  DEV: "DevOps security controls integrate security into development pipelines, code scanning, and container security.",
  GOV: "Governance and strategy controls establish security policies, risk management, compliance, and security architecture."
}

const FRAMEWORKS: Record<string, string[]> = {
  NET: ["CIS Controls 13", "NIST CSF PR.AC-5", "Azure Security Benchmark NS-1", "PCI-DSS 1.x"],
  ID: ["CIS Controls 5-6", "NIST CSF PR.AC-1", "Azure Security Benchmark IM-1", "SOC 2 CC6.1"],
  PA: ["CIS Controls 4", "NIST CSF PR.AC-4", "Azure Security Benchmark PA-1", "SOC 2 CC6.2"],
  DATA: ["CIS Controls 13", "NIST CSF PR.DS-1", "Azure Security Benchmark DP-1", "GDPR Art. 32"],
  ASSET: ["CIS Controls 1-2", "NIST CSF ID.AM-1", "Azure Security Benchmark AM-1"],
  LOG: ["CIS Controls 6", "NIST CSF DE.AE-1", "Azure Security Benchmark LT-1", "PCI-DSS 10.x"],
  IR: ["CIS Controls 17", "NIST CSF RS.RP-1", "Azure Security Benchmark IR-1", "SOC 2 CC7.4"],
  POST: ["CIS Controls 3", "NIST CSF PR.IP-1", "Azure Security Benchmark PV-1"],
  END: ["CIS Controls 8", "NIST CSF PR.DS-2", "Azure Security Benchmark ES-1"],
  BAK: ["CIS Controls 11", "NIST CSF RC.RP-1", "Azure Security Benchmark BR-1"],
  DEV: ["CIS Controls 18", "NIST CSF PR.IP-7", "Azure Security Benchmark DS-1"],
  GOV: ["CIS Controls 20", "NIST CSF GV.RM-1", "Azure Security Benchmark GS-1", "ISO 27001 A.5"]
}

const STATUS_COLORS = {
  Complete: '#10b981',
  InProgress: '#f59e0b',
  NotStarted: '#ef4444'
}

const ProgressRing = ({ percent }: { percent: number }) => {
  const r = 18
  const c = 2 * Math.PI * r
  const offset = c - (percent / 100) * c
  const color = percent >= 80 ? 'text-green-500' : percent >= 50 ? 'text-yellow-500' : 'text-red-500'

  return (
    <div className="relative h-12 w-12 flex items-center justify-center">
      <svg className="h-full w-full -rotate-90" viewBox="0 0 48 48">
        <circle className="text-slate-800" strokeWidth="4" stroke="currentColor" fill="transparent" r={r} cx="24" cy="24" />
        <circle
          className={`${color} transition-all duration-1000 ease-out`}
          strokeWidth="4"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={r}
          cx="24"
          cy="24"
        />
      </svg>
      <span className="absolute text-[10px] font-bold text-slate-300">{percent}%</span>
    </div>
  )
}

export default function Domain({ tenantId }: Props) {
  const { domainCode } = useParams<{ domainCode: string }>()
  const [controls, setControls] = useState<any[]>([])
  const [gaps, setGaps] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    if (!domainCode) return
    let mounted = true
    setLoading(true)

    Promise.all([
      getControlsByDomain(tenantId, domainCode),
      getGaps(tenantId)
    ]).then(([controlsData, gapsData]) => {
      if (!mounted) return
      // Normalize controls data
      const items = (controlsData.items || []).map((c: any) => ({
        ...c,
        RowKey: c.RowKey || c.ControlID,
        Status: c.Status || 'NotStarted'
      }))
      setControls(items)

      // Build gaps map
      const gapsMap: Record<string, any> = {}
      gapsData.items?.forEach((g: any) => {
        const id = g.ControlID || g.RowKey
        if (id?.includes(`-${domainCode}-`)) {
          gapsMap[id] = g
        }
      })
      setGaps(gapsMap)
    }).finally(() => {
      if (mounted) setLoading(false)
    })

    return () => { mounted = false }
  }, [tenantId, domainCode])

  if (!domainCode) return <div className="text-red-500">Domain not specified</div>

  const domainName = DOMAINS[domainCode as keyof typeof DOMAINS] || domainCode
  const description = DOMAIN_DESCRIPTIONS[domainCode] || "Security domain assessment."
  const frameworks = FRAMEWORKS[domainCode] || []

  const filteredControls = statusFilter
    ? controls.filter(c => {
      const status = (c.Status || 'NotStarted').toLowerCase().replace(/\s+/g, '')
      return status === statusFilter.toLowerCase()
    })
    : controls

  // Calculate stats
  const stats = {
    total: controls.length,
    complete: controls.filter(c => c.Status === 'Complete').length,
    inProgress: controls.filter(c => c.Status === 'InProgress').length,
    notStarted: controls.filter(c => c.Status === 'NotStarted' || !c.Status).length
  }

  const pieData = [
    { name: 'Complete', value: stats.complete, color: STATUS_COLORS.Complete },
    { name: 'In Progress', value: stats.inProgress, color: STATUS_COLORS.InProgress },
    { name: 'Not Started', value: stats.notStarted, color: STATUS_COLORS.NotStarted }
  ].filter(d => d.value > 0)

  const completionRate = stats.total > 0 ? Math.round((stats.complete / stats.total) * 100) : 0

  return (
    <div className="space-y-6">
      <PageHeader
        title={`${domainCode}: ${domainName}`}
        subtitle={description}
        parentLink={{ to: `/tenant/${tenantId}/dashboard`, label: 'Dashboard' }}
        action={
          isDemoMode() && (
            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-medium border border-yellow-500/30">
              Demo Mode
            </span>
          )
        }
      />

      {/* Framework Tags */}
      {frameworks.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {frameworks.map((fw, idx) => (
            <span key={idx} className="px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700 text-xs text-slate-400 font-mono">
              {fw}
            </span>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-5 gap-4">
        <GlassCard className="p-5">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">Total Controls</div>
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
        <GlassCard className="p-5 flex items-center justify-between">
          <div>
            <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">Completion</div>
            <div className="text-3xl font-bold text-cyan-400">{completionRate}%</div>
          </div>
          <div className="h-[60px] w-[60px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={15} outerRadius={28} paddingAngle={2} dataKey="value">
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
      <div className="flex justify-between items-center">
        <div className="text-sm text-slate-500">
          Showing {filteredControls.length} of {controls.length} controls
        </div>
        <div className="bg-slate-900/50 p-1 rounded-lg border border-white/5 flex gap-1">
          {[
            { value: '', label: 'All' },
            { value: 'notstarted', label: 'Not Started' },
            { value: 'inprogress', label: 'In Progress' },
            { value: 'complete', label: 'Complete' }
          ].map(option => (
            <button
              key={option.value}
              onClick={() => setStatusFilter(option.value)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${statusFilter === option.value
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Controls Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-48 bg-slate-900/50 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : filteredControls.length === 0 ? (
        <GlassCard className="p-12 text-center">
          <div className="text-slate-500">No controls found for this filter.</div>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredControls.map((control) => {
            const controlId = control.RowKey || control.ControlID
            const controlGaps = gaps[controlId]
            const coverage = controlGaps?.Coverage ?? (control.ScoreNumeric ? control.ScoreNumeric / 100 : 0)
            const status = control.Status || 'NotStarted'

            return (
              <Link key={controlId} to={`/tenant/${tenantId}/control/${controlId}`}>
                <GlassCard hoverEffect className="h-full p-5 flex flex-col">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <ProgressRing percent={Math.round(coverage * 100)} />
                      <div>
                        <div className="font-mono text-xs text-blue-400">{controlId}</div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          {control.Criticality || 'Medium'} Priority
                        </div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide border ${status === 'Complete' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                        status === 'InProgress' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                          'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                      {status === 'InProgress' ? 'In Progress' : status === 'NotStarted' ? 'Not Started' : status}
                    </span>
                  </div>

                  <h3 className="text-white font-medium mb-2 line-clamp-2 min-h-[3rem]">
                    {control.ControlTitle}
                  </h3>

                  <p className="text-sm text-slate-400 line-clamp-2 flex-1">
                    {control.Observations || control.ControlDescription || 'No description available'}
                  </p>

                  <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center">
                    <span className="text-xs text-slate-500">Click to assess →</span>
                    <div className="flex gap-1">
                      {(controlGaps?.HardGaps?.length || 0) > 0 && (
                        <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px]">
                          {controlGaps.HardGaps.length} hard
                        </span>
                      )}
                      {(controlGaps?.SoftGaps?.length || 0) > 0 && (
                        <span className="px-1.5 py-0.5 bg-orange-500/20 text-orange-400 rounded text-[10px]">
                          {controlGaps.SoftGaps.length} soft
                        </span>
                      )}
                    </div>
                  </div>
                </GlassCard>
              </Link>
            )
          })}
        </div>
      )}

      {/* Quick Actions */}
      <GlassCard className="p-6">
        <h3 className="text-slate-300 font-semibold mb-4">Domain Actions</h3>
        <div className="flex gap-4">
          <Link
            to={`/tenant/${tenantId}/gaps`}
            className="flex-1 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-lg border border-white/5 hover:border-blue-500/30 transition-all text-center"
          >
            <div className="text-blue-400 font-semibold mb-1">View Gaps</div>
            <div className="text-xs text-slate-500">See all gaps for this domain</div>
          </Link>
          <Link
            to={`/tenant/${tenantId}/report`}
            className="flex-1 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-lg border border-white/5 hover:border-green-500/30 transition-all text-center"
          >
            <div className="text-green-400 font-semibold mb-1">Generate Report</div>
            <div className="text-xs text-slate-500">Create assessment report</div>
          </Link>
          <Link
            to={`/tenant/${tenantId}/tools`}
            className="flex-1 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-lg border border-white/5 hover:border-purple-500/30 transition-all text-center"
          >
            <div className="text-purple-400 font-semibold mb-1">Tool Coverage</div>
            <div className="text-xs text-slate-500">See tool-capability matrix</div>
          </Link>
        </div>
      </GlassCard>
    </div>
  )
}
