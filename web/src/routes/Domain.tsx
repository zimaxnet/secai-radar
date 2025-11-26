import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getControlsByDomain, getDomains, getGaps } from '../api'
import PageHeader from '../components/ui/PageHeader'
import GlassCard from '../components/ui/GlassCard'

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
  NET: ["CIS Controls 13", "NIST CSF PR.AC-5", "Azure Security Benchmark NS-1"],
  ID: ["CIS Controls 5-6", "NIST CSF PR.AC-1", "Azure Security Benchmark IM-1"],
  PA: ["CIS Controls 4", "NIST CSF PR.AC-4", "Azure Security Benchmark PA-1"],
  DATA: ["CIS Controls 13", "NIST CSF PR.DS-1", "Azure Security Benchmark DP-1"],
  ASSET: ["CIS Controls 1-2", "NIST CSF ID.AM-1", "Azure Security Benchmark AM-1"],
  LOG: ["CIS Controls 6", "NIST CSF DE.AE-1", "Azure Security Benchmark LT-1"],
  IR: ["CIS Controls 17", "NIST CSF RS.RP-1", "Azure Security Benchmark IR-1"],
  POST: ["CIS Controls 3", "NIST CSF PR.IP-1", "Azure Security Benchmark PV-1"],
  END: ["CIS Controls 8", "NIST CSF PR.DS-2", "Azure Security Benchmark ES-1"],
  BAK: ["CIS Controls 11", "NIST CSF RC.RP-1", "Azure Security Benchmark BR-1"],
  DEV: ["CIS Controls 18", "NIST CSF PR.IP-7", "Azure Security Benchmark DS-1"],
  GOV: ["CIS Controls 20", "NIST CSF GV.RM-1", "Azure Security Benchmark GS-1"]
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
  const [domainInfo, setDomainInfo] = useState<any>(null)
  const [gaps, setGaps] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    if (!domainCode) return
    let mounted = true
    setLoading(true)

    Promise.all([
      getDomains(),
      getControlsByDomain(tenantId, domainCode),
      getGaps(tenantId)
    ]).then(([domains, controlsData, gapsData]) => {
      if (!mounted) return
      const domain = domains.find((d: any) => d.code === domainCode)
      setDomainInfo(domain)
      setControls(controlsData.items || [])
      
      const gapsMap: Record<string, any> = {}
      gapsData.items?.forEach((g: any) => {
        if (g.DomainPartition?.endsWith(`|${domainCode}`) || g.ControlID?.startsWith(`SEC-${domainCode}-`)) {
          gapsMap[g.ControlID] = g
        }
      })
      setGaps(gapsMap)
    }).finally(() => {
      if (mounted) setLoading(false)
    })

    return () => { mounted = false }
  }, [tenantId, domainCode])

  if (!domainCode) return <div className="text-red-500">Domain not specified</div>

  const domainName = domainInfo?.name || domainCode
  const description = DOMAIN_DESCRIPTIONS[domainCode] || "Security domain assessment."
  const frameworks = FRAMEWORKS[domainCode] || []

  const filteredControls = statusFilter
    ? controls.filter(c => (c.Status || '').toLowerCase() === statusFilter.toLowerCase())
    : controls

  return (
    <div className="space-y-8">
      <PageHeader 
        title={`${domainCode}: ${domainName}`} 
        subtitle={description}
        parentLink={{ to: `/tenant/${tenantId}/dashboard`, label: 'Dashboard' }}
      />

      {/* Framework Tags */}
      {frameworks.length > 0 && (
        <div className="flex flex-wrap gap-2 -mt-4 mb-8">
          {frameworks.map((fw, idx) => (
            <span key={idx} className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs text-slate-400 font-mono">
              {fw}
            </span>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex justify-end">
        <div className="bg-slate-900/50 p-1 rounded-lg border border-white/5 flex gap-1">
          {['', 'Not Started', 'In Progress', 'Complete'].map(status => (
            <button
              key={status}
              onClick={() => setStatusFilter(status === 'Not Started' ? 'notstarted' : status === 'In Progress' ? 'inprogress' : status === 'Complete' ? 'complete' : '')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                (status === '' && !statusFilter) || (status.toLowerCase().replace(' ', '') === statusFilter)
                  ? 'bg-blue-600 text-white shadow-sm' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {status || 'All Controls'}
            </button>
          ))}
        </div>
      </div>

      {/* Controls Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="h-48 bg-slate-900/50 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredControls.map((control) => {
            const controlGaps = gaps[control.RowKey || control.ControlID]
            const coverage = controlGaps?.Coverage || 0
            const status = (control.Status || 'Not Started')
            
            return (
              <Link key={control.RowKey} to={`/tenant/${tenantId}/control/${control.RowKey}`}>
                <GlassCard hoverEffect className="h-full p-5 flex flex-col">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <ProgressRing percent={Math.round(coverage * 100)} />
                      <div>
                        <div className="font-mono text-xs text-blue-400">{control.RowKey}</div>
                        <div className="text-xs text-slate-500 mt-0.5">{control.Owner || 'Unassigned'}</div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide border ${
                      status === 'Complete' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                      status === 'In Progress' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                      'bg-slate-800 text-slate-400 border-slate-700'
                    }`}>
                      {status}
                    </span>
                  </div>
                  
                  <h3 className="text-white font-medium mb-2 line-clamp-2 min-h-[3rem]">
                    {control.ControlTitle}
                  </h3>
                  
                  <p className="text-sm text-slate-400 line-clamp-3 flex-1">
                    {control.ControlDescription}
                  </p>

                  <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center">
                    <span className="text-xs text-slate-500">Click to assess →</span>
                    {controlGaps && (
                      <div className="flex gap-1">
                        {(controlGaps.HardGaps?.length || 0) > 0 && <div className="h-2 w-2 rounded-full bg-red-500" title="Hard Gaps" />}
                        {(controlGaps.SoftGaps?.length || 0) > 0 && <div className="h-2 w-2 rounded-full bg-orange-500" title="Soft Gaps" />}
                      </div>
                    )}
                  </div>
                </GlassCard>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
