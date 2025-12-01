# DNS Security Quick Reference

## Quick Commands

### Check DNS Records
```bash
# Basic DNS lookup
dig secai-radar.zimax.net
dig wiki.secai-radar.zimax.net

# Check CAA records
dig CAA secai-radar.zimax.net

# Check DNSSEC
dig +dnssec secai-radar.zimax.net

# Check MX records (if email is used)
dig MX secai-radar.zimax.net

# Check all record types
dig ANY secai-radar.zimax.net
```

### Azure DNS Commands
```bash
# List all DNS zones
az network dns zone list

# List records in a zone
az network dns record-set list \
  --resource-group rg-secai-radar \
  --zone-name secai-radar.zimax.net

# View CAA records
az network dns record-set caa show \
  --resource-group rg-secai-radar \
  --zone-name secai-radar.zimax.net \
  --name @

# Add CNAME record (for wiki subdomain)
az network dns record-set cname create \
  --resource-group rg-secai-radar \
  --zone-name secai-radar.zimax.net \
  --name wiki \
  --cname zimaxnet.github.io \
  --ttl 3600
```

### DNS Security Testing
```bash
# Test DNSSEC validation
dig +dnssec +noall +answer secai-radar.zimax.net | grep -i "ad flag"

# Test DNS over HTTPS
curl -H "accept: application/dns-json" \
  "https://cloudflare-dns.com/dns-query?name=secai-radar.zimax.net&type=A"

# Test DNS resolution time
time dig secai-radar.zimax.net

# Check for DNS leaks
# Use online tool: https://dnsleaktest.com/
```

## Common DNS Record Types

### A Record (IPv4 Address)
```
Type: A
Name: @ (or subdomain)
Value: 1.2.3.4
TTL: 3600
```

### CNAME Record (Canonical Name)
```
Type: CNAME
Name: wiki
Value: zimaxnet.github.io
TTL: 3600
```

### CAA Record (Certificate Authority Authorization)
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

### TXT Record (Text/SPF/DMARC)
```
# SPF
Type: TXT
Name: @
Value: "v=spf1 include:_spf.github.com ~all"

# DMARC
Type: TXT
Name: _dmarc
Value: "v=DMARC1; p=quarantine; rua=mailto:dmarc@zimax.net"
```

## Online DNS Testing Tools

1. **DNSSEC Analyzer**: https://dnssec-analyzer.verisignlabs.com/
   - Validates DNSSEC configuration
   - Shows DNS record chain of trust

2. **DNSViz**: https://dnsviz.net/
   - Visualizes DNS and DNSSEC status
   - Identifies configuration issues

3. **MXToolbox**: https://mxtoolbox.com/
   - DNS lookup and diagnostics
   - Blacklist checking
   - Email server testing

4. **SSL Labs**: https://www.ssllabs.com/ssltest/
   - SSL/TLS certificate testing
   - Certificate chain validation

5. **DNS Leak Test**: https://dnsleaktest.com/
   - Checks for DNS leaks
   - Identifies DNS servers in use

6. **DNS Checker**: https://dnschecker.org/
   - Global DNS propagation check
   - TTL monitoring

## Recommended TTL Values

| Record Type | Recommended TTL | Reason |
|------------|----------------|---------|
| A/CNAME (Production) | 3600 (1 hour) | Balance between performance and flexibility |
| A/CNAME (Development) | 300 (5 min) | Faster updates for testing |
| NS | 86400 (24 hours) | Rarely changes |
| MX | 3600 (1 hour) | Email reliability |
| TXT (SPF/DMARC) | 3600 (1 hour) | Email security |
| CAA | 3600 (1 hour) | Certificate security |

## DNS Security Checklist

### Initial Setup
- [ ] Enable DNSSEC
- [ ] Add CAA records
- [ ] Configure DNS monitoring
- [ ] Set up DNS redundancy
- [ ] Document DNS architecture

### Ongoing Maintenance
- [ ] Monitor DNS resolution times
- [ ] Review DNS query logs monthly
- [ ] Verify DNSSEC validation
- [ ] Check for unauthorized changes
- [ ] Update DNS records as needed
- [ ] Test DNS failover procedures

### Security Monitoring
- [ ] Set up alerts for DNS changes
- [ ] Monitor for DNS hijacking attempts
- [ ] Track DNS query anomalies
- [ ] Review DNSSEC validation failures
- [ ] Monitor DNS-based DDoS attacks

## Troubleshooting Common Issues

### DNS Not Resolving
```bash
# Check if DNS server is reachable
dig @8.8.8.8 secai-radar.zimax.net

# Check DNS propagation
# Use: https://dnschecker.org/

# Verify record exists in Azure
az network dns record-set list \
  --resource-group rg-secai-radar \
  --zone-name secai-radar.zimax.net
```

### DNSSEC Validation Failing
```bash
# Check DNSSEC status
dig +dnssec secai-radar.zimax.net

# Verify DS records at registrar
# Check DNSSEC analyzer: https://dnssec-analyzer.verisignlabs.com/

# Ensure DNSSEC is enabled in Azure
az network dns zone show \
  --resource-group rg-secai-radar \
  --zone-name secai-radar.zimax.net \
  --query "dnssecEnabled"
```

### CAA Records Not Working
```bash
# Verify CAA records exist
dig CAA secai-radar.zimax.net

# Check CAA record format
az network dns record-set caa show \
  --resource-group rg-secai-radar \
  --zone-name secai-radar.zimax.net \
  --name @

# Test certificate issuance (should respect CAA)
# Use Let's Encrypt test endpoint
```

## Emergency DNS Procedures

### If DNS is Hijacked
1. Immediately verify records at DNS provider
2. Check for unauthorized changes in audit logs
3. Restore correct DNS records
4. Change DNS provider credentials
5. Enable additional security (2FA, IP restrictions)
6. Investigate root cause

### If DNS Service is Down
1. Check DNS provider status page
2. Verify DNS zone is active in Azure
3. Check for resource group or subscription issues
4. Fail over to secondary DNS provider if configured
5. Contact DNS provider support

### If DNSSEC Fails
1. Verify DNSSEC is enabled
2. Check DS records at registrar
3. Validate DNSKEY records
4. Review DNSSEC chain of trust
5. Temporarily disable DNSSEC if causing issues (not recommended)

## Contact Information

- **DNS Provider**: Azure DNS
- **Domain Registrar**: [Your Registrar]
- **Security Email**: security@zimax.net
- **Emergency Contact**: [Your Contact]

---

*For detailed information, see [DNS-SECURITY-GUIDE.md](./DNS-SECURITY-GUIDE.md)*

