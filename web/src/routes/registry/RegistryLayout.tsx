/**
 * Private Registry shell (T-110): authenticated routes, workspace context, login redirect.
 */
import { useEffect } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useIsAuthenticated, useMsal } from '@azure/msal-react'
import { loginRequest } from '../../authConfig'
import { setPrivateAPIConfig } from '../../api/private'

const DEMO_WORKSPACE_ID = 'ws-demo-00000001'

export default function RegistryLayout() {
  const { instance, accounts } = useMsal()
  const isAuthenticated = useIsAuthenticated()
  const location = useLocation()

  useEffect(() => {
    if (!isAuthenticated || accounts.length === 0) {
      setPrivateAPIConfig(null, null)
      return
    }
    const account = accounts[0]
    instance.acquireTokenSilent({ ...loginRequest, account }).then((res) => {
      setPrivateAPIConfig(res.accessToken, DEMO_WORKSPACE_ID)
    }).catch(() => {
      setPrivateAPIConfig(null, null)
    })
  }, [isAuthenticated, accounts, instance])

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch(console.error)
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-white mb-2">Trust Registry</h1>
          <p className="text-slate-400 mb-4">Sign in to manage workspace inventory, policies, and evidence.</p>
          <button
            type="button"
            onClick={handleLogin}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500"
          >
            Sign in
          </button>
        </div>
      </div>
    )
  }

  const nav = [
    { to: '/registry', label: 'Inventory' },
    { to: '/registry/policies', label: 'Policies' },
    { to: '/registry/evidence', label: 'Evidence' },
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-white/10 bg-slate-900/80">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <nav className="flex gap-4">
            {nav.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className={location.pathname === to ? 'text-blue-400' : 'text-slate-400 hover:text-white'}
              >
                {label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">Workspace</span>
            <span className="text-sm font-medium text-slate-200">{DEMO_WORKSPACE_ID}</span>
            <button
              type="button"
              onClick={() => instance.logoutPopup()}
              className="text-xs text-slate-500 hover:text-slate-300"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
