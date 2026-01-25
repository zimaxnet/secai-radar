/**
 * Analytics Event Tracking
 * Based on Step 6: MVP PRD + UI Component Spec + Analytics Plan specification
 */

// ============================================================================
// 4.1 Event Naming Conventions
// ============================================================================

export type AnalyticsEvent =
  | 'page_view'
  | 'search_used'
  | 'filter_applied'
  | 'server_clicked'
  | 'tab_opened'
  | 'evidence_link_clicked'
  | 'drift_item_expanded'
  | 'graph_node_clicked'
  | 'feed_subscribed'
  | 'submit_evidence_started'
  | 'submit_evidence_completed'
  | 'cta_ctxeco_clicked'
  | 'ranking_item_clicked'
  | 'provider_clicked'
  | 'daily_brief_clicked'
  | 'methodology_viewed'
  | 'flag_tooltip_viewed'
  | 'compare_started'
  | 'export_requested'

export interface AnalyticsEventData {
  event: AnalyticsEvent
  properties?: Record<string, any>
  timestamp?: string
}

// ============================================================================
// Analytics Implementation
// ============================================================================

/**
 * Track analytics event
 * Supports multiple analytics providers (Google Analytics, Plausible, custom)
 */
export function trackEvent(event: AnalyticsEvent, properties?: Record<string, any>): void {
  const eventData: AnalyticsEventData = {
    event,
    properties,
    timestamp: new Date().toISOString(),
  }

  // Google Analytics 4 (if available)
  if (typeof window !== 'undefined' && (window as any).gtag) {
    ;(window as any).gtag('event', event, properties)
  }

  // Plausible (if available)
  if (typeof window !== 'undefined' && (window as any).plausible) {
    ;(window as any).plausible(event, { props: properties })
  }

  // Custom analytics endpoint (if configured)
  const analyticsEndpoint = import.meta.env.VITE_ANALYTICS_ENDPOINT
  if (typeof analyticsEndpoint === 'string') {
    fetch(analyticsEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventData),
    }).catch(err => console.warn('Analytics tracking failed:', err))
  }

  // Console log in development
  if (import.meta.env.DEV) {
    console.log('[Analytics]', event, properties)
  }
}

// ============================================================================
// Convenience Functions
// ============================================================================

/**
 * Track page view
 */
export function trackPageView(path: string, title?: string): void {
  trackEvent('page_view', {
    path,
    title: title || path,
  })
}

/**
 * Track search usage
 */
export function trackSearch(query: string, resultsCount?: number): void {
  trackEvent('search_used', {
    query,
    resultsCount,
  })
}

/**
 * Track filter application
 */
export function trackFilter(filterType: string, filterValue: string): void {
  trackEvent('filter_applied', {
    filterType,
    filterValue,
  })
}

/**
 * Track server click
 */
export function trackServerClick(serverId: string, serverSlug: string, source: string): void {
  trackEvent('server_clicked', {
    serverId,
    serverSlug,
    source, // 'overview', 'rankings', 'daily_brief', etc.
  })
}

/**
 * Track tab opened on server detail page
 */
export function trackTabOpened(serverId: string, tabName: 'overview' | 'evidence' | 'drift' | 'graph' | 'response'): void {
  trackEvent('tab_opened', {
    serverId,
    tabName,
  })
}

/**
 * Track evidence link click
 */
export function trackEvidenceLinkClick(serverId: string, evidenceId: string, evidenceUrl: string): void {
  trackEvent('evidence_link_clicked', {
    serverId,
    evidenceId,
    evidenceUrl,
  })
}

/**
 * Track drift item expansion
 */
export function trackDriftItemExpanded(serverId: string, driftId: string, eventType: string): void {
  trackEvent('drift_item_expanded', {
    serverId,
    driftId,
    eventType,
  })
}

/**
 * Track graph node click
 */
export function trackGraphNodeClick(serverId: string, nodeId: string, nodeType: string): void {
  trackEvent('graph_node_clicked', {
    serverId,
    nodeId,
    nodeType,
  })
}

/**
 * Track feed subscription
 */
export function trackFeedSubscription(feedType: 'rss' | 'json'): void {
  trackEvent('feed_subscribed', {
    feedType,
  })
}

/**
 * Track evidence submission start
 */
export function trackSubmitEvidenceStarted(serverId?: string, providerId?: string): void {
  trackEvent('submit_evidence_started', {
    serverId,
    providerId,
  })
}

/**
 * Track evidence submission completion
 */
export function trackSubmitEvidenceCompleted(serverId?: string, providerId?: string, success: boolean = true): void {
  trackEvent('submit_evidence_completed', {
    serverId,
    providerId,
    success,
  })
}

/**
 * Track CTA click to ctxeco
 */
export function trackCtaCtxecoClick(source: string): void {
  trackEvent('cta_ctxeco_clicked', {
    source, // 'overview', 'server_detail', 'footer', etc.
  })
}

// ============================================================================
// Funnel Tracking
// ============================================================================

/**
 * Track funnel progression
 */
export function trackFunnelStep(funnelName: string, step: string, properties?: Record<string, any>): void {
  trackEvent('funnel_step' as AnalyticsEvent, {
    funnelName,
    step,
    ...properties,
  })
}

/**
 * Funnel A: Discovery → Transparency
 * overview → rankings → server detail → evidence tab opened → evidence link clicked
 */
export const FunnelA = {
  overview: () => trackFunnelStep('discovery_transparency', 'overview'),
  rankings: () => trackFunnelStep('discovery_transparency', 'rankings'),
  serverDetail: (serverId: string) => trackFunnelStep('discovery_transparency', 'server_detail', { serverId }),
  evidenceTab: (serverId: string) => trackFunnelStep('discovery_transparency', 'evidence_tab', { serverId }),
  evidenceLink: (serverId: string, evidenceId: string) =>
    trackFunnelStep('discovery_transparency', 'evidence_link', { serverId, evidenceId }),
}

/**
 * Funnel B: Daily brief → deep dive
 * daily brief → server detail → drift expanded
 */
export const FunnelB = {
  dailyBrief: (date: string) => trackFunnelStep('daily_brief_deep_dive', 'daily_brief', { date }),
  serverDetail: (serverId: string) => trackFunnelStep('daily_brief_deep_dive', 'server_detail', { serverId }),
  driftExpanded: (serverId: string, driftId: string) =>
    trackFunnelStep('daily_brief_deep_dive', 'drift_expanded', { serverId, driftId }),
}

/**
 * Funnel C: Provider engagement
 * server detail → provider response tab → submit evidence started → completed
 */
export const FunnelC = {
  serverDetail: (serverId: string) => trackFunnelStep('provider_engagement', 'server_detail', { serverId }),
  providerResponseTab: (serverId: string) => trackFunnelStep('provider_engagement', 'provider_response_tab', { serverId }),
  submitStarted: (serverId: string, providerId: string) =>
    trackFunnelStep('provider_engagement', 'submit_started', { serverId, providerId }),
  submitCompleted: (serverId: string, providerId: string) =>
    trackFunnelStep('provider_engagement', 'submit_completed', { serverId, providerId }),
}

/**
 * Funnel D: Commercial conversion
 * public pages → ctxeco CTA → demo request (tracked on ctxeco side)
 */
export const FunnelD = {
  publicPage: (page: string) => trackFunnelStep('commercial_conversion', 'public_page', { page }),
  ctaClick: (source: string) => trackFunnelStep('commercial_conversion', 'cta_click', { source }),
}
