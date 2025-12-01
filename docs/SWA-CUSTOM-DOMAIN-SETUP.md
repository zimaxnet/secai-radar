# Azure Static Web App Custom Domain Setup - secairadar.cloud

## Current Status

- **Domain**: `secairadar.cloud`
- **Static Web App**: `secai-radar`
- **Resource Group**: `secai-radar-rg`
- **Default Hostname**: `purple-moss-0942f9e10.3.azurestaticapps.net`
- **Status**: Validating
- **DNS Records**: ✅ TXT and ALIAS records added
- **Default Domain**: ✅ Set to secairadar.cloud

## Required DNS Configuration

### 1. TXT Record (for Domain Validation)

Azure requires a TXT record to validate domain ownership for apex domains.

**DNS Record:**
```
Name: @ (or secairadar.cloud)
Type: TXT
Value: _7rdm8xrwpltbnbaj5691my0c39x7afd
TTL: 3600 (or default)
```

### 2. CNAME Record (for Traffic Routing)

**DNS Record:**
```
Name: @ (or secairadar.cloud)
Type: CNAME
Value: purple-moss-0942f9e10.3.azurestaticapps.net
TTL: 3600 (or default)
```

## Important Notes

### Apex Domain Limitations

`secairadar.cloud` is an **apex domain** (root domain, no subdomain). Some DNS providers have limitations:

1. **CNAME at Apex**: Not all DNS providers support CNAME records at the apex (root) domain
2. **Alternatives**:
   - Use **ALIAS** or **ANAME** record if your DNS provider supports it
   - Use a subdomain like `www.secairadar.cloud` (which supports CNAME)
   - Use Azure Front Door for apex domain support

### If Your DNS Provider Doesn't Support Apex CNAME

**Option 1: Use ALIAS/ANAME Record**
- Some providers (Route 53, Cloudflare, etc.) support ALIAS/ANAME records
- These work like CNAME but can be used at apex domains
- Point ALIAS/ANAME to: `purple-moss-0942f9e10.3.azurestaticapps.net`

**Option 2: Use Subdomain**
- Configure `www.secairadar.cloud` instead
- Subdomains fully support CNAME records
- You can redirect apex to www if needed

**Option 3: Azure Front Door**
- Use Azure Front Door in front of Static Web App
- Front Door supports apex domains natively

## Validation Process

1. **Add TXT Record**: Add the validation token as a TXT record
2. **Add CNAME/ALIAS**: Point domain to SWA hostname
3. **Wait for DNS Propagation**: Usually 1-24 hours (typically 1-2 hours)
4. **Azure Validation**: Azure automatically validates the TXT record
5. **Certificate Provisioning**: SSL certificate is automatically provisioned (24-48 hours after validation)

## Checking Status

### Quick Status Check Script

Use the provided script to check status:

```bash
./scripts/check-swa-domain-status.sh
```

This script will show:
- Current validation status
- DNS resolution status
- Timeline estimates
- Next steps

### Via Azure CLI

```bash
# Check domain status
az staticwebapp hostname show \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --hostname secairadar.cloud

# List all custom domains
az staticwebapp hostname list \
  --name secai-radar \
  --resource-group secai-radar-rg
```

### Via Azure Portal

Navigate to:
```
https://portal.azure.com/#@/resource/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/customDomains
```

## Troubleshooting

### Certificate Not Provisioning

1. **Verify DNS Records**:
   ```bash
   # Check TXT record
   dig +short secairadar.cloud TXT
   
   # Check CNAME/ALIAS
   dig +short secairadar.cloud CNAME
   dig +short secairadar.cloud A
   ```

2. **Check Validation Status**:
   - Status should be "Ready" or "Valid"
   - ValidationState should be "Valid" or "Approved"

3. **Common Issues**:
   - DNS not propagated (wait longer)
   - TXT record missing or incorrect
   - CNAME/ALIAS not pointing to correct hostname
   - DNS provider doesn't support apex CNAME (use ALIAS/ANAME)

### Domain Validation Failed

If validation fails:

1. **Remove and Re-add**:
   ```bash
   # Remove domain
   az staticwebapp hostname delete \
     --name secai-radar \
     --resource-group secai-radar-rg \
     --hostname secairadar.cloud \
     --yes
   
   # Wait 15 minutes
   # Re-add domain
   az staticwebapp hostname set \
     --name secai-radar \
     --resource-group secai-radar-rg \
     --hostname secairadar.cloud \
     --validation-method dns-txt-token
   ```

2. **Get New Validation Token**:
   ```bash
   az staticwebapp hostname show \
     --name secai-radar \
     --resource-group secai-radar-rg \
     --hostname secairadar.cloud \
     --query "validationToken" -o tsv
   ```

## Timeline

- **DNS Propagation**: 1-24 hours (typically 1-2 hours)
- **Domain Validation**: Automatic after DNS propagates
- **Certificate Provisioning**: 24-48 hours after validation completes

## Scripts

Use the provided script to configure and check status:

```bash
./scripts/configure-swa-secairadar-cloud.sh
```

## References

- [Azure Static Web Apps Custom Domains](https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain)
- [DNS Configuration for Apex Domains](https://learn.microsoft.com/en-us/azure/static-web-apps/custom-domain#apex-domains)

