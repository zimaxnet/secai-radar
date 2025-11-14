import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getSummary } from '../api'

interface Assessment {
  tenantId: string
  name: string
  lastUpdated: string
  progress: number
  status: 'not_started' | 'in_progress' | 'review' | 'complete'
  totalControls: number
  completeControls: number
}

export default function Assessments() {
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newTenantName, setNewTenantName] = useState('')
  const [newTenantId, setNewTenantId] = useState('')
  const navigate = useNavigate()

  // For MVP, we'll use a default tenant and show it as an assessment
  // In production, this would list all tenants from an API
  useEffect(() => {
    setLoading(true)
    // Check if we have data for default tenant
    const defaultTenant = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'CONTOSO'
    
    getSummary(defaultTenant).then(d => {
      const totalControls = d.byDomain?.reduce((sum: number, domain: any) => sum + (domain.total || 0), 0) || 0
      const completeControls = d.byDomain?.reduce((sum: number, domain: any) => sum + (domain.complete || 0), 0) || 0
      const progress = totalControls > 0 ? (completeControls / totalControls) * 100 : 0
      
      setAssessments([{
        tenantId: defaultTenant,
        name: defaultTenant,
        lastUpdated: new Date().toISOString(),
        progress: progress,
        status: progress === 0 ? 'not_started' : progress === 100 ? 'complete' : 'in_progress',
        totalControls: totalControls,
        completeControls: completeControls
      }])
    }).catch(() => {
      // If no data, show empty state with option to create
      setAssessments([])
    }).finally(() => {
      setLoading(false)
    })
  }, [])

  const handleCreateAssessment = () => {
    if (!newTenantName.trim()) {
      alert('Please enter a customer/organization name')
      return
    }
    
    const tenantId = newTenantId.trim() || newTenantName.toUpperCase().replace(/\s+/g, '-').substring(0, 10)
    
    // For MVP, navigate to setup. In production, create tenant via API first
    navigate(`/tenant/${tenantId}/setup`)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'review': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'complete': return 'Complete'
      case 'in_progress': return 'In Progress'
      case 'review': return 'Under Review'
      default: return 'Not Started'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link to="/" className="text-blue-600 hover:underline text-sm mb-4 inline-block">
            ← Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Assessments</h1>
          <p className="text-gray-600">Select an existing assessment or start a new one</p>
        </div>

        {/* Create New Assessment */}
        <div className="mb-8">
          {!showCreateForm ? (
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
            >
              + Start New Assessment
            </button>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Assessment</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Customer/Organization Name *
                  </label>
                  <input
                    type="text"
                    value={newTenantName}
                    onChange={e => setNewTenantName(e.target.value)}
                    placeholder="e.g., Acme Corporation"
                    className="w-full border rounded-lg px-4 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tenant ID (optional, auto-generated if blank)
                  </label>
                  <input
                    type="text"
                    value={newTenantId}
                    onChange={e => setNewTenantId(e.target.value)}
                    placeholder="e.g., ACME"
                    className="w-full border rounded-lg px-4 py-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">Used to identify this assessment (alphanumeric, no spaces)</p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleCreateAssessment}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
                  >
                    Create & Continue
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateForm(false)
                      setNewTenantName('')
                      setNewTenantId('')
                    }}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Existing Assessments */}
        {loading ? (
          <div className="text-gray-500">Loading assessments...</div>
        ) : assessments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <div className="text-6xl mb-4">📋</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">No Assessments Yet</h2>
            <p className="text-gray-600 mb-6">
              Start your first SecAI Framework assessment to begin evaluating your Azure security posture.
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            >
              Start Your First Assessment
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assessments.map(assessment => (
              <Link
                key={assessment.tenantId}
                to={`/tenant/${assessment.tenantId}/assessment`}
                className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-2 border-transparent hover:border-blue-500"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-1">{assessment.name}</h3>
                    <p className="text-sm text-gray-500">Tenant ID: {assessment.tenantId}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(assessment.status)}`}>
                    {getStatusLabel(assessment.status)}
                  </span>
                </div>
                
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-semibold text-gray-900">{Math.round(assessment.progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 rounded-full h-3 transition-all"
                      style={{ width: `${assessment.progress}%` }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                  <div>
                    <div className="text-gray-500">Controls</div>
                    <div className="font-semibold text-gray-900">
                      {assessment.completeControls} / {assessment.totalControls}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Last Updated</div>
                    <div className="font-semibold text-gray-900">
                      {new Date(assessment.lastUpdated).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <div className="text-sm font-medium text-blue-600">
                    {assessment.status === 'complete' ? 'View Report →' : 'Continue Assessment →'}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

