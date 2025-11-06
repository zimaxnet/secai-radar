import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getControlsByDomain, getDomains, getGaps } from '../api'

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

    // Load domain info
    getDomains().then(domains => {
      if (!mounted) return
      const domain = domains.find((d: any) => d.code === domainCode)
      setDomainInfo(domain)
    })

    // Load controls for this domain
    getControlsByDomain(tenantId, domainCode).then(d => {
      if (!mounted) return
      setControls(d.items || [])
    })

    // Load gaps for all controls
    getGaps(tenantId).then(d => {
      if (!mounted) return
      const gapsMap: Record<string, any> = {}
      d.items?.forEach((g: any) => {
        if (g.DomainPartition?.endsWith(`|${domainCode}`) || g.ControlID?.startsWith(`SEC-${domainCode}-`)) {
          gapsMap[g.ControlID] = g
        }
      })
      setGaps(gapsMap)
    })

    setLoading(false)
    return () => { mounted = false }
  }, [tenantId, domainCode])

  if (!domainCode) return <div>Domain not specified</div>

  const domainName = domainInfo?.name || domainCode
  const description = DOMAIN_DESCRIPTIONS[domainCode] || "Security domain for comprehensive assessment."
  const frameworks = FRAMEWORKS[domainCode] || []

  // Filter controls by status
  const filteredControls = statusFilter
    ? controls.filter(c => (c.Status || '').toLowerCase() === statusFilter.toLowerCase())
    : controls

  // Calculate progress
  const totalControls = controls.length
  const completeControls = controls.filter(c => (c.Status || '').toLowerCase() === 'complete').length
  const inProgressControls = controls.filter(c => (c.Status || '').toLowerCase() === 'inprogress').length
  const notStartedControls = controls.filter(c => !c.Status || (c.Status || '').toLowerCase() === 'notstarted').length
  const progressPercent = totalControls > 0 ? (completeControls / totalControls) * 100 : 0

  // Calculate domain-level gaps
  const domainGaps = Object.values(gaps).filter((g: any) => 
    (g.HardGaps?.length || 0) + (g.SoftGaps?.length || 0) > 0
  ).length

  return (
    <div className="space-y-6">
      {/* Domain Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg p-6">
        <Link to={`/tenant/${tenantId}/assessment`} className="text-blue-200 hover:text-white text-sm mb-2 inline-block">
          ← Back to Assessment Overview
        </Link>
        <h1 className="text-3xl font-bold mb-2">{domainCode}: {domainName}</h1>
        <p className="text-blue-100 text-lg">{description}</p>
        
        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span>Domain Progress</span>
            <span className="font-semibold">{progressPercent.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-blue-900 rounded-full h-3">
            <div 
              className="bg-white rounded-full h-3 transition-all"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="flex gap-4 mt-3 text-sm">
            <span>Complete: {completeControls}</span>
            <span>In Progress: {inProgressControls}</span>
            <span>Not Started: {notStartedControls}</span>
            <span>Total: {totalControls}</span>
          </div>
        </div>
      </div>

      {/* Framework Mappings */}
      {frameworks.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-yellow-900 mb-2">Mapped Frameworks</h2>
          <div className="flex flex-wrap gap-2">
            {frameworks.map((framework, idx) => (
              <span key={idx} className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                {framework}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Domain Gaps Summary */}
      {domainGaps > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-red-900 mb-2">Domain Gaps</h2>
          <p className="text-sm text-red-800">
            {domainGaps} control{domainGaps !== 1 ? 's' : ''} with identified gaps requiring attention.
          </p>
        </div>
      )}

      {/* Controls List */}
      <div className="bg-white border rounded-lg">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Controls</h2>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="border rounded px-3 py-1 text-sm"
          >
            <option value="">All Statuses</option>
            <option value="complete">Complete</option>
            <option value="inprogress">In Progress</option>
            <option value="notstarted">Not Started</option>
          </select>
        </div>

        {loading ? (
          <div className="p-4 text-gray-500">Loading controls...</div>
        ) : filteredControls.length === 0 ? (
          <div className="p-4 text-gray-500">No controls found for this domain.</div>
        ) : (
          <div className="divide-y">
            {filteredControls.map((control) => {
              const controlGaps = gaps[control.RowKey || control.ControlID]
              const hasGaps = controlGaps && (
                (controlGaps.HardGaps?.length || 0) + (controlGaps.SoftGaps?.length || 0) > 0
              )
              const coverage = controlGaps?.Coverage || 0
              const status = (control.Status || '').toLowerCase()

              return (
                <Link
                  key={control.RowKey || control.ControlID}
                  to={`/tenant/${tenantId}/control/${control.RowKey || control.ControlID}`}
                  className="block p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-gray-900">{control.RowKey || control.ControlID}</span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          status === 'complete' ? 'bg-green-100 text-green-800' :
                          status === 'inprogress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {control.Status || 'Not Started'}
                        </span>
                        {hasGaps && (
                          <span className="px-2 py-1 rounded text-xs bg-red-100 text-red-800">
                            Has Gaps
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-700 mt-1">{control.ControlTitle}</div>
                      {control.Owner && (
                        <div className="text-xs text-gray-500 mt-1">Owner: {control.Owner}</div>
                      )}
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-sm text-gray-600">Coverage</div>
                      <div 
                        className="text-lg font-bold"
                        style={{ 
                          color: coverage >= 0.7 ? 'green' : coverage >= 0.5 ? 'orange' : 'red' 
                        }}
                      >
                        {(coverage * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

