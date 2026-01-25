/**
 * Social media and community template generators
 * Based on Step 2: Content Objects + Feed Specs specification
 */

import type { DailyTrustBrief } from '../types/mcp'

const BASE_URL = 'https://secairadar.cloud'

/**
 * Generate X (Twitter) thread from daily brief
 * Returns array of posts (5-7 posts)
 */
export function generateXThread(brief: DailyTrustBrief): string[] {
  const posts: string[] = []

  // Post 1: Hook
  posts.push(
    `Verified MCP Daily Brief — ${brief.date}\n` +
    `Top movers, downgrades, and drift you should know.\n\n` +
    `${BASE_URL}${brief.permalink}`
  )

  // Post 2: Movers
  if (brief.topMovers.length > 0) {
    const moversText = brief.topMovers
      .slice(0, 3)
      .map((m, idx) => `${idx + 1}) ${m.serverName} (+${m.scoreDelta}) — ${m.reasonCodes.join(', ')}`)
      .join('\n')
    posts.push(
      `⬆️ Movers:\n${moversText}\n\n` +
      brief.topMovers.slice(0, 3).map(m => `${BASE_URL}${m.permalink}`).join('\n')
    )
  }

  // Post 3: Downgrades
  if (brief.topDowngrades.length > 0) {
    const downgradesText = brief.topDowngrades
      .slice(0, 3)
      .map((d, idx) => {
        const newFlags = d.flagChanges.added.length > 0 ? ` — new flag: ${d.flagChanges.added[0]}` : ''
        return `${idx + 1}) ${d.serverName} (${d.scoreDelta})${newFlags}`
      })
      .join('\n')
    posts.push(
      `⬇️ Downgrades:\n${downgradesText}\n\n` +
      brief.topDowngrades.slice(0, 3).map(d => `${BASE_URL}${d.permalink}`).join('\n')
    )
  }

  // Post 4: Drift
  if (brief.notableDrift.length > 0) {
    const driftText = brief.notableDrift
      .slice(0, 3)
      .map(d => `- ${d.serverName}: ${d.summary}`)
      .join('\n')
    posts.push(
      `🧭 Drift highlights:\n${driftText}\n\n` +
      brief.notableDrift.slice(0, 3).map(d => `${BASE_URL}${d.permalink}`).join('\n')
    )
  }

  // Post 5: Tip
  posts.push(
    `💡 Tip: ${brief.tipOfTheDay}`
  )

  // Post 6: Methodology
  posts.push(
    `Scored with Trust Score ${brief.methodologyVersion} + Evidence Confidence (0–3).\n` +
    `Full dashboard: ${BASE_URL}/mcp`
  )

  // Post 7: CTA
  posts.push(
    `Providers: submit evidence packs to improve verification.\n` +
    `Customers: use the Trust Registry to govern your MCP catalog.\n\n` +
    `${BASE_URL}/mcp/submit`
  )

  return posts
}

/**
 * Generate LinkedIn post from daily brief
 * Returns single post (1 post)
 */
export function generateLinkedInPost(brief: DailyTrustBrief): string {
  const moversText = brief.topMovers
    .slice(0, 2)
    .map(m => `${m.serverName} (+${m.scoreDelta})`)
    .join(', ')
  
  const downgradesText = brief.topDowngrades
    .slice(0, 2)
    .map(d => {
      const newFlag = d.flagChanges.added.length > 0 ? ` — ${d.flagChanges.added[0]}` : ''
      return `${d.serverName} (${d.scoreDelta})${newFlag}`
    })
    .join(', ')
  
  const driftText = brief.notableDrift
    .slice(0, 1)
    .map(d => `${d.serverName} — ${d.summary}`)
    .join(', ')

  return `Verified MCP Daily Brief — ${brief.date}

Today's highlights:
• Movers: ${moversText || 'None'}
• Downgrades: ${downgradesText || 'None'}
• Drift: ${driftText || 'None'}

Why it matters: Microsoft notes third‑party MCP servers aren't verified; organizations must review and track what they connect. Verified MCP provides transparency (scores, evidence confidence, drift timelines) so teams can adopt MCP safely.

Read the brief + drill into evidence: ${BASE_URL}${brief.permalink}`
}

/**
 * Generate Reddit post from daily brief
 * Returns weekly post format
 */
export function generateRedditPost(brief: DailyTrustBrief, isWeekly: boolean = false): string {
  const title = isWeekly
    ? `Verified MCP Weekly — biggest movers/downgrades + what changed (${brief.date})`
    : `Verified MCP Daily Brief — ${brief.date}`

  const top5Links = [
    ...brief.topMovers.slice(0, 2).map(m => `- [${m.serverName} (+${m.scoreDelta})](${BASE_URL}${m.permalink})`),
    ...brief.topDowngrades.slice(0, 2).map(d => `- [${d.serverName} (${d.scoreDelta})](${BASE_URL}${d.permalink})`),
    ...brief.newEntrants.slice(0, 1).map(e => `- [${e.serverName} (new)](${BASE_URL}${e.permalink})`),
  ].slice(0, 5)

  return `**${title}**

${brief.narrativeShort}

**Top Highlights:**
${brief.highlights.map(h => `- ${h}`).join('\n')}

**Top Links:**
${top5Links.join('\n')}

**Methodology:**
Scored with Trust Score ${brief.methodologyVersion} + Evidence Confidence (0–3). Full methodology: ${BASE_URL}/mcp/methodology

**Disclaimers:**
- This is a risk posture assessment, not a certification
- Scores reflect evidence confidence and trust indicators
- Providers can submit evidence to improve verification

**Provider Evidence Submissions:**
Providers can submit evidence packs: ${BASE_URL}/mcp/submit

Full dashboard: ${BASE_URL}/mcp`
}

/**
 * Generate Hacker News / Lobsters post
 * Only for major events (major downgrades, vulnerabilities, quarterly reports)
 */
export function generateHNPost(brief: DailyTrustBrief, eventType: 'major-downgrade' | 'vulnerability' | 'quarterly-report'): string {
  const title = eventType === 'quarterly-report'
    ? `Verified MCP: State of MCP Security Q1 2026 (methodology + data)`
    : `Verified MCP: daily trust scoring + drift tracking for MCP servers (methodology + data)`

  return `**${title}**

${brief.narrativeShort}

**Key Points:**
${brief.highlights.map(h => `- ${h}`).join('\n')}

**Methodology:**
Trust Score ${brief.methodologyVersion} + Evidence Confidence (0–3). Full details: ${BASE_URL}/mcp/methodology

**Data & Dashboard:**
${BASE_URL}/mcp

**Source:**
SecAI Radar - Transparent trust authority for MCP security posture`
}

/**
 * Generate headline following rules:
 * - Keep <= 60 chars
 * - Always include a number (delta or rank)
 * - Avoid implying certification
 */
export function generateHeadline(brief: DailyTrustBrief): string {
  if (brief.topMovers.length > 0) {
    const topMover = brief.topMovers[0]
    return `${topMover.serverName} leads movers with +${topMover.scoreDelta} score boost`
  }
  if (brief.topDowngrades.length > 0) {
    const topDowngrade = brief.topDowngrades[0]
    return `${topDowngrade.serverName} downgraded ${Math.abs(topDowngrade.scoreDelta)} points`
  }
  return `Verified MCP Daily Brief — ${brief.date}`
}
