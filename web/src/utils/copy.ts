/**
 * Copy System - Labels, Disclaimers, Badges
 * Based on Step 6: MVP PRD + UI Component Spec + Copy System specification
 */

// ============================================================================
// 3.1 Core Labels
// ============================================================================

export const COPY = {
  trustScore: {
    label: 'Trust Score',
    description: 'Risk posture score (0–100)',
  },
  tier: {
    A: {
      label: 'Tier A',
      description: 'Strong posture',
      color: 'green',
    },
    B: {
      label: 'Tier B',
      description: 'Good posture',
      color: 'blue',
    },
    C: {
      label: 'Tier C',
      description: 'Mixed/unknown',
      color: 'yellow',
    },
    D: {
      label: 'Tier D',
      description: 'High risk/insufficient evidence',
      color: 'red',
    },
  },
  evidenceConfidence: {
    0: {
      label: 'Evidence Confidence: 0',
      description: 'Unknown — not enough evidence',
      short: 'Unknown',
    },
    1: {
      label: 'Evidence Confidence: 1',
      description: 'Public claims — self-attested',
      short: 'Self-attested',
    },
    2: {
      label: 'Evidence Confidence: 2',
      description: 'Verifiable — artifacts reviewed',
      short: 'Verifiable',
    },
    3: {
      label: 'Evidence Confidence: 3',
      description: 'Validated — independent verification',
      short: 'Validated',
    },
  },
} as const

// ============================================================================
// 3.2 Disclaimers
// ============================================================================

export const DISCLAIMERS = {
  short: 'Verified MCP provides a risk posture assessment, not a certification. Scores reflect evidence observed at the time of assessment.',
  long: 'Scores are derived from public and/or submitted artifacts and may change as evidence changes. Providers can submit evidence and responses. Do not treat this as a guarantee of security.',
  methodology: 'This assessment uses Trust Score v1 methodology. Scores are based on evidence available at the time of assessment and may change as new evidence is submitted or discovered.',
} as const

// ============================================================================
// 3.3 Flag Definitions (Tooltips)
// ============================================================================

export const FLAG_DEFINITIONS = {
  'Fail-fast': 'Blocks "enterprise-ready" until addressed',
  'Opaque custody': 'Unclear who operates/controls data path',
  'No audit claim': 'No clear audit/logging statement found',
  'Static keys': 'Requires long-lived API keys/PAT',
  'Write tools enabled': 'Write or destructive actions available without explicit gating',
  'Retention unclear': 'Data retention/deletion unclear in public docs',
} as const

export type FlagName = keyof typeof FLAG_DEFINITIONS

/**
 * Get flag definition for tooltip
 */
export function getFlagDefinition(flagName: string): string {
  // Handle variations like "fail-fast", "FailFast", etc.
  const normalized = flagName
    .replace(/[-_]/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')

  return FLAG_DEFINITIONS[normalized as FlagName] || flagName
}

// ============================================================================
// 3.4 CTA Copy
// ============================================================================

export const CTAs = {
  lookBehindVeil: 'Look behind the veil',
  submitEvidence: 'Submit evidence to improve verification',
  governCatalog: 'Govern your MCP catalog',
  readDailyBrief: 'Read today\'s brief',
  viewEvidence: 'View evidence',
  viewDrift: 'View drift timeline',
  viewGraph: 'Explore trust graph',
  submitProviderEvidence: 'Submit provider evidence',
  requestDemo: 'Request demo',
} as const

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get tier badge configuration
 */
export function getTierBadge(tier: 'A' | 'B' | 'C' | 'D') {
  return COPY.tier[tier]
}

/**
 * Get evidence confidence badge configuration
 */
export function getEvidenceConfidenceBadge(confidence: 0 | 1 | 2 | 3) {
  return COPY.evidenceConfidence[confidence]
}

/**
 * Format evidence confidence for display
 */
export function formatEvidenceConfidence(confidence: number): string {
  const badge = getEvidenceConfidenceBadge(confidence as 0 | 1 | 2 | 3)
  return `${confidence}/3 — ${badge.short}`
}

/**
 * Get enterprise fit label
 */
export function getEnterpriseFitLabel(fit: 'Regulated' | 'Standard' | 'Experimental'): string {
  const labels = {
    Regulated: 'Enterprise-ready (Regulated)',
    Standard: 'Enterprise-ready (Standard)',
    Experimental: 'Experimental use only',
  }
  return labels[fit]
}
