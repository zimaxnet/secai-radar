/**
 * Route change tracking for analytics
 */

import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { trackPageView } from './analytics'

/**
 * Hook to track page views on route changes
 */
export function usePageTracking() {
  const location = useLocation()

  useEffect(() => {
    trackPageView(location.pathname)
  }, [location])
}
