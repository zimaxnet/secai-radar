/**
 * Private API Client (Trust Registry)
 * Based on Step 4: Data Model + API Spec specification
 * 
 * Private endpoints require authentication (Entra ID / JWT) and RBAC.
 */

import type { PublicAPIResponse } from '../types/dataModel'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const PRIVATE_API = `${API_BASE}/v1/private/registry`

/**
 * Get authentication token (placeholder - implement based on your auth system)
 */
async function getAuthToken(): Promise<string | null> {
  // TODO: Implement actual auth token retrieval
  // This should use your Entra ID / OIDC implementation
  return null
}

/**
 * Standard fetch wrapper for private API with auth
 */
async function fetchPrivateAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<PublicAPIResponse<T> | null> {
  const token = await getAuthToken()
  
  if (!token) {
    console.error('No authentication token available')
    return null
  }

  try {
    const response = await fetch(`${PRIVATE_API}${endpoint}`, {
      ...options,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        // Handle auth errors
        console.error('Authentication/authorization error')
        return null
      }
      const error = await response.json().catch(() => ({ error: { code: 'Unknown', message: response.statusText } }))
      throw new Error(error.error?.message || `API error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`Private API error (${endpoint}):`, error)
    return null
  }
}

// ============================================================================
// 6.2 Private Endpoints
// ============================================================================

/**
 * Registry inventory
 * GET /api/v1/private/registry/servers
 */
export async function getRegistryServers(workspaceId?: string): Promise<any[]> {
  const params = workspaceId ? `?workspaceId=${workspaceId}` : ''
  const response = await fetchPrivateAPI<{ items: any[] }>(`/servers${params}`)
  return response?.data?.items || []
}

/**
 * POST /api/v1/private/registry/servers
 * Add server to org inventory
 */
export async function addRegistryServer(serverId: string, metadata: {
  owner?: string
  purpose?: string
  environment?: string
}): Promise<any> {
  const response = await fetchPrivateAPI<any>('/servers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      serverId,
      ...metadata,
    }),
  })
  return response?.data || null
}

/**
 * GET /api/v1/private/registry/servers/{serverId}
 */
export async function getRegistryServer(serverId: string): Promise<any> {
  const response = await fetchPrivateAPI<any>(`/servers/${serverId}`)
  return response?.data || null
}

/**
 * PATCH /api/v1/private/registry/servers/{serverId}
 * Update org metadata
 */
export async function updateRegistryServer(
  serverId: string,
  metadata: {
    owner?: string
    purpose?: string
    environment?: string
  }
): Promise<any> {
  const response = await fetchPrivateAPI<any>(`/servers/${serverId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(metadata),
  })
  return response?.data || null
}

/**
 * Policies + approvals
 * GET /api/v1/private/registry/policies
 */
export async function getPolicies(workspaceId?: string): Promise<any[]> {
  const params = workspaceId ? `?workspaceId=${workspaceId}` : ''
  const response = await fetchPrivateAPI<{ items: any[] }>(`/policies${params}`)
  return response?.data?.items || []
}

/**
 * POST /api/v1/private/registry/policies
 * Create allow/deny/prompt-for-approval rules
 */
export interface CreatePolicyRequest {
  workspaceId: string
  scope: {
    type: 'server' | 'tool' | 'category'
    value: string
  }
  decision: 'Allow' | 'Deny' | 'RequireApproval'
  conditions?: {
    env?: string
    dataClass?: string
    toolAgency?: string
    evidenceConfidence?: number
  }
  expiresAt?: string
}

export async function createPolicy(policy: CreatePolicyRequest): Promise<any> {
  const response = await fetchPrivateAPI<any>('/policies', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(policy),
  })
  return response?.data || null
}

/**
 * POST /api/v1/private/registry/policies/{policyId}/approve
 */
export async function approvePolicy(policyId: string, approval: {
  approvedBy: string
  notes?: string
}): Promise<any> {
  const response = await fetchPrivateAPI<any>(`/policies/${policyId}/approve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(approval),
  })
  return response?.data || null
}

/**
 * POST /api/v1/private/registry/policies/{policyId}/deny
 */
export async function denyPolicy(policyId: string, denial: {
  deniedBy: string
  reason: string
}): Promise<any> {
  const response = await fetchPrivateAPI<any>(`/policies/${policyId}/deny`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(denial),
  })
  return response?.data || null
}

/**
 * Evidence packs (private uploads)
 * POST /api/v1/private/registry/evidence-packs
 */
export async function uploadEvidencePack(file: File, metadata: {
  serverId: string
  type: string
  description?: string
}): Promise<any> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('metadata', JSON.stringify(metadata))

  const response = await fetchPrivateAPI<any>('/evidence-packs', {
    method: 'POST',
    body: formData,
  })
  return response?.data || null
}

/**
 * GET /api/v1/private/registry/evidence-packs
 */
export async function getEvidencePacks(workspaceId?: string): Promise<any[]> {
  const params = workspaceId ? `?workspaceId=${workspaceId}` : ''
  const response = await fetchPrivateAPI<{ items: any[] }>(`/evidence-packs${params}`)
  return response?.data?.items || []
}

/**
 * POST /api/v1/private/registry/evidence-packs/{id}/validate
 */
export async function validateEvidencePack(packId: string, validation: {
  validatedBy: string
  confidence: 1 | 2 | 3
  notes?: string
}): Promise<any> {
  const response = await fetchPrivateAPI<any>(`/evidence-packs/${packId}/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(validation),
  })
  return response?.data || null
}

