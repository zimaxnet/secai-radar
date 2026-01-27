/**
 * Public API Client
 * Based on Step 4: Data Model + API Spec specification
 * 
 * All public endpoints are read-only, no auth required.
 * Apply rate limits and caching.
 */

import type {
  PublicAPIResponse,
  SummaryResponse,
  RecentlyUpdatedItem,
  RankingItem,
  ServerDetailResponse,
  ServerEvidenceResponse,
  ServerDriftResponse,
  ServerGraphResponse,
  ProviderPortfolioResponse,
  DailyBrief,
} from '../types/dataModel'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const PUBLIC_API = `${API_BASE}/v1/public/mcp`

/**
 * Standard fetch wrapper with error handling and caching support
 */
async function fetchPublicAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<PublicAPIResponse<T> | null> {
  try {
    const response = await fetch(`${PUBLIC_API}${endpoint}`, {
      ...options,
      headers: {
        'Accept': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      if (response.status === 404) {
        return null
      }
      const error = await response.json().catch(() => ({ error: { code: 'Unknown', message: response.statusText } }))
      throw new Error(error.error?.message || `API error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`Public API error (${endpoint}):`, error)
    return null
  }
}

/**
 * 4.1 Summary (overview dashboard)
 * GET /api/v1/public/mcp/summary?window=24h
 */
export async function getSummary(window: '24h' | '7d' | '30d' = '24h'): Promise<SummaryResponse | null> {
  const response = await fetchPublicAPI<SummaryResponse>(`/summary?window=${window}`)
  return response?.data || null
}

/**
 * 4.2 Recently Updated
 * GET /api/v1/public/mcp/recently-updated?limit=50
 */
export async function getRecentlyUpdated(limit: number = 50): Promise<RecentlyUpdatedItem[]> {
  const response = await fetchPublicAPI<{ items: RecentlyUpdatedItem[] }>(`/recently-updated?limit=${limit}`)
  return response?.data?.items || []
}

/**
 * 4.3 Rankings (search + filters)
 * GET /api/v1/public/mcp/rankings
 */
export interface RankingsParams {
  q?: string // search
  category?: string
  tag?: string
  deploymentType?: 'Remote' | 'Local' | 'Hybrid' | 'Unknown'
  authModel?: 'OAuthOIDC' | 'APIKey' | 'PAT' | 'mTLS' | 'Unknown'
  toolAgency?: 'ReadOnly' | 'ReadWrite' | 'DestructivePresent' | 'Unknown'
  enterpriseFit?: 'Regulated' | 'Standard' | 'Experimental'
  tier?: 'A' | 'B' | 'C' | 'D'
  evidenceConfidence?: 0 | 1 | 2 | 3
  flag?: string // repeatable
  sort?: 'trustScore' | 'evidenceConfidence' | 'scoreDelta24h' | 'scoreDelta7d' | 'lastAssessedAt'
  window?: '24h' | '7d' | '30d'
  page?: number
  pageSize?: number
}

export async function getRankings(params: RankingsParams = {}): Promise<{
  items: RankingItem[]
  total: number
  page: number
  pageSize: number
}> {
  const queryParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(v => queryParams.append(key, String(v)))
      } else {
        queryParams.append(key, String(value))
      }
    }
  })

  const response = await fetchPublicAPI<{ items: RankingItem[] }>(`/rankings?${queryParams.toString()}`)
  
  return {
    items: response?.data?.items || [],
    total: response?.meta?.total || 0,
    page: response?.meta?.page || 1,
    pageSize: response?.meta?.pageSize || 50,
  }
}

/**
 * 4.4 Server detail (overview payload)
 * GET /api/v1/public/mcp/servers/{serverIdOrSlug}
 */
export async function getServerDetail(serverIdOrSlug: string): Promise<ServerDetailResponse | null> {
  const response = await fetchPublicAPI<ServerDetailResponse>(`/servers/${encodeURIComponent(serverIdOrSlug)}`)
  return response?.data || null
}

/**
 * 4.5 Server evidence
 * GET /api/v1/public/mcp/servers/{serverIdOrSlug}/evidence
 */
export async function getServerEvidence(serverIdOrSlug: string): Promise<ServerEvidenceResponse | null> {
  const response = await fetchPublicAPI<ServerEvidenceResponse>(`/servers/${encodeURIComponent(serverIdOrSlug)}/evidence`)
  return response?.data || null
}

/**
 * 4.6 Server drift timeline
 * GET /api/v1/public/mcp/servers/{serverIdOrSlug}/drift?window=90d
 */
export async function getServerDrift(
  serverIdOrSlug: string,
  window: '7d' | '30d' | '90d' = '90d'
): Promise<ServerDriftResponse | null> {
  const response = await fetchPublicAPI<ServerDriftResponse>(
    `/servers/${encodeURIComponent(serverIdOrSlug)}/drift?window=${window}`
  )
  return response?.data || null
}

/**
 * 4.7 Server graph (T-121). Public redacted; 200 with empty nodes/edges when missing.
 * GET /api/v1/public/mcp/servers/{serverIdOrSlug}/graph
 */
export async function getServerGraph(serverIdOrSlug: string): Promise<{
  methodologyVersion?: string
  generatedAt?: string
  data: { nodes: any[]; edges: any[] }
  meta?: { hasSnapshot: boolean }
} | null> {
  const res = await fetch(`${PUBLIC_API}/servers/${encodeURIComponent(serverIdOrSlug)}/graph`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) return null
  const body = await res.json()
  return body as any
}

/**
 * 4.8 Provider portfolio
 * GET /api/v1/public/mcp/providers/{providerIdOrSlug}
 */
export async function getProviderPortfolio(providerIdOrSlug: string): Promise<ProviderPortfolioResponse | null> {
  const response = await fetchPublicAPI<ProviderPortfolioResponse>(`/providers/${encodeURIComponent(providerIdOrSlug)}`)
  return response?.data || null
}

/**
 * GET /api/v1/public/mcp/providers/{providerIdOrSlug}/servers
 */
export async function getProviderServers(providerIdOrSlug: string): Promise<ProviderPortfolioResponse['servers']> {
  const response = await fetchPublicAPI<ProviderPortfolioResponse>(`/providers/${encodeURIComponent(providerIdOrSlug)}/servers`)
  return response?.data?.servers || []
}

/**
 * 4.9 Daily brief
 * GET /api/v1/public/mcp/daily/{YYYY-MM-DD}
 */
export async function getDailyBrief(date: string): Promise<DailyBrief | null> {
  const response = await fetchPublicAPI<DailyBrief>(`/daily/${date}`)
  return response?.data || null
}

/**
 * Get current daily brief (today's date)
 */
export async function getCurrentDailyBrief(): Promise<DailyBrief | null> {
  const today = new Date().toISOString().split('T')[0]
  return getDailyBrief(today)
}

/** T-081: Status response for stale-data banner */
export interface StatusResponse {
  status: string
  lastSuccessfulRun: string | null
  timestamp: string
}

/**
 * T-081: GET /api/v1/public/status — last successful pipeline run for stale-data banner
 */
export async function getStatus(): Promise<StatusResponse | null> {
  try {
    const url = `${API_BASE}/v1/public/status`
    const response = await fetch(url, { headers: { Accept: 'application/json' } })
    if (!response.ok) return null
    const data = await response.json()
    return {
      status: data.status ?? 'operational',
      lastSuccessfulRun: data.lastSuccessfulRun ?? null,
      timestamp: data.timestamp ?? new Date().toISOString(),
    }
  } catch {
    return null
  }
}
