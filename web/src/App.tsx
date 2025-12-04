import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Link, useParams, Navigate, useLocation } from 'react-router-dom'
import OnboardingTour from './components/OnboardingTour'
import HelpAssistant from './components/HelpAssistant'

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
const AgentCommandCenter = lazy(() => import('./routes/AgentCommandCenter'))
const AgentRegistry = lazy(() => import('./routes/AgentRegistry'))
const AgentDetail = lazy(() => import('./routes/AgentDetail'))
const Observability = lazy(() => import('./routes/Observability'))
const VoiceAgentInterface = lazy(() => import('./routes/VoiceAgentInterface'))

function Shell() {
  const { id } = useParams()
  const tenantId = id || (import.meta.env.VITE_DEFAULT_TENANT as string) || 'CONTOSO'
  const location = useLocation()

  const navLinks = [
    { to: 'assessment', label: 'Overview' },
    { to: 'dashboard', label: 'Dashboard' },
    { to: 'controls', label: 'Controls' },
    { to: 'tools', label: 'Tools' },
    { to: 'gaps', label: 'Gaps' },
    { to: 'report', label: 'Report' },
    { to: 'agents', label: 'Agents' },
    { to: 'voice', label: 'Voice' },
    { to: 'observability', label: 'Observability' },
    { to: 'https://wiki.secairadar.cloud', label: 'Wiki', external: true }
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
      {/* Glass Header */}
      <div className="sticky top-0 z-50 border-b border-white/5 bg-slate-900/70 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 font-bold text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]">
                S
                <div className="absolute inset-0 rounded-lg bg-blue-400 opacity-20 blur-sm"></div>
              </div>
              <Link to="/" className="text-xl font-bold tracking-tight text-white hover:text-blue-400 transition-colors">
                SecAI Radar
              </Link>
            </div>

            {/* Nav */}
            <nav className="hidden md:flex gap-1">
              {navLinks.map(link => {
                const isActive = !link.external && location.pathname.includes(`/${link.to}`)
                if (link.external) {
                  return (
                    <a
                      key={link.to}
                      href={link.to}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 text-slate-400 hover:text-white hover:bg-white/5"
                    >
                      {link.label}
                    </a>
                  )
                }

                return (
                  <Link
                    key={link.to}
                    to={`/tenant/${tenantId}/${link.to}`}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${isActive
                      ? 'bg-blue-500/10 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.1)] border border-blue-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                      }`}
                  >
                    {link.label}
                  </Link>
                )
              })}
            </nav>

            {/* Tenant Badge */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:block text-right">
                <div className="text-xs text-slate-500 font-medium uppercase tracking-wider">Tenant</div>
                <div className="text-sm font-bold text-slate-200">{tenantId}</div>
              </div>
              <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-medium text-slate-400">
                {tenantId.substring(0, 2)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
        <Suspense fallback={
          <div className="flex h-64 items-center justify-center text-blue-500">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-current border-t-transparent" />
          </div>
        }>
          <Routes>
            <Route path="setup" element={<AssessmentSetup tenantId={tenantId} />} />
            <Route path="assessment" element={<AssessmentOverview tenantId={tenantId} />} />
            <Route path="dashboard" element={<Dashboard tenantId={tenantId} />} />
            <Route path="controls" element={<Controls tenantId={tenantId} />} />
            <Route path="tools" element={<Tools tenantId={tenantId} />} />
            <Route path="gaps" element={<Gaps tenantId={tenantId} />} />
            <Route path="report" element={<Report tenantId={tenantId} />} />
            <Route path="agents" element={<AgentCommandCenter tenantId={tenantId} />} />
            <Route path="agents/registry" element={<AgentRegistry tenantId={tenantId} />} />
            <Route path="agent/:agentId" element={<AgentDetail tenantId={tenantId} />} />
            <Route path="agent/:agentId" element={<AgentDetail tenantId={tenantId} />} />
            <Route path="voice" element={<VoiceAgentInterface />} />
            <Route path="observability" element={<Observability tenantId={tenantId} />} />
            <Route path="domain/:domainCode" element={<Domain tenantId={tenantId} />} />
            <Route path="control/:controlId" element={<ControlDetail tenantId={tenantId} />} />
            <Route path="*" element={<Navigate to={`/tenant/${tenantId}/assessment`} replace />} />
          </Routes>
        </Suspense>
      </main>
      <HelpAssistant />
    </div>
  )
}

function App() {
  const defaultTenant = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'CONTOSO'
  return (
    <BrowserRouter>
      <OnboardingTour />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/assessments" element={<Assessments />} />
        <Route path="/tenant/:id/*" element={<Shell />} />
        <Route path="*" element={<Navigate to={`/tenant/${defaultTenant}/dashboard`} replace />} />
      </Routes>
    </BrowserRouter>
  )
}


export default App

