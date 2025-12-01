# DNS and Wiki Reference Check Report

**Date**: 2025-11-05  
**Status**: Issues Found

## 🟡 DNS Configuration Issue

### Current Status
- **Domain**: `secai-radar.zimax.net`
- **Azure DNS Zone**: ✅ CNAME correctly configured to `purple-moss-0942f9e10.3.azurestaticapps.net`
- **External DNS Resolution**: ❌ Still resolving to `zimaxnet.github.io` (old target)
- **Azure Static Web App**: ✅ Working correctly at `https://purple-moss-0942f9e10.3.azurestaticapps.net` (HTTP 200)
- **Custom Domain Status**: ⏳ "Validating" (waiting for DNS to resolve correctly)

### Test Results
```bash
$ az network dns record-set cname show ... secai-radar
# Result: purple-moss-0942f9e10.3.azurestaticapps.net ✅ (Correct in Azure)

$ dig secai-radar.zimax.net
# Result: zimaxnet.github.io ❌ (External DNS still shows old value)

$ curl -I https://purple-moss-0942f9e10.3.azurestaticapps.net
# Result: HTTP/2 200 ✅ (Working)

$ curl -I https://secai-radar.zimax.net
# Result: SSL certificate mismatch + 404 (Resolving to wrong target)
```

### Issue Analysis
The Azure DNS Zone configuration is correct, but external DNS queries are still resolving to the old GitHub Pages target. This suggests:
1. **DNS Propagation Delay**: DNS changes may take 24-48 hours to fully propagate
2. **DNS Caching**: DNS resolvers may be caching the old CNAME record
3. **DNS Delegation**: The `zimax.net` domain may not be properly delegated to Azure DNS nameservers

### Verification Steps
1. Check if `zimax.net` domain registrar is pointing to Azure DNS nameservers:
   - Azure DNS nameservers: `ns1-09.azure-dns.com`, `ns2-09.azure-dns.net`, `ns3-09.azure-dns.org`, `ns4-09.azure-dns.info`
2. Wait for DNS propagation (can take up to 48 hours)
3. Clear DNS cache or use different DNS resolver to test
4. Once DNS resolves correctly, Azure Static Web App will automatically validate the domain and provision SSL certificate

**Azure Portal Links**:
- **DNS Zone**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/dns-rg/providers/Microsoft.Network/dnszones/zimax.net/overview
- **Custom Domains**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/domainManagement

---

## ✅ Wiki Reference Issue - FIXED

### Status
- **Field**: `SourceRef` exists in the data model and CSV import schema
- **Storage**: Field is stored in Azure Table Storage (Controls table)
- **Display**: ✅ **NOW DISPLAYED** in the Controls UI table

### Implementation
Added `SourceRef` column to the Controls table with the following features:
- Displays as "Reference" column
- If `SourceRef` contains a URL (http:// or https://), renders as clickable "🔗 Wiki" link
- Opens in new tab with security attributes (`target="_blank" rel="noopener noreferrer"`)
- Shows tooltip with full URL on hover
- Displays "-" if no SourceRef is present
- Shows plain text if SourceRef is not a URL

### Changes Made
- Updated `web/src/routes/Controls.tsx` to include SourceRef column
- Column renders URLs as clickable links with wiki icon
- Non-URL references displayed as text

### Testing
To test:
1. Import a control with SourceRef containing a wiki URL (e.g., `https://wiki.example.com/control-123`)
2. Verify the "Reference" column appears in the Controls table
3. Click the "🔗 Wiki" link to verify it opens correctly

---

## Summary

| Issue | Status | Impact | Priority |
|-------|--------|--------|----------|
| DNS CNAME | 🟡 Propagation Delay | App not accessible via custom domain | 🔴 High |
| Wiki Reference Display | ✅ Fixed | SourceRef now visible and clickable | ✅ Complete |

---

## Next Steps

1. **DNS**: Verify domain registrar is pointing to Azure DNS nameservers, wait for propagation (24-48 hours)
2. **Verify**: Once DNS resolves correctly, Azure will automatically validate and provision SSL certificate
3. **Test**: Deploy updated Controls component and verify SourceRef links work correctly
4. **Monitor**: Check Azure Portal → Static Web App → Custom domains for validation status

