/**
 * Dedupe heuristics for providers, servers, and endpoints
 * Based on Step 3: Automation Blueprint specification
 */

import { calculateNameSimilarity, normalizeRepoUrl, normalizeEndpointUrl } from './canonicalIds'

export interface DedupeCandidate {
  id: string
  name?: string
  repoUrl?: string
  endpointUrl?: string
  endpointHost?: string
  providerDomain?: string
  providerId?: string
  [key: string]: any
}

export interface DedupeResult {
  type: 'provider' | 'server' | 'endpoint'
  canonicalId: string
  mergedIds: string[]
  confidence: number // 0-1
  requiresReview: boolean
  reason: string
}

// const CONFIDENCE_THRESHOLD_HIGH = 0.9 // Unused for now
const CONFIDENCE_THRESHOLD_REVIEW = 0.7

/**
 * Dedupe servers using heuristics in order of precedence
 * 
 * Heuristics (in order):
 * 1. Exact match on repo URL
 * 2. Exact match on endpoint host
 * 3. Fuzzy match on normalized names + same provider domain
 * 4. Fuzzy match on repo name + same provider
 * 5. Human review queue when confidence < threshold
 */
export function dedupeServers(
  candidates: DedupeCandidate[],
  existingServers: DedupeCandidate[]
): DedupeResult[] {
  const results: DedupeResult[] = []
  const processed = new Set<string>()

  for (const candidate of candidates) {
    if (processed.has(candidate.id)) continue

    const matches: string[] = [candidate.id]
    let confidence = 0
    let reason = ''
    let requiresReview = false

    // Heuristic 1: Exact match on repo URL
    if (candidate.repoUrl) {
      const normalizedRepo = normalizeRepoUrl(candidate.repoUrl)
      const match = existingServers.find(s => 
        s.repoUrl && normalizeRepoUrl(s.repoUrl) === normalizedRepo
      )
      if (match && !processed.has(match.id)) {
        matches.push(match.id)
        confidence = 1.0
        reason = 'Exact match on repo URL'
        processed.add(match.id)
      }
    }

    // Heuristic 2: Exact match on endpoint host
    if (confidence < 1.0 && candidate.endpointHost) {
      const normalizedHost = candidate.endpointHost.toLowerCase().trim()
      const match = existingServers.find(s => 
        s.endpointHost && s.endpointHost.toLowerCase().trim() === normalizedHost
      )
      if (match && !processed.has(match.id)) {
        matches.push(match.id)
        confidence = 0.95
        reason = 'Exact match on endpoint host'
        processed.add(match.id)
      }
    }

    // Heuristic 3: Fuzzy match on normalized names + same provider domain
    if (confidence < 0.9 && candidate.name && candidate.providerDomain) {
      // const normalizedCandidateName = normalizeName(candidate.name) // Unused for now
      const match = existingServers.find(s => {
        if (!s.name || !s.providerDomain) return false
        if (s.providerDomain !== candidate.providerDomain) return false
        
        const similarity = calculateNameSimilarity(
          candidate.name || '', 
          s.name || ''
        )
        return similarity >= 0.85 // High similarity threshold
      })
      
      if (match && !processed.has(match.id)) {
        const similarity = calculateNameSimilarity(candidate.name, match.name!)
        matches.push(match.id)
        confidence = similarity * 0.9 // Slightly lower than exact match
        reason = `Fuzzy name match (${Math.round(similarity * 100)}%) + same provider domain`
        processed.add(match.id)
      }
    }

    // Heuristic 4: Fuzzy match on repo name + same provider
    if (confidence < 0.8 && candidate.repoUrl && candidate.providerId) {
      const repoName = extractRepoName(candidate.repoUrl)
      const match = existingServers.find(s => {
        if (!s.repoUrl || !s.providerId) return false
        if (s.providerId !== candidate.providerId) return false
        
        const matchRepoName = extractRepoName(s.repoUrl)
        const similarity = calculateNameSimilarity(repoName, matchRepoName)
        return similarity >= 0.8
      })
      
      if (match && !processed.has(match.id)) {
        const matchRepoName = extractRepoName(match.repoUrl!)
        const similarity = calculateNameSimilarity(repoName, matchRepoName)
        matches.push(match.id)
        confidence = similarity * 0.85
        reason = `Fuzzy repo name match (${Math.round(similarity * 100)}%) + same provider`
        processed.add(match.id)
      }
    }

    // Determine if review is required
    if (confidence > 0 && confidence < CONFIDENCE_THRESHOLD_REVIEW) {
      requiresReview = true
    }

    if (matches.length > 1) {
      results.push({
        type: 'server',
        canonicalId: matches[0], // Use first match as canonical
        mergedIds: matches.slice(1),
        confidence,
        requiresReview,
        reason,
      })
    }

    processed.add(candidate.id)
  }

  return results
}

