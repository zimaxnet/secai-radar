import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link, useParams, Navigate } from 'react-router-dom'
import Dashboard from './routes/Dashboard'
import Controls from './routes/Controls'
import Tools from './routes/Tools'
import Gaps from './routes/Gaps'

function Shell() {
  const { id } = useParams()
  const tenantId = id || (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-4">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">SecAI Radar</h1>
          <nav className="flex gap-4 text-blue-600">
            <Link to={`/tenant/${tenantId}/dashboard`}>Dashboard</Link>
            <Link to={`/tenant/${tenantId}/controls`}>Controls</Link>
            <Link to={`/tenant/${tenantId}/tools`}>Tools</Link>
            <Link to={`/tenant/${tenantId}/gaps`}>Gaps</Link>
          </nav>
        </header>
        <main className="mt-4">
          <Routes>
            <Route path="dashboard" element={<Dashboard tenantId={tenantId} />} />
            <Route path="controls" element={<Controls tenantId={tenantId} />} />
            <Route path="tools" element={<Tools tenantId={tenantId} />} />
            <Route path="gaps" element={<Gaps tenantId={tenantId} />} />
            <Route path="*" element={<Navigate to={`/tenant/${tenantId}/dashboard`} replace />} />
          </Routes>
        </main>
      </div>
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
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-2xl w-full p-8 bg-white rounded-lg shadow">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">SecAI Radar</h1>
        <p className="text-gray-600 mb-6">Azure security assessment platform</p>
        
        {loading && <div className="text-gray-500">Loading...</div>}
        {domains.length > 0 && (
          <div className="mb-6">
            <p className="text-sm text-gray-700 mb-2">API is working! Found {domains.length} domains:</p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              {domains.slice(0, 3).map((d: any) => (
                <li key={d.code}>{d.code}: {d.name}</li>
              ))}
            </ul>
          </div>
        )}
        
        <a 
          href={`/tenant/${defaultTenant}/dashboard`}
          className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Go to Dashboard →
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

