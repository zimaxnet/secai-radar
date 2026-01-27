/**
 * Private API Client (Trust Registry) — T-110/T-111/T-112/T-113
 * Requires Entra ID JWT and workspace_id (query or X-Workspace-Id).
 */

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const REGISTRY_API = import.meta.env.VITE_REGISTRY_API_BASE || `${API_BASE}/v1/private/registry`

let _config: { token: string | null; workspaceId: string | null } = { token: null, workspaceId: null }

/** Set token and workspace after login (called from Registry layout). */
export function setPrivateAPIConfig(token: string | null, workspaceId: string | null) {
  _config = { token, workspaceId }
}

function urlWithWorkspace(path: string, workspaceId?: string | null): string {
  const wid = workspaceId ?? _config.workspaceId
  const base = `${REGISTRY_API}${path}`
  if (!wid) return base
  const sep = path.includes('?') ? '&' : '?'
  return `${base}${sep}workspace_id=${encodeURIComponent(wid)}`
}

async function fetchPrivate<T>(
  endpoint: string,
  options: RequestInit = {},
  workspaceId?: string | null
): Promise<T | null> {
  const token = _config.token
  if (!token) {
    console.error('No auth token — sign in in Registry')
    return null
  }
  const url = urlWithWorkspace(endpoint, workspaceId)
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
        ...(options.headers as Record<string, string>),
      },
    })
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) return null
      const err = await res.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail || res.statusText)
    }
    return await res.json()
  } catch (e) {
    console.error(`Private API ${endpoint}:`, e)
    return null
  }
}

// ============================================================================
// 6.2 Private Endpoints
// ============================================================================

/** GET /api/v1/private/registry/servers */
export async function getRegistryServers(workspaceId?: string | null): Promise<{ servers: any[]; total: number }> {
  const r = await fetchPrivate<{ servers: any[]; total: number }>('/servers', {}, workspaceId)
  return r ?? { servers: [], total: 0 }
}

/** POST /api/v1/private/registry/servers */
export async function addRegistryServer(
  body: { serverId: string; owner?: string; purpose?: string; environment?: string },
  workspaceId?: string | null
): Promise<any> {
  return await fetchPrivate<any>('/servers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }, workspaceId)
}

/**
 * GET /api/v1/private/registry/policies
 */
export async function getPolicies(workspaceId?: string | null): Promise<{ policies: any[] }> {
  const r = await fetchPrivate<{ policies: any[] }>('/policies', {}, workspaceId)
  return r ?? { policies: [] }
}

/** POST /api/v1/private/registry/policies */
export interface CreatePolicyRequest {
  scope: { type: 'server' | 'tool' | 'category'; value: string }
  decision: 'Allow' | 'Deny' | 'RequireApproval'
  conditions?: Record<string, unknown>
  expiresAt?: string
}

export async function createPolicy(body: CreatePolicyRequest, workspaceId?: string | null): Promise<any> {
  return await fetchPrivate<any>('/policies', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }, workspaceId)
}

/** POST /api/v1/private/registry/policies/{policyId}/approve */
export async function approvePolicy(policyId: string, body?: { notes?: string }, workspaceId?: string | null): Promise<any> {
  return await fetchPrivate<any>(`/policies/${policyId}/approve`, {
    method: 'POST',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  } as RequestInit, workspaceId)
}

/** POST /api/v1/private/registry/policies/{policyId}/deny */
export async function denyPolicy(policyId: string, body?: { notes?: string }, workspaceId?: string | null): Promise<any> {
  return await fetchPrivate<any>(`/policies/${policyId}/deny`, {
    method: 'POST',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  }, workspaceId)
}

/**
 * GET /api/v1/private/registry/evidence-packs
 * Query by workspace (from context or param). Optional: serverId, status (Submitted|Validated|Rejected).
 */
export async function getEvidencePacks(
  params?: { serverId?: string; status?: string },
  workspaceId?: string | null
): Promise<{ items: Array<{ packId: string; serverId: string; status: string; submittedAt?: string; validatedAt?: string; validatedBy?: string; confidence?: number }>; total: number }> {
  const q = new URLSearchParams()
  if (params?.serverId) q.set('serverId', params.serverId)
  if (params?.status) q.set('status', params.status)
  const suffix = q.toString() ? `?${q.toString()}` : ''
  const r = await fetchPrivate<{ items: unknown[]; total: number }>(`/evidence-packs${suffix}`, {}, workspaceId)
  return r ?? { items: [], total: 0 }
}

/**
 * POST /api/v1/private/registry/evidence-packs — multipart: serverId (form) + file
 */
export async function uploadEvidencePack(
  serverId: string,
  file?: File | null,
  workspaceId?: string | null
): Promise<any> {
  const form = new FormData()
  form.append('serverId', serverId)
  if (file) form.append('file', file)
  return await fetchPrivate<any>('/evidence-packs', {
    method: 'POST',
    body: form,
  }, workspaceId)
}

/** POST /api/v1/private/registry/evidence-packs/{id}/validate */
export async function validateEvidencePack(
  packId: string,
  params?: { confidence?: number },
  workspaceId?: string | null
): Promise<any> {
  const q = params?.confidence != null ? `?confidence=${params.confidence}` : ''
  return await fetchPrivate<any>(`/evidence-packs/${packId}/validate${q}`, { method: 'POST' }, workspaceId)
}

/** POST /api/v1/private/registry/exports/audit-pack */
export async function createAuditPack(
  body?: { dateFrom?: string; dateTo?: string },
  workspaceId?: string | null
): Promise<{ exportId: string; status: string }> {
  const r = await fetchPrivate<{ exportId: string; status: string }>('/exports/audit-pack', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  }, workspaceId)
  return r ?? { exportId: '', status: 'failed' }
}

/** GET /api/v1/private/registry/exports/{exportId} */
export async function getExport(exportId: string, workspaceId?: string | null): Promise<any> {
  return await fetchPrivate<any>(`/exports/${exportId}`, {}, workspaceId)
}

/** Stub: agents/runs (not implemented in registry-api yet) */
export async function getAgentRuns(_date?: string, workspaceId?: string | null): Promise<any[]> {
  await fetchPrivate<any>('/agents/runs', {}, workspaceId)
  return []
}

/** Stub: agents/run */
export async function triggerAgentRun(_config?: object, workspaceId?: string | null): Promise<any> {
  return await fetchPrivate<any>('/agents/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }, workspaceId)
}

/** Stub: agents/schedules */
export async function configureSchedule(_schedule: object, workspaceId?: string | null): Promise<any> {
  return await fetchPrivate<any>('/agents/schedules', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }, workspaceId)
}

/** Stub: outbox */
export async function getOutbox(_date?: string): Promise<any[]> {
  return []
}

/** Stub: createOutboxItem */
export async function createOutboxItem(_item: object): Promise<any> {
  return null
}

/** Stub: markOutboxItemSent */
export async function markOutboxItemSent(_outboxId: string): Promise<any> {
  return null
}
