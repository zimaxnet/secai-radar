/**
 * Feed generation utilities for RSS/Atom and JSON Feed
 * Based on Step 2: Content Objects + Feed Specs specification
 */

import type { DailyTrustBrief, RSSFeedItem, JSONFeedItem, JSONFeed } from '../types/mcp'

const FEED_BASE_URL = 'https://secairadar.cloud'
const FEED_TITLE = 'SecAI Radar - Verified MCP Daily Brief'
const FEED_DESCRIPTION = 'Transparent trust authority for MCP security posture. Daily briefs, rankings, evidence, and drift tracking.'

/**
 * Generate RSS/Atom feed XML from daily briefs
 */
export function generateRSSFeed(briefs: DailyTrustBrief[]): string {
  const items = briefs.map(brief => generateRSSItem(brief))
  
  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>${escapeXml(FEED_TITLE)}</title>
    <link>${FEED_BASE_URL}/mcp</link>
    <description>${escapeXml(FEED_DESCRIPTION)}</description>
    <language>en-US</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${FEED_BASE_URL}/mcp/feed.xml" rel="self" type="application/rss+xml"/>
    ${items.map(item => `
    <item>
      <title>${escapeXml(item.title)}</title>
      <link>${FEED_BASE_URL}${item.link}</link>
      <guid isPermaLink="true">${FEED_BASE_URL}${item.link}</guid>
      <pubDate>${new Date(item.pubDate).toUTCString()}</pubDate>
      <description>${escapeXml(item.description)}</description>
      ${item.contentEncoded ? `<content:encoded><![CDATA[${item.contentEncoded}]]></content:encoded>` : ''}
      ${item.categories.map(cat => `<category>${escapeXml(cat)}</category>`).join('\n      ')}
      ${item.mediaImageUrl ? `<enclosure url="${item.mediaImageUrl}" type="image/png"/>` : ''}
    </item>`).join('')}
  </channel>
</rss>`
  
  return rss
}

/**
 * Generate RSS feed item from daily brief
 */
function generateRSSItem(brief: DailyTrustBrief): RSSFeedItem {
  const categories = ['VerifiedMCP', 'DailyBrief']
  if (brief.topMovers.length > 0) categories.push('Movers')
  if (brief.topDowngrades.length > 0) categories.push('Downgrades')
  if (brief.newEntrants.length > 0) categories.push('NewEntrants')

  return {
    title: brief.headline,
    link: brief.permalink,
    pubDate: brief.generatedAt,
    guid: `${FEED_BASE_URL}${brief.permalink}`,
    description: brief.narrativeShort,
    categories,
    contentEncoded: generateHTMLContent(brief),
    // mediaImageUrl: `https://sage-meridian.example.com/cards/${brief.date}.png`, // TODO: Add when Sage Meridian is integrated
  }
}

/**
 * Generate JSON Feed from daily briefs
 */
export function generateJSONFeed(briefs: DailyTrustBrief[]): JSONFeed {
  return {
    version: 'https://jsonfeed.org/version/1.1',
    title: FEED_TITLE,
    home_page_url: `${FEED_BASE_URL}/mcp`,
    feed_url: `${FEED_BASE_URL}/mcp/feed.json`,
    items: briefs.map(brief => generateJSONFeedItem(brief)),
  } as JSONFeed
}

/**
 * Generate JSON Feed item from daily brief
 */
function generateJSONFeedItem(brief: DailyTrustBrief): JSONFeedItem {
  const tags = ['VerifiedMCP', 'DailyBrief']
  if (brief.topMovers.length > 0) tags.push('Movers')
  if (brief.topDowngrades.length > 0) tags.push('Downgrades')
  if (brief.newEntrants.length > 0) tags.push('NewEntrants')

  return {
    id: `${FEED_BASE_URL}${brief.permalink}`,
    url: `${FEED_BASE_URL}${brief.permalink}`,
    title: brief.headline,
    content_text: brief.narrativeShort,
    content_html: generateHTMLContent(brief),
    date_published: brief.generatedAt,
    tags,
    // attachments: [
    //   {
    //     url: `https://sage-meridian.example.com/cards/${brief.date}.png`,
    //     mime_type: 'image/png',
    //     title: `Daily Brief Card - ${brief.date}`,
    //   },
    // ], // TODO: Add when Sage Meridian is integrated
    author: 'SecAI Radar Verified MCP',
  }
}

/**
 * Generate HTML content for feed items
 */
function generateHTMLContent(brief: DailyTrustBrief): string {
  const highlights = brief.highlights.map(h => `<li>${escapeHtml(h)}</li>`).join('')
  const movers = brief.topMovers.map(m => 
    `<li><a href="${FEED_BASE_URL}${m.permalink}">${escapeHtml(m.serverName)}</a> (+${m.scoreDelta})</li>`
  ).join('')
  const downgrades = brief.topDowngrades.map(d => 
    `<li><a href="${FEED_BASE_URL}${d.permalink}">${escapeHtml(d.serverName)}</a> (${d.scoreDelta})</li>`
  ).join('')

  return `
    <h2>${escapeHtml(brief.headline)}</h2>
    <p><strong>Date:</strong> ${brief.date}</p>
    <p>${escapeHtml(brief.narrativeLong)}</p>
    <h3>Highlights</h3>
    <ul>${highlights}</ul>
    ${movers ? `<h3>Top Movers</h3><ul>${movers}</ul>` : ''}
    ${downgrades ? `<h3>Top Downgrades</h3><ul>${downgrades}</ul>` : ''}
    <h3>Tip of the Day</h3>
    <p>${escapeHtml(brief.tipOfTheDay)}</p>
    <p><a href="${FEED_BASE_URL}${brief.permalink}">Read full brief →</a></p>
  `.trim()
}

/**
 * Escape XML special characters
 */
function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

/**
 * Escape HTML special characters
 */
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}
