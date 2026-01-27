# Public rate limiting and WAF (T-130)

Baseline for SecAI Radar public API and feeds.

## Rate limits (documented thresholds)

Apply at edge (e.g. Azure Front Door, Cloudflare) or in the public-api:

| Endpoint / group | Limit | Window |
|------------------|--------|--------|
| General read (summary, rankings, server detail) | 100 req | per IP per minute |
| Search / rankings (heavy) | 50 req | per IP per minute |
| Feeds (feed.xml, feed.json) | 10 req | per IP per minute |
| Health / status | 20 req | per IP per minute |

Return **429 Too Many Requests** with `Retry-After` when exceeded.

## Abuse rules (basic)

- Block requests with no or fake `User-Agent` (optional strict policy).
- Block obvious bot patterns (e.g. same path >50/min from one IP).
- WAF: enable SQLi and XSS rules at the edge where applicable (e.g. Azure Front Door WAF, AWS WAF).

## Implementation notes

- **Public API:** In-API middleware in [apps/public-api/src/middleware/rate_limit.py](../../apps/public-api/src/middleware/rate_limit.py) enforces the above limits per client IP; path groups are feed / health / heavy (rankings) / general. Returns 429 with `Retry-After` when exceeded. Alternatively use Azure Front Door rate-limit and WAF policies at the edge.
- **Feeds:** Same limits as above (feed group: 10/min); consider caching at CDN so origin rate limits matter less.
