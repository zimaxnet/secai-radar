import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Verified MCP public site: no auth gate. Renders immediately so SWA never shows a white page.
// Legacy auth (MSAL) was removed from bootstrap; restore MsalProvider here if adding private routes.
const root = document.getElementById('root')
if (root) {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}