/**
 * Exports (audit packs)
 * POST /api/v1/private/registry/exports/audit-pack
 */
export interface CreateAuditPackRequest {
  serverIds: string[]
  dateRange: {
    from: string
    to: string
  }
  includeLogs: boolean
  redactionLevel: 'none' | 'partial' | 'full'
}

export async function createAuditPack(request: CreateAuditPackRequest): Promise<{
  exportId: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
}> {
  const response = await fetchPrivateAPI<{
    exportId: string
    status: string
  }>('/exports/audit-pack', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  const result = response?.data || { exportId: '', status: 'failed' }
  return {
    exportId: result.exportId,
    status: (result.status === 'queued' || result.status === 'processing' || result.status === 'completed' || result.status === 'failed') 
      ? result.status 
      : 'failed' as 'queued' | 'processing' | 'completed' | 'failed',
  }
}

/**
 * GET /api/v1/private/registry/exports/{exportId}
 */
export async function getExport(exportId: string): Promise<{
  exportId: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  downloadUrl?: string
  error?: string
}> {
  const response = await fetchPrivateAPI<any>(`/exports/${exportId}`)
  return response?.data || { exportId, status: 'failed' }
}

/**
 * Automation runs
 * GET /api/v1/private/registry/agents/runs?date=...
 */
export async function getAgentRuns(date?: string): Promise<any[]> {
  const params = date ? `?date=${date}` : ''
  const response = await fetchPrivateAPI<{ items: any[] }>(`/agents/runs${params}`)
  return response?.data?.items || []
}

/**
 * POST /api/v1/private/registry/agents/run
 * Trigger run
 */
export async function triggerAgentRun(config?: {
  stages?: string[]
  force?: boolean
}): Promise<any> {
  const response = await fetchPrivateAPI<any>('/agents/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(config || {}),
  })
  return response?.data || null
}

/**
 * POST /api/v1/private/registry/agents/schedules
 * Configure daily schedules
 */
export async function configureSchedule(schedule: {
  enabled: boolean
  cronExpression?: string
  stages?: string[]
}): Promise<any> {
  const response = await fetchPrivateAPI<any>('/agents/schedules', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(schedule),
  })
  return response?.data || null
}

/**
 * Outbox (distribution drafts)
 * GET /api/v1/private/outbox?date=...
 */
export async function getOutbox(date?: string): Promise<any[]> {
  const params = date ? `?date=${date}` : ''
  const response = await fetchPrivateAPI<{ items: any[] }>(`/outbox${params}`)
  return response?.data?.items || []
}

/**
 * POST /api/v1/private/outbox
 * Create scheduled post payload
 */
export async function createOutboxItem(item: {
  channel: 'x' | 'linkedin' | 'reddit' | 'hn' | 'mastodon' | 'bluesky'
  content: string
  media?: string[]
  links: string[]
  scheduledFor?: string
}): Promise<any> {
  const response = await fetchPrivateAPI<any>('/outbox', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(item),
  })
  return response?.data || null
}

/**
 * POST /api/v1/private/outbox/{id}/mark-sent
 */
export async function markOutboxItemSent(outboxId: string): Promise<any> {
  const response = await fetchPrivateAPI<any>(`/outbox/${outboxId}/mark-sent`, {
    method: 'POST',
  })
  return response?.data || null
}
