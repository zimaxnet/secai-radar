import { useState, useEffect, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Link, useParams, Navigate } from 'react-router-dom'

// Lazy load route components for code splitting
const Dashboard = lazy(() => import('./routes/Dashboard'))
const Controls = lazy(() => import('./routes/Controls'))
const Tools = lazy(() => import('./routes/Tools'))
const Gaps = lazy(() => import('./routes/Gaps'))

function Shell() {
  const { id } = useParams()
  const tenantId = id || (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'
  const location = window.location.pathname
  
  const navLinks = [
    { path: `/tenant/${tenantId}/dashboard`, label: 'Dashboard' },
    { path: `/tenant/${tenantId}/controls`, label: 'Controls' },
    { path: `/tenant/${tenantId}/tools`, label: 'Tools' },
    { path: `/tenant/${tenantId}/gaps`, label: 'Gaps' },
  ]
  
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-slate-900">SecAI Radar</h1>
              <span className="ml-3 text-sm text-slate-500">Tenant: {tenantId}</span>
            </div>
            <nav className="flex items-center space-x-1">
              {navLinks.map((link) => {
                const isActive = location === link.path || location.startsWith(link.path + '/')
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-slate-900 text-white'
                        : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    {link.label}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Suspense fallback={
          <div className="flex items-center justify-center py-12">
            <div className="spinner"></div>
            <span className="ml-3 text-slate-600">Loading...</span>
          </div>
        }>
          <Routes>
            <Route path="dashboard" element={<Dashboard tenantId={tenantId} />} />
            <Route path="controls" element={<Controls tenantId={tenantId} />} />
            <Route path="tools" element={<Tools tenantId={tenantId} />} />
            <Route path="gaps" element={<Gaps tenantId={tenantId} />} />
            <Route path="*" element={<Navigate to={`/tenant/${tenantId}/dashboard`} replace />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  )
}

function Home() {
  const [domains, setDomains] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    setLoading(true)
    fetch('/api/domains').then(r => r.json()).then(d => {
      setDomains(d || [])
    }).finally(() => setLoading(false))
  }, [])
  
  const defaultTenant = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'
  
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full card p-8">
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">SecAI Radar</h1>
        <p className="text-slate-600 mb-8">Cloud security assessment platform</p>
        
        {loading && (
          <div className="flex items-center py-4">
            <div className="spinner"></div>
            <span className="ml-3 text-slate-600">Loading...</span>
          </div>
        )}
        {domains.length > 0 && (
          <div className="mb-6 p-4 bg-slate-50 rounded-md">
            <p className="text-sm font-medium text-slate-700 mb-3">API Status: Connected</p>
            <p className="text-sm text-slate-600 mb-2">Found {domains.length} security domains:</p>
            <ul className="space-y-1 text-sm text-slate-600">
              {domains.slice(0, 3).map((d: any) => (
                <li key={d.code} className="flex items-center">
                  <span className="w-2 h-2 bg-slate-400 rounded-full mr-2"></span>
                  <span className="font-medium">{d.code}</span>: {d.name}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <a 
          href={`/tenant/${defaultTenant}/dashboard`}
          className="btn-primary inline-flex items-center"
        >
          Go to Dashboard
          <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </a>
      </div>
    </div>
  )
}

function App() {
  const defaultTenant = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tenant/:id/*" element={<Shell />} />
        <Route path="*" element={<Navigate to={`/tenant/${defaultTenant}/dashboard`} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

