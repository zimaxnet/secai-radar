# DNS Security and Functionality Guide for SecAI Radar

## Overview
This guide outlines DNS security best practices and improvements for the SecAI Radar infrastructure, focusing on the `secai-radar.zimax.net` domain and its subdomains.

## Current DNS Setup
- **Main Application**: `secai-radar.zimax.net` (Azure Static Web App)
- **Wiki**: `wiki.secai-radar.zimax.net` (GitHub Pages)
- **API**: Via Azure Functions backend

## DNS Security Improvements

### 1. DNSSEC (DNS Security Extensions)
**Purpose**: Prevents DNS spoofing and cache poisoning attacks by cryptographically signing DNS records.

**Implementation**:
- Enable DNSSEC at your DNS provider (e.g., Azure DNS, Route 53, Cloudflare)
- Generate DNSKEY and DS records
- Configure your registrar to support DNSSEC delegation

**Commands for Azure DNS**:
```bash
# Enable DNSSEC on Azure DNS zone
az network dns zone update \
  --resource-group <resource-group> \
  --name secai-radar.zimax.net \
  --set dnssecEnabled=true
```

**Verification**:
```bash
# Check DNSSEC status
dig +dnssec secai-radar.zimax.net
# Or using online tools: https://dnssec-analyzer.verisignlabs.com/
```

### 2. CAA Records (Certificate Authority Authorization)
**Purpose**: Restricts which Certificate Authorities (CAs) can issue SSL/TLS certificates for your domain.

**Recommended Records**:
```
Type: CAA
Name: @
Flags: 0
Tag: issue
Value: "letsencrypt.org"

Type: CAA
Name: @
Flags: 0
Tag: issuewild
Value: "letsencrypt.org"

Type: CAA
Name: @
Flags: 0
Tag: iodef
Value: "mailto:security@zimax.net"
```

**Implementation**:
- Add CAA records at your DNS provider
- GitHub Pages automatically handles certificates, but CAA records add an extra layer of security
- Consider adding records for Azure-managed certificates if applicable

### 3. SPF, DKIM, and DMARC (Email Security)
**Purpose**: Protect against email spoofing and phishing if email services are used.

**If using email subdomain** (`mail.secai-radar.zimax.net` or similar):

**SPF Record**:
```
Type: TXT
Name: @
Value: "v=spf1 include:_spf.github.com include:mailgun.org ~all"
```

**DKIM**: Configure in your email service provider

**DMARC Record**:
```
Type: TXT
Name: _dmarc
Value: "v=DMARC1; p=quarantine; rua=mailto:dmarc@zimax.net; ruf=mailto:dmarc@zimax.net; pct=100"
```

### 4. Security Headers via DNS
While security headers are typically set at the application level, DNS can support:

**CSP (Content Security Policy)**: Set via HTTP headers in Azure Static Web Apps and GitHub Pages
**HSTS (HTTP Strict Transport Security)**: Ensure HTTPS-only access

### 5. DNS Over HTTPS (DoH) / DNS Over TLS (DoT)
**Purpose**: Encrypt DNS queries to prevent eavesdropping and manipulation.

**Implementation Options**:
- Use a DNS provider that supports DoH/DoT (Cloudflare, Quad9, Google)
- Configure clients to use encrypted DNS
- Consider running your own DoH/DoT resolver if needed

**Recommended Public DNS Resolvers**:
- Cloudflare: `1.1.1.1` (DoH/DoT)
- Quad9: `9.9.9.9` (DoH/DoT with threat blocking)
- Google: `8.8.8.8` (DoH/DoT)

### 6. DNS Monitoring and Alerting
**Purpose**: Detect DNS hijacking, unauthorized changes, and availability issues.

**Monitoring Checks**:
- DNS resolution time
- Record changes (DNSSEC validation failures)
- Unauthorized DNS modifications
- DNS query patterns and anomalies

**Recommended Tools**:
- **Azure Monitor**: For Azure DNS zones
- **DNSSEC Analyzer**: https://dnssec-analyzer.verisignlabs.com/
- **DNSViz**: https://dnsviz.net/
- **UptimeRobot** or **Pingdom**: For DNS resolution monitoring