/**
 * Dedupe providers using similar heuristics
 */
export function dedupeProviders(
  candidates: DedupeCandidate[],
  existingProviders: DedupeCandidate[]
): DedupeResult[] {
  const results: DedupeResult[] = []
  const processed = new Set<string>()

  for (const candidate of candidates) {
    if (processed.has(candidate.id)) continue

    const matches: string[] = [candidate.id]
    let confidence = 0
    let reason = ''
    let requiresReview = false

    // Exact match on domain
    if (candidate.providerDomain) {
      const normalizedDomain = candidate.providerDomain.toLowerCase().trim()
      const match = existingProviders.find(p => 
        p.providerDomain && p.providerDomain.toLowerCase().trim() === normalizedDomain
      )
      if (match && !processed.has(match.id)) {
        matches.push(match.id)
        confidence = 1.0
        reason = 'Exact match on provider domain'
        processed.add(match.id)
      }
    }

    // Fuzzy match on name
    if (confidence < 1.0 && candidate.name) {
      const match = existingProviders.find(p => {
        if (!p.name) return false
        const similarity = calculateNameSimilarity(candidate.name!, p.name)
        return similarity >= 0.9
      })
      
      if (match && !processed.has(match.id)) {
        const similarity = calculateNameSimilarity(candidate.name, match.name!)
        matches.push(match.id)
        confidence = similarity * 0.95
        reason = `Fuzzy name match (${Math.round(similarity * 100)}%)`
        processed.add(match.id)
      }
    }

    if (confidence > 0 && confidence < CONFIDENCE_THRESHOLD_REVIEW) {
      requiresReview = true
    }

    if (matches.length > 1) {
      results.push({
        type: 'provider',
        canonicalId: matches[0],
        mergedIds: matches.slice(1),
        confidence,
        requiresReview,
        reason,
      })
    }

    processed.add(candidate.id)
  }

  return results
}

/**
 * Dedupe endpoints
 */
export function dedupeEndpoints(
  candidates: DedupeCandidate[],
  existingEndpoints: DedupeCandidate[]
): DedupeResult[] {
  const results: DedupeResult[] = []
  const processed = new Set<string>()

  for (const candidate of candidates) {
    if (processed.has(candidate.id)) continue

    const matches: string[] = [candidate.id]
    let confidence = 0
    let reason = ''

    // Exact match on normalized endpoint URL
    if (candidate.endpointUrl) {
      const normalized = normalizeEndpointUrl(candidate.endpointUrl)
      const match = existingEndpoints.find(e => 
        e.endpointUrl && normalizeEndpointUrl(e.endpointUrl) === normalized
      )
      if (match && !processed.has(match.id)) {
        matches.push(match.id)
        confidence = 1.0
        reason = 'Exact match on normalized endpoint URL'
        processed.add(match.id)
      }
    }

    // Exact match on endpoint host
    if (confidence < 1.0 && candidate.endpointHost) {
      const normalizedHost = candidate.endpointHost.toLowerCase().trim()
      const match = existingEndpoints.find(e => 
        e.endpointHost && e.endpointHost.toLowerCase().trim() === normalizedHost
      )
      if (match && !processed.has(match.id)) {
        matches.push(match.id)
        confidence = 0.95
        reason = 'Exact match on endpoint host'
        processed.add(match.id)
      }
    }

    if (matches.length > 1) {
      results.push({
        type: 'endpoint',
        canonicalId: matches[0],
        mergedIds: matches.slice(1),
        confidence,
        requiresReview: false, // Endpoints are usually straightforward
        reason,
      })
    }

    processed.add(candidate.id)
  }

  return results
}

/**
 * Extract repository name from URL
 */
function extractRepoName(repoUrl: string): string {
  try {
    const parsed = new URL(repoUrl)
    const pathParts = parsed.pathname.split('/').filter(p => p)
    if (pathParts.length >= 2) {
      return pathParts[pathParts.length - 1].replace(/\.git$/, '')
    }
    return parsed.pathname
  } catch {
    return repoUrl
  }
}
