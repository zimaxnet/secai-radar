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

function App() {
  const defaultTenant = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/tenant/:id/*" element={<Shell />} />
        <Route path="*" element={<Navigate to={`/tenant/${defaultTenant}/dashboard`} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

