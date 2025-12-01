---
layout: default
title: Azure Dns Verification
---

> **Update (2025-11):** The wiki now publishes at `https://zimaxnet.github.io/secai-radar/`. References to the former `/wiki` subdirectory are retained for historical context.


# Azure DNS Verification and Configuration

Complete guide for verifying and configuring DNS in Azure for SecAI Radar.

---

## Current Status

✅ **DNS Zone Found**: `zimax.net` exists in Azure
- Resource Group: `dns-rg`
- Subscription: `23f4e2c5-0667-4514-8e2e-f02ca7880c95`

❌ **CNAME Record Missing**: `secai-radar` CNAME record not found

---

## Required DNS Configuration

### CNAME Record

Both the main app and wiki use the **same domain** (`secai-radar.zimax.net`). You need **one CNAME record**:

```
Type: CNAME
Name: secai-radar
Value: {your-github-username}.github.io
TTL: 3600
```

**Note**: Replace `{your-github-username}` with your actual GitHub username or organization name.

---

## Verification Script

A verification script is available at `scripts/verify-dns.sh`:

```bash
./scripts/verify-dns.sh
```

This script:
- Checks Azure login status
- Verifies DNS zone exists
- Checks for CNAME record
- Tests DNS resolution
- Provides summary of configuration

---

## Configuration Script

A configuration script is available at `scripts/configure-dns.sh`:

```bash
./scripts/configure-dns.sh
```

This script:
- Checks Azure login
- Verifies DNS zone exists (or creates it)
- Creates or updates CNAME record
- Configures TTL
- Provides summary

---

## Manual Configuration

### Option 1: Using Azure CLI

```bash
# Set variables
RESOURCE_GROUP="dns-rg"
DNS_ZONE="zimax.net"
GITHUB_USERNAME="your-username"  # Replace with your GitHub username

# Create CNAME record
az network dns record-set cname create \
  --resource-group "$RESOURCE_GROUP" \
  --zone-name "$DNS_ZONE" \
  --name "secai-radar" \
  --cname "${GITHUB_USERNAME}.github.io" \
  --ttl 3600
```

### Option 2: Using Azure Portal

1. Go to **Azure Portal** → **DNS zones**
2. Select **zimax.net** zone
3. Click **+ Record set**
4. Configure:
   - **Name**: `secai-radar`
   - **Type**: `CNAME`
   - **Alias**: `{your-github-username}.github.io`
   - **TTL**: `3600`
5. Click **OK**

---

## Verification Steps

### 1. Verify CNAME Record Exists

```bash
az network dns record-set cname show \
  --resource-group "dns-rg" \
  --zone-name "zimax.net" \
  --name "secai-radar"
```

### 2. Check DNS Resolution

```bash
# Using dig
dig secai-radar.zimax.net CNAME

# Using nslookup
nslookup -type=CNAME secai-radar.zimax.net
```

Expected output should show:
- **Type**: CNAME
- **Value**: `{your-github-username}.github.io`

### 3. Test Domain Access

- **Main App**: `https://secai-radar.zimax.net`
- **Wiki**: `https://zimaxnet.github.io/secai-radar`

---

## Current Configuration Status

### ✅ Configured

- DNS Zone: `zimax.net` exists in Azure
- Resource Group: `dns-rg`
- Subscription: `23f4e2c5-0667-4514-8e2e-f02ca7880c95`

### ❌ Missing

- CNAME record: `secai-radar` → `{your-github-username}.github.io`

---

## Next Steps

1. **Determine GitHub Username**: Find your GitHub username or organization name
2. **Create CNAME Record**: Use the configuration script or manual method above
3. **Verify DNS**: Run verification script to confirm
4. **Wait for Propagation**: DNS propagation can take 1-24 hours (usually 1-2 hours)
5. **Test Access**: Verify both app and wiki are accessible

---

## Troubleshooting

### CNAME Record Not Found

**Symptom**: Verification script shows CNAME record doesn't exist

**Solution**: 
1. Run configuration script: `./scripts/configure-dns.sh`
2. Or manually create CNAME record using Azure CLI/Portal
3. Verify with: `./scripts/verify-dns.sh`

### DNS Not Resolving

**Symptom**: DNS resolution fails or doesn't point to GitHub

**Solutions**:
1. **Check DNS Record**: Verify CNAME record exists and is correct
2. **Wait for Propagation**: DNS changes can take up to 24 hours
3. **Check GitHub Pages**: Verify GitHub Pages is configured for your repository
4. **Clear DNS Cache**: Clear local DNS cache if needed

### Wrong GitHub Username

**Symptom**: CNAME points to wrong GitHub Pages URL

**Solution**:
1. Update CNAME record with correct GitHub username
2. Use configuration script to update
3. Wait for DNS propagation

---

## Quick Reference

### Azure CLI Commands

```bash
# List DNS zones
az network dns zone list

# List CNAME records in zone
az network dns record-set cname list \
  --resource-group "dns-rg" \
  --zone-name "zimax.net"

# Show specific CNAME record
az network dns record-set cname show \
  --resource-group "dns-rg" \
  --zone-name "zimax.net" \
  --name "secai-radar"

# Create CNAME record
az network dns record-set cname create \
  --resource-group "dns-rg" \
  --zone-name "zimax.net" \
  --name "secai-radar" \
  --cname "{your-github-username}.github.io" \
  --ttl 3600

# Update CNAME record
az network dns record-set cname set-record \
  --resource-group "dns-rg" \
  --zone-name "zimax.net" \
  --record-set-name "secai-radar" \
  --cname "{your-github-username}.github.io" \
  --ttl 3600

# Delete CNAME record (if needed)
az network dns record-set cname delete \
  --resource-group "dns-rg" \
  --zone-name "zimax.net" \
  --name "secai-radar" \
  --yes
```

---

## Important Notes

1. **Same Domain**: Both app and wiki use `secai-radar.zimax.net`
2. **Single CNAME**: Only one CNAME record needed for both
3. **GitHub Username**: Must match your GitHub username or organization
4. **DNS Propagation**: Changes can take 1-24 hours to propagate
5. **SSL Certificate**: GitHub will issue SSL certificate automatically

---

**Related**: [DNS-CONFIGURATION.md](docs/wiki/DNS-CONFIGURATION.md) | [GitHub-Pages-Deployment-Instructions.md](docs/wiki/GitHub-Pages-Deployment-Instructions.md)
