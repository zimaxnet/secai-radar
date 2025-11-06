import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Link, useParams, Navigate } from 'react-router-dom'

// Lazy load route components for code splitting
const Landing = lazy(() => import('./routes/Landing'))
const Assessments = lazy(() => import('./routes/Assessments'))
const AssessmentSetup = lazy(() => import('./routes/AssessmentSetup'))
const AssessmentOverview = lazy(() => import('./routes/AssessmentOverview'))
const Dashboard = lazy(() => import('./routes/Dashboard'))
const Controls = lazy(() => import('./routes/Controls'))
const Tools = lazy(() => import('./routes/Tools'))
const Gaps = lazy(() => import('./routes/Gaps'))
const Domain = lazy(() => import('./routes/Domain'))
const ControlDetail = lazy(() => import('./routes/ControlDetail'))
const Report = lazy(() => import('./routes/Report'))

function Shell() {
  const { id } = useParams()
  const tenantId = id || (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-4">
        <header className="flex items-center justify-between mb-4">
          <Link to="/" className="text-2xl font-bold text-gray-900 hover:text-blue-600">
            SecAI Radar
          </Link>
          <nav className="flex gap-4 text-blue-600">
            <Link to={`/tenant/${tenantId}/assessment`} className="hover:underline">Assessment</Link>
            <Link to={`/tenant/${tenantId}/controls`} className="hover:underline">Controls</Link>
            <Link to={`/tenant/${tenantId}/tools`} className="hover:underline">Tools</Link>
            <Link to={`/tenant/${tenantId}/gaps`} className="hover:underline">Gaps</Link>
            <Link to={`/tenant/${tenantId}/report`} className="hover:underline">Report</Link>
          </nav>
        </header>
        <main className="mt-4">
          <Suspense fallback={<div className="p-4 text-gray-600">Loading...</div>}>
            <Routes>
              <Route path="setup" element={<AssessmentSetup tenantId={tenantId} />} />
              <Route path="assessment" element={<AssessmentOverview tenantId={tenantId} />} />
              <Route path="dashboard" element={<Dashboard tenantId={tenantId} />} />
              <Route path="controls" element={<Controls tenantId={tenantId} />} />
              <Route path="tools" element={<Tools tenantId={tenantId} />} />
              <Route path="gaps" element={<Gaps tenantId={tenantId} />} />
              <Route path="report" element={<Report tenantId={tenantId} />} />
              <Route path="domain/:domainCode" element={<Domain tenantId={tenantId} />} />
              <Route path="control/:controlId" element={<ControlDetail tenantId={tenantId} />} />
              <Route path="*" element={<Navigate to={`/tenant/${tenantId}/assessment`} replace />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/assessments" element={<Assessments />} />
        <Route path="/tenant/:id/*" element={<Shell />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

