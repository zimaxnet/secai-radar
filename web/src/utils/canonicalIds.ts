/**
 * Canonical ID generation and dedupe utilities
 * Based on Step 3: Automation Blueprint specification
 */

/**
 * Simple hash function for canonical IDs
 * Note: For production, use a proper crypto library (e.g., Web Crypto API or crypto-js)
 */
async function hashString(input: string): Promise<string> {
  // Use Web Crypto API if available (browser)
  if (typeof window !== 'undefined' && window.crypto && window.crypto.subtle) {
    const encoder = new TextEncoder()
    const data = encoder.encode(input)
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('').substring(0, 16)
  }
  
  // Fallback: simple hash (for development/testing)
  let hash = 0
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16).padStart(16, '0')
}

/**
 * Generate canonical provider ID
 * Rule: providerId = hash(legalName + primaryDomain)
 */
export async function generateProviderId(legalName: string, primaryDomain: string): Promise<string> {
  const normalized = `${legalName.toLowerCase().trim()}|${primaryDomain.toLowerCase().trim()}`
  return await hashString(normalized)
}

/**
 * Generate canonical server ID
 * Rule: serverId = hash(providerId + primaryIdentifier)
 * 
 * Primary identifier precedence:
 * 1. Official repo URL (canonical)
 * 2. Official hosted endpoint domain
 * 3. Official product page URL
 * 4. If none: (normalized name + top source URL)
 */
export async function generateServerId(
  providerId: string,
  primaryIdentifier: string
): Promise<string> {
  const normalized = `${providerId}|${primaryIdentifier.toLowerCase().trim()}`
  return await hashString(normalized)
}

/**
 * Determine primary identifier from available sources
 * Returns the identifier based on precedence rules
 */
export function determinePrimaryIdentifier(options: {
  repoUrl?: string
  endpointDomain?: string
  productPageUrl?: string
  normalizedName?: string
  topSourceUrl?: string
}): string {
  // Precedence 1: Official repo URL
  if (options.repoUrl) {
    return normalizeRepoUrl(options.repoUrl)
  }

  // Precedence 2: Official hosted endpoint domain
  if (options.endpointDomain) {
    return normalizeEndpointDomain(options.endpointDomain)
  }

  // Precedence 3: Official product page URL
  if (options.productPageUrl) {
    return normalizeUrl(options.productPageUrl)
  }

  // Precedence 4: Normalized name + top source URL
  if (options.normalizedName && options.topSourceUrl) {
    return `${options.normalizedName}|${normalizeUrl(options.topSourceUrl)}`
  }

  throw new Error('Cannot determine primary identifier: insufficient data')
}

/**
 * Normalize repository URL to canonical form
 */
export function normalizeRepoUrl(url: string): string {
  try {
    const parsed = new URL(url)
    
    // Normalize GitHub URLs
    if (parsed.hostname === 'github.com' || parsed.hostname === 'www.github.com') {
      const path = parsed.pathname.replace(/\.git$/, '').replace(/^\/+|\/+$/g, '')
      return `github.com/${path.toLowerCase()}`
    }

    // Normalize GitLab URLs
    if (parsed.hostname.includes('gitlab.com')) {
      const path = parsed.pathname.replace(/\.git$/, '').replace(/^\/+|\/+$/g, '')
      return `gitlab.com/${path.toLowerCase()}`
    }

    // Generic: hostname + normalized path
    return `${parsed.hostname.toLowerCase()}${parsed.pathname.toLowerCase()}`
  } catch {
    return url.toLowerCase()
  }
}

/**
 * Normalize endpoint domain
 */
export function normalizeEndpointDomain(domain: string): string {
  return domain.toLowerCase().trim().replace(/^https?:\/\//, '').replace(/\/$/, '')
}

/**
 * Normalize URL
 */
export function normalizeUrl(url: string): string {
  try {
    const parsed = new URL(url)
    return `${parsed.hostname.toLowerCase()}${parsed.pathname.toLowerCase()}`
  } catch {
    return url.toLowerCase()
  }
}

/**
 * Normalize name for dedupe matching
 * Converts "Notion MCP", "notion-mcp-server" → same normalized form
 */
export function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with hyphens
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
    .replace(/-+/g, '-') // Collapse multiple hyphens
}

/**
 * Calculate name similarity (0-1)
 * Uses Levenshtein distance for fuzzy matching
 */
export function calculateNameSimilarity(name1: string, name2: string): number {
  const normalized1 = normalizeName(name1)
  const normalized2 = normalizeName(name2)

  if (normalized1 === normalized2) return 1.0

  const distance = levenshteinDistance(normalized1, normalized2)
  const maxLength = Math.max(normalized1.length, normalized2.length)
  
  return maxLength === 0 ? 1.0 : 1 - (distance / maxLength)
}

/**
 * Levenshtein distance calculation
 */
function levenshteinDistance(str1: string, str2: string): number {
  const matrix: number[][] = []

  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i]
  }

  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j
  }

  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1, // insertion
          matrix[i - 1][j] + 1 // deletion
        )
      }
    }
  }

  return matrix[str2.length][str1.length]
}

/**
 * Normalize endpoint URL (strip tracking params, normalize scheme/host)
 */
export function normalizeEndpointUrl(url: string): string {
  try {
    const parsed = new URL(url)
    
    // Remove common tracking parameters
    const trackingParams = ['utm_source', 'utm_medium', 'utm_campaign', 'ref', 'source', 'fbclid', 'gclid']
    trackingParams.forEach(param => parsed.searchParams.delete(param))

    // Normalize scheme (https preferred)
    const scheme = parsed.protocol === 'http:' ? 'https:' : parsed.protocol

    // Normalize hostname (remove www)
    let hostname = parsed.hostname.toLowerCase()
    if (hostname.startsWith('www.')) {
      hostname = hostname.substring(4)
    }

    // Reconstruct normalized URL
    return `${scheme}//${hostname}${parsed.pathname}${parsed.search}`
  } catch {
    return url
  }
}
