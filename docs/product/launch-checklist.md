# SecAI Radar Verified MCP - Launch Checklist

**Based on:** Step 6 MVP PRD  
**Target Launch:** MVP (4 weeks from start)

## Pre-Launch Checklist

### Content & Copy
- [ ] Methodology page complete + disclaimers
- [ ] All copy reviewed for accuracy and tone
- [ ] Flag definitions tooltips implemented
- [ ] Evidence confidence labels consistent
- [ ] Tier descriptions clear
- [ ] CTA copy consistent across pages

### Pages & Functionality
- [ ] Overview + Rankings + Server Detail + Daily Brief pages live
- [ ] All pages mobile responsive
- [ ] All pages accessible (WCAG 2.1 AA minimum)
- [ ] Server detail tabs functional (Overview, Evidence, Drift, Graph, Response)
- [ ] Submit Evidence page functional
- [ ] Methodology page complete

### API & Data
- [ ] Public API ETag + caching enabled
- [ ] All API endpoints return proper response envelopes
- [ ] Methodology version headers on all responses
- [ ] Error handling tested
- [ ] Rate limiting configured

### Feeds
- [ ] RSS feed validated (`/mcp/feed.xml`)
- [ ] JSON Feed validated (`/mcp/feed.json`)
- [ ] Feed items include proper metadata
- [ ] Feed links work from overview page

### Automation
- [ ] Daily pipeline run scheduled
- [ ] Publish swap tested (staging → stable)
- [ ] Validation logic working
- [ ] Staleness banner shows when data is old
- [ ] Outbox drafts generated

### Analytics
- [ ] Analytics tracking implemented
- [ ] Key events tracked (page_view, server_clicked, tab_opened, etc.)
- [ ] Funnels configured
- [ ] Dashboard access configured

### Legal & Compliance
- [ ] Disclaimers visible on all pages
- [ ] "Right-to-respond" channel established (email/form)
- [ ] Privacy policy linked (if applicable)
- [ ] Terms of service (if applicable)

### Marketing & Communication
- [ ] Press kit page on zimax.net (about, logos, contact)
- [ ] Social media accounts ready (if applicable)
- [ ] Launch announcement prepared
- [ ] Documentation links verified

### Testing
- [ ] End-to-end user flows tested
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile device testing
- [ ] Performance testing (page load < 2s)
- [ ] Accessibility testing
- [ ] Security testing (WAF, rate limiting)

### Infrastructure
- [ ] Azure resources provisioned
- [ ] Database migrations run
- [ ] Storage containers created
- [ ] Key Vault secrets configured
- [ ] Monitoring and alerts configured
- [ ] Backup strategy in place

## Launch Day Checklist

- [ ] Final data pipeline run successful
- [ ] All pages accessible
- [ ] Feeds accessible
- [ ] Analytics tracking verified
- [ ] Social media posts scheduled (if applicable)
- [ ] Team notified
- [ ] Monitoring dashboards checked

## Post-Launch Checklist (First Week)

- [ ] Monitor daily pipeline runs
- [ ] Review analytics daily
- [ ] Check for errors/alerts
- [ ] Review user feedback
- [ ] Monitor feed subscriptions
- [ ] Track evidence submissions
- [ ] Review server page views

## Success Metrics Tracking

### Week 1 Targets
- [ ] Daily run success rate ≥ 95%
- [ ] CTR overview → server detail ≥ 25%
- [ ] Evidence tab open rate ≥ 30%
- [ ] Tracked servers increase
- [ ] At least 1 evidence submission

### Ongoing Monitoring
- [ ] Weekly analytics review
- [ ] Weekly pipeline health check
- [ ] Monthly growth metrics review
- [ ] Quarterly methodology review