**Alert Conditions**:
- DNS resolution failures
- DNSSEC validation failures
- Unauthorized record changes
- Unusual query patterns
- TTL expiration issues

### 7. DNS Redundancy and High Availability
**Purpose**: Ensure DNS availability even if one provider fails.

**Implementation**:
- Use multiple DNS providers (primary + secondary)
- Configure secondary DNS servers with different providers
- Set appropriate TTL values (balance between performance and flexibility)

**Recommended Setup**:
- Primary: Azure DNS
- Secondary: Cloudflare or Route 53
- TTL: 300-3600 seconds depending on change frequency

### 8. Subdomain Security Policies
**Purpose**: Apply consistent security policies across all subdomains.

**Current Subdomains**:
- `wiki.secai-radar.zimax.net` (GitHub Pages)
- `api.secai-radar.zimax.net` (if exposed, Azure Functions)
- `app.secai-radar.zimax.net` (if needed, Azure Static Web App)

**Security Considerations**:
- Each subdomain should have its own CAA records
- Consistent DNSSEC signing across all subdomains
- Proper CORS policies in application code
- CSP headers configured per subdomain

### 9. DNS Query Logging and Analysis
**Purpose**: Monitor DNS activity for security threats and performance optimization.

**Logging**:
- Enable DNS query logging at your DNS provider
- Store logs in Azure Log Analytics or similar
- Set retention policies (minimum 30 days for security analysis)

**Analysis**:
- Identify malicious queries
- Detect DDoS attempts
- Optimize DNS performance
- Compliance and audit requirements

### 10. DNS Firewall and Threat Protection
**Purpose**: Block malicious domains and prevent DNS-based attacks.

**Features**:
- Block known malicious domains
- Malware and phishing domain filtering
- Botnet C&C domain blocking
- DNS tunneling detection

**Providers with Built-in Protection**:
- **Cloudflare Gateway**: DNS filtering service
- **Quad9**: Free public DNS with threat blocking
- **Azure DNS Private Zones**: With Azure Firewall integration

## Implementation Checklist

### Immediate Actions (High Priority)
- [ ] Enable DNSSEC for `secai-radar.zimax.net`
- [ ] Add CAA records to restrict certificate issuance
- [ ] Configure DNS monitoring and alerting
- [ ] Set up DNS query logging
- [ ] Implement DNS redundancy (secondary DNS provider)

### Short-term Actions (Medium Priority)
- [ ] Add SPF/DKIM/DMARC records if email is used
- [ ] Configure security headers in applications (CSP, HSTS)
- [ ] Set up DNS-based threat protection
- [ ] Document DNS architecture and procedures
- [ ] Implement DNS change management process

### Long-term Actions (Low Priority)
- [ ] Migrate to managed DNS service with advanced security features
- [ ] Implement custom DoH/DoT resolver if needed
- [ ] Set up comprehensive DNS analytics dashboard
- [ ] Regular DNS security audits
- [ ] DNS penetration testing

## Azure DNS Specific Recommendations

### Enable Azure DNS DNSSEC
```bash
# Check if DNSSEC is supported in your region
az network dns zone list --query "[?name=='secai-radar.zimax.net']"

# Enable DNSSEC (if supported)
az network dns zone update \
  --resource-group <resource-group> \
  --name secai-radar.zimax.net \
  --set dnssecEnabled=true
```

### Azure DNS Monitoring
```bash
# Enable diagnostic logging
az monitor diagnostic-settings create \
  --name dns-logging \
  --resource <dns-zone-resource-id> \
  --workspace <log-analytics-workspace-id> \
  --logs '[{"category":"DnsQueryLogs","enabled":true}]'
```

### Azure Private DNS (if applicable)
For internal services, use Azure Private DNS zones:
- Isolated from public DNS
- Integrated with Azure Virtual Networks
- Supports conditional forwarding

## GitHub Pages DNS Considerations

### Current Setup
- CNAME record: `wiki.secai-radar.zimax.net` → GitHub Pages
- GitHub automatically provisions SSL certificates

