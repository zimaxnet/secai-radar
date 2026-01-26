import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { PageTracker } from './components/PageTracker'

// MCP (Model Context Protocol) public routes - Verified MCP Trust Hub
const MCPLayout = lazy(() => import('./routes/mcp/MCPLayout'))
const MCPOverview = lazy(() => import('./routes/mcp/Overview'))
const MCPRankings = lazy(() => import('./routes/mcp/Rankings'))
const MCPServerDetail = lazy(() => import('./routes/mcp/ServerDetail'))
const MCPProviderPortfolio = lazy(() => import('./routes/mcp/ProviderPortfolio'))
const MCPDailyBrief = lazy(() => import('./routes/mcp/DailyBrief'))
const MCPMethodology = lazy(() => import('./routes/mcp/Methodology'))
const MCPChangelog = lazy(() => import('./routes/mcp/Changelog'))
const MCPSubmit = lazy(() => import('./routes/mcp/Submit'))
const MCPAbout = lazy(() => import('./routes/mcp/About'))

// Loading spinner component
function LoadingSpinner() {
  return (
    <div className="flex h-64 items-center justify-center text-blue-500">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-current border-t-transparent" />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <PageTracker />
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Root redirects to Verified MCP dashboard */}
          <Route path="/" element={<Navigate to="/mcp" replace />} />
          
          {/* Verified MCP Public Routes */}
          <Route path="/mcp" element={<MCPLayout />}>
            <Route index element={<MCPOverview />} />
            <Route path="rankings" element={<MCPRankings />} />
            <Route path="servers/:serverSlug" element={<MCPServerDetail />} />
            <Route path="providers/:providerSlug" element={<MCPProviderPortfolio />} />
            <Route path="daily/:date" element={<MCPDailyBrief />} />
            <Route path="daily" element={<Navigate to={`/mcp/daily/${new Date().toISOString().split('T')[0]}`} replace />} />
            <Route path="methodology" element={<MCPMethodology />} />
            <Route path="changelog" element={<MCPChangelog />} />
            <Route path="submit" element={<MCPSubmit />} />
            <Route path="about" element={<MCPAbout />} />
          </Route>
          
          {/* Catch-all: redirect to MCP dashboard */}
          <Route path="*" element={<Navigate to="/mcp" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
