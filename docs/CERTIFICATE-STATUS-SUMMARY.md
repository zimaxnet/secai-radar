# Certificate Status Summary

**Last Updated:** 2026-01-27

## Container Apps Custom Domains

### secai-radar-public-api

| Domain | Status | Certificate | Binding |
|--------|--------|-------------|---------|
| `api.secairadar.cloud` | ✅ Active | Managed | SniEnabled |
| `registry.secairadar.com` | ⏳ Pending | - | - |

**Default FQDN:** `secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io`

### secai-radar-registry-api

| Domain | Status | Certificate | Binding |
|--------|--------|-------------|---------|
| `registry.secairadar.cloud` | ✅ Active | Managed | SniEnabled |

**Default FQDN:** `secai-radar-registry-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io`

## Managed Certificates

### Active Certificates

1. **api.secairadar.cloud-secai-ra-260127195414**
   - **Subject:** `api.secairadar.cloud`
   - **Status:** Succeeded
   - **Bound to:** `secai-radar-public-api`
   - **Binding:** SniEnabled

2. **registry.secairadar.cloud-secai-ra-260127195717**
   - **Subject:** `registry.secairadar.cloud`
   - **Status:** Succeeded
   - **Bound to:** `secai-radar-registry-api`
   - **Binding:** SniEnabled

## DNS Configuration

### Required DNS Records

#### For api.secairadar.cloud
```
Type: CNAME
Name: api.secairadar.cloud
Value: secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io
```

#### For registry.secairadar.cloud
```
Type: CNAME
Name: registry.secairadar.cloud
Value: secai-radar-registry-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io
```

#### For registry.secairadar.com (if adding to registry-api)
```
Type: CNAME
Name: registry.secairadar.com
Value: secai-radar-registry-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io

Type: TXT (for domain validation)
Name: asuid.registry.secairadar.com
Value: <validation-token-from-azure>
```

## Verification Commands

### Check Container App Domains

```bash
# Public API
az containerapp show \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --query "properties.configuration.ingress.customDomains" -o json

# Registry API
az containerapp show \
  --name secai-radar-registry-api \
  --resource-group secai-radar-rg \
  --query "properties.configuration.ingress.customDomains" -o json
```

### List All Managed Certificates

```bash
az containerapp env certificate list \
  --name secai-radar-dev-env \
  --resource-group secai-radar-rg \
  -o table
```

### Check Certificate Details

```bash
az resource show \
  --ids "/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/managedEnvironments/secai-radar-dev-env/managedCertificates/<certificate-name>" \
  --query "{name:name, provisioningState:properties.provisioningState, subjectName:properties.subjectName}" -o json
```

### Test Domains

```bash
# Test api.secairadar.cloud
curl -I https://api.secairadar.cloud/api/v1/public/health

# Test registry.secairadar.cloud
curl -I https://registry.secairadar.cloud/health

# Test registry.secairadar.com (if configured)
curl -I https://registry.secairadar.com/health
```

## Certificate Provisioning Timeline

- **DNS Propagation:** 5-15 minutes
- **Domain Validation:** 5-15 minutes after DNS
- **Certificate Provisioning:** 5-15 minutes after validation
- **Total:** Usually 15-45 minutes (can take up to 2 hours)

## Troubleshooting

### Certificate Stuck in "Pending"

1. **Verify DNS:**
   ```bash
   dig registry.secairadar.com CNAME
   dig asuid.registry.secairadar.com TXT
   ```

2. **Check Certificate Status:**
   ```bash
   az containerapp env certificate list \
     --name secai-radar-dev-env \
     --resource-group secai-radar-rg \
     --query "[?contains(name, 'registry')]" -o table
   ```

3. **Verify Domain Binding:**
   ```bash
   az containerapp show \
     --name secai-radar-registry-api \
     --resource-group secai-radar-rg \
     --query "properties.configuration.ingress.customDomains" -o json
   ```

### Domain Not Accessible

1. **Check DNS Resolution:**
   ```bash
   nslookup registry.secairadar.com
   ```

2. **Verify Certificate Binding:**
   - Should show `bindingType: "SniEnabled"`
   - Should have a valid `certificateId`

3. **Test HTTPS:**
   ```bash
   curl -v https://registry.secairadar.com/health
   ```

## Azure Portal Links

- **Public API Custom Domains:**
  https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/containerApps/secai-radar-public-api/customDomains

- **Registry API Custom Domains:**
  https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/containerApps/secai-radar-registry-api/customDomains

- **Managed Certificates:**
  https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/managedEnvironments/secai-radar-dev-env/managedCertificates
