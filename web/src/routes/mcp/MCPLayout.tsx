import { Link, Outlet, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getStatus } from '../../api/public'

/** T-081: Show stale-data banner when last run older than this (ms) */
const STALE_THRESHOLD_MS = 24 * 60 * 60 * 1000

/**
 * Layout component for the MCP (Model Context Protocol) public section
 * Provides global navigation and consistent header/footer for all /mcp/* routes
 */
export default function MCPLayout() {
  const location = useLocation()
  const [lastSuccessfulRun, setLastSuccessfulRun] = useState<string | null | undefined>(undefined)

  useEffect(() => {
    getStatus().then((s) => setLastSuccessfulRun(s?.lastSuccessfulRun ?? null))
  }, [])

  const isStale =
    lastSuccessfulRun === null ||
    lastSuccessfulRun === undefined ||
    (lastSuccessfulRun !== null && Date.now() - new Date(lastSuccessfulRun).getTime() > STALE_THRESHOLD_MS)
  const showStaleBanner = lastSuccessfulRun !== undefined && isStale

  const navLinks = [
    { to: '/mcp', label: 'Verified MCP', exact: true },
    { to: '/mcp/rankings', label: 'Rankings' },
    { to: '/mcp/daily', label: 'Daily Brief' },
    { to: '/mcp/methodology', label: 'Methodology' },
    { to: '/mcp/fairness', label: 'Fairness' },
    { to: '/mcp/submit', label: 'Submit Evidence', cta: true },
  ]

  const isActive = (to: string, exact?: boolean) => {
    if (exact) {
      return location.pathname === to
    }
    return location.pathname.startsWith(to)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
      {/* Global Header */}
      <header className="sticky top-0 z-50 border-b border-white/5 bg-slate-900/70 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 font-bold text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]">
                S
                <div className="absolute inset-0 rounded-lg bg-blue-400 opacity-20 blur-sm"></div>
              </div>
              <Link to="/mcp" className="text-xl font-bold tracking-tight text-white hover:text-blue-400 transition-colors">
                SecAI Radar
              </Link>
            </div>

            {/* Main Navigation */}
            <nav className="hidden md:flex gap-1">
              {navLinks.map(link => {
                const active = isActive(link.to, link.exact)
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                      active
                        ? 'bg-blue-500/10 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.1)] border border-blue-500/20'
                        : link.cta
                        ? 'text-white bg-blue-600 hover:bg-blue-700'
                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {link.label}
                  </Link>
                )
              })}
            </nav>

            {/* Global Controls (Right Side) */}
            <div className="flex items-center gap-4">
              {/* Search */}
              <button className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="hidden lg:inline">Search</span>
              </button>

              {/* Time Window Filter */}
              <select className="hidden lg:block px-3 py-2 rounded-lg text-sm bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors">
                <option value="24h">Updated in last: 24h</option>
                <option value="7d">Updated in last: 7d</option>
                <option value="30d">Updated in last: 30d</option>
              </select>

              {/* Evidence Confidence Filter */}
              <select className="hidden xl:block px-3 py-2 rounded-lg text-sm bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors">
                <option value="all">Evidence: All</option>
                <option value="3">Evidence: High (3)</option>
                <option value="2">Evidence: Medium (2)</option>
                <option value="1">Evidence: Low (1)</option>
                <option value="0">Evidence: None (0)</option>
              </select>

              {/* About Link */}
              <Link
                to="/mcp/about"
                className="px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                About
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* T-081: Stale-data banner when last pipeline run > 24h or never run */}
      {showStaleBanner && (
        <div className="bg-amber-500/10 border-b border-amber-500/30 text-amber-200 px-4 py-2 text-center text-sm">
          Data may be outdated. Last pipeline run: {lastSuccessfulRun ? new Date(lastSuccessfulRun).toLocaleString() : 'never'}.
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-white mb-4">SecAI Radar</h3>
              <p className="text-sm text-slate-400">
                Transparent trust authority for MCP security posture. Rankings, evidence, drift, and graph exploration.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><Link to="/mcp/methodology" className="hover:text-white transition-colors">Methodology</Link></li>
                <li><Link to="/mcp/changelog" className="hover:text-white transition-colors">Changelog</Link></li>
                <li><a href="https://github.com/zimaxnet/secai-radar" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">GitHub</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white mb-4">Connect</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="https://zimax.net" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Zimax</a></li>
                <li><a href="https://ctxeco.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">CtxEco</a></li>
                <li><a href="https://github.com/derekbmoore/openContextGraph" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">OSS Engine</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/5 text-sm text-slate-500 text-center">
            <p>© {new Date().getFullYear()} SecAI Radar. Transparent trust authority for MCP security.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
