# SecAI Radar Azure Deployment Inventory

## Resource Overview (as of 2025-11)
- **Subscription**: 23f4e2c5-0667-4514-8e2e-f02ca7880c95
- **Primary Resource Group**: `secai-radar-rg`
- **Supporting Resource Groups**:
  - `rg-KDOL_hub` (shared networking, DNS private zones)
  - `dns-rg` (public DNS for `zimax.net`)
- **Identity Tenant**: 8838531d-55dd-4018-8341-77705f4845f4

## Live Application Footprint
- **Azure Static Web App**: `secai-radar`
  - Tier: Free
  - Domains: `secai-radar.zimax.net`, `purple-moss-0942f9e10.3.azurestaticapps.net`
  - GitHub Source: `zimaxnet/secai-radar` (`main`)
- **Azure Functions App**: `secai-radar-api`
  - Plan: Consumption (Linux)
  - Status: App running, functions pending deployment
  - Settings: `VITE_API_BASE=https://secai-radar-api.azurewebsites.net/api`
- **Azure Storage Account**: `secairadarsa`
  - Services: Blob (evidence, exports), Table (controls, tools, evidence metadata)
  - Redundancy: Standard_LRS
- **Azure Key Vault**: `secai-radar-kv-*`
  - Purpose: Store Azure OpenAI secrets, function app configuration
  - Access: Managed Identity for `secai-radar-api`
- **Azure OpenAI**: `secai-radar-aoai`
  - Model: GPT‑4o (preferred), GPT‑4 Turbo (legacy fallback)
  - Usage: Recommendations, evidence classification, report generation

## Deployment & Automation Services
- **GitHub Actions**: Deploy Static Web App and Functions (`Deploy Azure Functions` workflow)
- **Azure Monitor / App Insights**: Not provisioned (gap)
- **CI/CD Secrets**:
  - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` (pending)
  - `VITE_API_BASE` (configured)

## Quotas & Capacity Notes
- **Static Web App**: Free tier provides 100 GB/month bandwidth, 2 staging slots max; upgrade required if exceeded.
- **Functions Consumption Plan**: 1 million executions + 400,000 GB-s free per month; expect <$15/month under moderate load.
- **Azure OpenAI**: Provisioned at standard regional quota; monitor token usage to stay within 5M token/day soft limit.
- **Storage Account**: Current footprint <5 GB; Cool tier recommended for evidence >180 days (per ADR 0005).

## Cost Baseline (reference `docs/COST-ESTIMATION.md`)
- **Minimal (AI Off)**: $2–5/month
- **Moderate (AI On)**: $18–41/month
- **Heavy Usage**: $74–146/month
- Key driver: Azure OpenAI token consumption (50–70% of total when enabled)

## Outstanding Gaps / Follow-Ups
- Deploy functions to `secai-radar-api` and confirm managed identity access to Key Vault.
- Enable Application Insights or Log Analytics to track execution counts and latency.
- Configure Azure Cost Management budgets: total $50/month, AI $30/month, storage $10/month, functions $20/month.
- Document private DNS mappings for hub/spoke networks once provisioned (per corporate standard).

## Data Sources
- [`docs/CURRENT-STATUS.md`](../CURRENT-STATUS.md)
- [`docs/DEPLOYMENT-STATUS-SUMMARY.md`](../DEPLOYMENT-STATUS-SUMMARY.md)
- [`docs/COST-ESTIMATION.md`](../COST-ESTIMATION.md)
- [`docs/azure-portal-config.md`](../azure-portal-config.md)
