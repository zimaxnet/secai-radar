# Container App Custom Domains Configuration

## Current Status

### ✅ api.secairadar.cloud
- **Status**: Configured with managed certificate
- **Binding**: SniEnabled
- **Certificate ID**: `/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/managedEnvironments/secai-radar-dev-env/managedCertificates/api.secairadar.cloud-secai-ra-260127195414`
- **DNS**: Should point to `secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io`

### ⏳ registry.secairadar.com
- **Status**: Not yet added
- **DNS Required**: CNAME pointing to `secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io`

## Container App Details

- **Name**: `secai-radar-public-api`
- **Resource Group**: `secai-radar-rg`
- **Environment**: `secai-radar-dev-env`
- **Default FQDN**: `secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io`

## Adding registry.secairadar.com

### Step 1: Configure DNS

Add a CNAME record:

```
Type: CNAME
Name: registry.secairadar.com
Value: secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io
TTL: 3600 (or default)
```

### Step 2: Verify DNS Propagation

```bash
# Check DNS
dig registry.secairadar.com CNAME
# Should return: secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io
```

### Step 3: Add Domain to Container App

Once DNS is configured and propagated (usually 5-15 minutes), run:

```bash
# Add the domain
az containerapp hostname add \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --hostname registry.secairadar.com

# Bind with managed certificate
az containerapp hostname bind \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --hostname registry.secairadar.com \
  --environment secai-radar-dev-env \
  --validation-method HTTP
```

Or use the automated script:

```bash
./scripts/add-container-app-custom-domains.sh
```

## Verify Configuration

### List all custom domains:

```bash
az containerapp hostname list \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  -o table
```

### Check specific domain:

```bash
az containerapp hostname list \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --query "[?name=='registry.secairadar.com']" -o json
```

### Test domains:

```bash
# Test api.secairadar.cloud
curl https://api.secairadar.cloud/api/v1/public/health

# Test registry.secairadar.com (after configuration)
curl https://registry.secairadar.com/api/v1/public/health
```

## Managed Certificates

Azure Container Apps automatically provisions and manages SSL/TLS certificates for custom domains. The certificates are:

- **Automatically renewed** by Azure
- **Free** (no additional cost)
- **Provisioned** within 5-15 minutes after DNS is configured
- **Validated** via HTTP validation method

## Troubleshooting

### Domain validation fails

1. **Check DNS**: Ensure CNAME points to the correct FQDN
2. **Wait for propagation**: DNS changes can take up to 24 hours (usually 5-15 minutes)
3. **Verify DNS**: Use `dig` or `nslookup` to confirm DNS resolution

### Certificate not provisioning

1. **Check binding status**: `az containerapp hostname list` should show `SniEnabled`
2. **Wait**: Managed certificates can take 5-15 minutes to provision
3. **Check DNS**: Certificate provisioning requires valid DNS configuration

### Domain shows "Disabled" binding

Run the bind command again:

```bash
az containerapp hostname bind \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --hostname <domain> \
  --environment secai-radar-dev-env \
  --validation-method HTTP
```

## Quick Reference Commands

```bash
# List domains
az containerapp hostname list --name secai-radar-public-api --resource-group secai-radar-rg

# Add domain
az containerapp hostname add --name secai-radar-public-api --resource-group secai-radar-rg --hostname <domain>

# Bind certificate
az containerapp hostname bind --name secai-radar-public-api --resource-group secai-radar-rg --hostname <domain> --environment secai-radar-dev-env

# Remove domain
az containerapp hostname delete --name secai-radar-public-api --resource-group secai-radar-rg --hostname <domain>
```
