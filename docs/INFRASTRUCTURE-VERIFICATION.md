# Infrastructure Verification and Cost Monitoring

This guide explains how to verify your Azure infrastructure deployment and monitor costs for the SecAI Radar application.

## Quick Start

### Verify All Infrastructure

```bash
# Run the comprehensive verification script
./scripts/verify-infrastructure.sh
```

This script checks:
- ✅ Resource Group existence and location
- ✅ Storage Account (status and SKU)
- ✅ Function Plan (SKU, workers, pre-warmed instances)
- ✅ Function App (status and URL)
- ✅ Application Insights (daily cap configuration)
- ✅ Static Web App (if deployed)
- ✅ Cosmos DB (if deployed, including free tier status)
- ✅ Key Vault (if deployed)
- ✅ Storage Queues

### Monitor Costs

```bash
# Quick cost check
./scripts/monitor-costs.sh
```

This script provides:
- Current month-to-date costs (if available)
- Cost breakdown by resource type
- Estimated monthly costs based on SKUs
- Links to Azure Portal cost management

## Scripts Overview

### `verify-infrastructure.sh`

**Purpose**: Comprehensive infrastructure verification and health check

**Features**:
- Verifies all resources from Bicep deployment
- Checks resource status and configuration
- Provides cost estimates based on SKUs
- Offers cost optimization recommendations
- Color-coded output (✅ success, ⚠️ warning, ❌ failure)

**Usage**:
```bash
# Use default settings (secai-radar-dev-rg)
./scripts/verify-infrastructure.sh

# Override resource group
RESOURCE_GROUP=secai-radar-prod-rg ./scripts/verify-infrastructure.sh

# Override environment
ENVIRONMENT=prod ./scripts/verify-infrastructure.sh
```

**Environment Variables**:
- `RESOURCE_GROUP`: Resource group name (default: `secai-radar-dev-rg`)
- `ENVIRONMENT`: Environment suffix (default: `dev`)
- `APP_NAME`: Application name (default: `secai-radar`)
- `LOCATION`: Azure region (default: `eastus2`)

**Output**:
- Summary of all checks with pass/fail status
- Resource-specific details (SKUs, URLs, status)
- Cost estimates and optimization tips
- Exit code: 0 if all checks pass, 1 if failures

### `monitor-costs.sh`

**Purpose**: Quick cost monitoring and estimation

**Features**:
- Current month-to-date costs (via Azure Cost Management API)
- Resource-specific cost estimates
- Links to Azure Portal cost management
- Budget alert setup guidance

**Usage**:
```bash
# Use default settings
./scripts/monitor-costs.sh

# Override resource group
RESOURCE_GROUP=secai-radar-prod-rg ./scripts/monitor-costs.sh
```

**Prerequisites**:
- Azure CLI installed and authenticated
- Cost Management Reader role (for actual cost data)
- Optional: `jq` for detailed cost breakdowns

## Cost Management

### Understanding Costs

The SecAI Radar infrastructure is designed to be cost-conscious:

1. **Function Plan (Elastic Premium EP1)**
   - Base cost: ~$0.20/hour when running
   - With `preWarmedInstanceCount=0`: Pay only for actual usage
   - Estimated: $50-100/month for typical usage

2. **Storage Account (Standard LRS)**
   - First 50GB free
   - Then ~$0.92/month per 50GB
   - Transactions: ~$0.004 per 10,000 operations

3. **Application Insights**
   - First 5GB free per month
   - Then $2.30/GB ingested
   - Daily cap configured to prevent surprises

4. **Static Web App**
   - Free tier: $0/month
   - Standard tier: ~$9/month

5. **Cosmos DB (Optional)**
   - Free tier: $0/month (1,000 RU/s + 25GB for 12 months)
   - Provisioned: ~$23-230/month depending on throughput

### Cost Optimization Tips

1. **Keep Pre-warmed Instances at 0**
   - Set `preWarmedInstanceCount=0` in Bicep parameters
   - Reduces idle costs significantly

2. **Configure Application Insights Daily Cap**
   - Set `appInsightsDailyCapGb` in Bicep parameters
   - Prevents unexpected data ingestion costs

3. **Use Free Tier Where Possible**
   - Static Web App: Free tier is sufficient for development
   - Cosmos DB: Enable free tier if within limits

4. **Monitor Regularly**
   - Run `monitor-costs.sh` weekly
   - Set up budget alerts in Azure Portal
   - Review cost analysis monthly

### Setting Up Budget Alerts

1. Go to [Azure Cost Management - Budgets](https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/Budgets)
2. Click **Add** → **Create budget**
3. Configure:
   - **Scope**: Resource Group → `secai-radar-dev-rg`
   - **Budget amount**: e.g., $100/month
   - **Alert conditions**: 50%, 75%, 90%, 100% of budget
   - **Email recipients**: Your team email addresses
4. Save the budget

### Viewing Costs in Azure Portal

**Cost Analysis**:
```
https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/costanalysis
```

**Resource Group Costs**:
```
https://portal.azure.com/#@/resource/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/costAnalysis
```

## Troubleshooting

### "Cost data not available via CLI"

**Cause**: Missing Cost Management Reader role or costs haven't been calculated yet

**Solution**:
1. Assign Cost Management Reader role:
   ```bash
   az role assignment create \
     --assignee <your-email> \
     --role "Cost Management Reader" \
     --scope /subscriptions/{SUBSCRIPTION_ID}
   ```
2. Wait 24-48 hours for costs to be calculated
3. Use Azure Portal for immediate cost viewing

### "Resource not found" errors

**Cause**: Resource name mismatch or resource in different resource group

**Solution**:
1. Check actual resource names:
   ```bash
   az resource list --resource-group $RESOURCE_GROUP --output table
   ```
2. Override script variables to match actual names
3. Check if resources are in different resource groups

### "Command not found: az"

**Cause**: Azure CLI not installed or not in PATH

**Solution**:
1. Install Azure CLI:
   ```bash
   # macOS
   brew install azure-cli
   
   # Linux
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```
2. Authenticate:
   ```bash
   az login
   ```

## Regular Maintenance

### Weekly
- Run `verify-infrastructure.sh` to check resource health
- Run `monitor-costs.sh` to review spending

### Monthly
- Review Azure Portal cost analysis
- Check budget alerts and adjust if needed
- Review resource utilization and optimize SKUs

### Quarterly
- Review and optimize Function Plan SKU
- Review Application Insights sampling and daily cap
- Consider reserved capacity for predictable workloads

## Related Documentation

- [Deployment Guide](./deployment.md) - Initial infrastructure setup
- [Bicep Infrastructure](../infra/README.md) - Infrastructure as Code details
- [Cost Optimization ADR](./adr/0001-architecture-and-storage.md) - Architecture decisions