### Security Recommendations
1. **CAA Records**: Allow GitHub to issue certificates
   ```
   CAA 0 issue "digicert.com"
   CAA 0 issuewild "digicert.com"
   ```

2. **DNSSEC**: Enable at parent domain level (zimax.net)

3. **Security Headers**: Configure via GitHub Pages or Cloudflare (if using proxy)

## DNS Performance Optimization

### TTL Values
- **A/CNAME records**: 300-3600 seconds
  - Lower for development/testing
  - Higher for production stability
- **NS records**: 86400 seconds (24 hours)
- **MX records**: 3600 seconds (1 hour)

### DNS Caching
- Use DNS caching at application level
- Configure appropriate cache TTLs
- Monitor cache hit rates

### CDN Integration
- If using Azure CDN or Cloudflare, DNS automatically routes to nearest edge
- Consider GeoDNS for global distribution

## Testing and Validation

### DNS Security Testing
```bash
# Test DNSSEC validation
dig +dnssec +noall +answer secai-radar.zimax.net

# Test DNS resolution
nslookup wiki.secai-radar.zimax.net

# Check CAA records
dig CAA secai-radar.zimax.net

# Test DNS over HTTPS
curl -H "accept: application/dns-json" \
  "https://cloudflare-dns.com/dns-query?name=secai-radar.zimax.net&type=A"
```

### Online Testing Tools
- **DNSSEC Analyzer**: https://dnssec-analyzer.verisignlabs.com/
- **DNSViz**: https://dnsviz.net/
- **MXToolbox**: https://mxtoolbox.com/
- **SSL Labs**: https://www.ssllabs.com/ssltest/

## Compliance and Audit

### DNS Audit Requirements
- Document all DNS records and their purposes
- Maintain change log for DNS modifications
- Regular DNS security assessments
- Compliance with security frameworks (NIST, ISO 27001, SOC 2)

### Documentation
- DNS architecture diagram
- Record inventory
- Change management procedures
- Incident response procedures for DNS attacks

## Cost Considerations

### Azure DNS Pricing
- **Hosted zones**: $0.50/month per zone
- **DNS queries**: $0.40 per million queries
- **DNSSEC**: Included at no extra cost

### Cost Optimization
- Use Azure DNS for primary zone (cost-effective)
- Consider Cloudflare free tier for secondary DNS
- Monitor query volumes and optimize if needed
- Use appropriate TTL values to reduce query frequency

## Incident Response

### DNS Attack Scenarios
1. **DNS Hijacking**: Unauthorized DNS record changes
2. **DNS Spoofing**: Man-in-the-middle attacks
3. **DDoS on DNS**: Overwhelming DNS servers
4. **Cache Poisoning**: Corrupting DNS cache

### Response Procedures
1. Immediately verify DNS records
2. Check DNSSEC validation status
3. Contact DNS provider support
4. Restore correct DNS records
5. Investigate unauthorized changes
6. Document incident and lessons learned

## Resources

### Documentation
- [Azure DNS Documentation](https://docs.microsoft.com/azure/dns/)
- [DNSSEC Guide](https://www.cloudflare.com/learning/dns/dns-security/)
- [CAA Records Guide](https://letsencrypt.org/docs/caa/)

### Tools
- [DNSViz](https://dnsviz.net/) - DNSSEC visualization
- [DNSSEC Analyzer](https://dnssec-analyzer.verisignlabs.com/)
- [MXToolbox](https://mxtoolbox.com/) - DNS diagnostics

### Standards
- RFC 4033: DNS Security Introduction
- RFC 4034: Resource Records for DNSSEC
- RFC 6844: DNS Certification Authority Authorization (CAA)

## Next Steps

1. **Review current DNS configuration** at your DNS provider
2. **Implement DNSSEC** for primary domain
3. **Add CAA records** to restrict certificate issuance
4. **Set up monitoring** and alerting for DNS changes
5. **Document DNS architecture** and procedures
6. **Schedule regular DNS security audits**

---

*Last Updated: [Current Date]*
*Maintained by: SecAI Radar Security Team*

