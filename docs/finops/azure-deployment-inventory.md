# SecAI Radar Azure Deployment Inventory

## Resource Overview (as of 2026-01)
- **Subscription**: 23f4e2c5-0667-4514-8e2e-f02ca7880c95
- **Primary Resource Group**: `secai-radar-rg`
- **Supporting Resource Groups**:
  - `ctxeco-rg` (existing PostgreSQL Flexible Server `ctxeco-db` — secairadar database)
  - `rg-KDOL_hub` (shared networking, DNS private zones) if used
  - `dns-rg` (public DNS for `zimax.net`)
- **Identity Tenant**: 8838531d-55dd-4018-8341-77705f4845f4

## Live Application Footprint (Verified MCP)

- **Azure Static Web App**: `secai-radar`
  - **Tier: Standard** (required for backend linking, staging)
  - Domains: secairadar.cloud, `secai-radar.zimax.net`, default *.azurestaticapps.net
  - Source: GitHub Actions → build from `apps/public-web`, deploy to SWA
- **Azure Container Apps** (consumption, in `secai-radar-dev-env` or similar):
  - **secai-radar-public-api** – REST API for MCP overview, rankings, server detail; image from ACR.
  - **secai-radar-registry-api** – Registry API; image from ACR.
- **Image registry**: **GitHub Container Registry (ghcr.io)** — images `ghcr.io/<org>/secai-radar-public-api:latest` and `ghcr.io/<org>/secai-radar-registry-api:latest`. Azure Container Registry (ACR) is optional; omit with `deployContainerRegistry: false` in Bicep when using ghcr.io (see [USING-GHCR-INSTEAD-OF-ACR.md](./USING-GHCR-INSTEAD-OF-ACR.md)).
- **Log Analytics**: `secai-radar-dev-law` (or equivalent)
  - SKU: PerGB2018, 30-day retention; used by Container Apps environment
- **Azure Storage Account**: `secairadardevsa` (or equivalent, from Bicep)
  - Blob: `evidence-private`, `public-assets`, `exports-private`
  - Redundancy: Standard_LRS
- **Azure Key Vault**: `secai-radar-dev-kv` (or equivalent)
  - Purpose: secrets (e.g. DATABASE_URL reference for Container Apps), RBAC
- **PostgreSQL**: **Existing** `ctxeco-db` (Flexible Server in `ctxeco-rg`)
  - Database: `secairadar`; used by public-api via `DATABASE_URL`
  - Not provisioned by SecAI Bicep; cost attributed to ctxEco unless allocated to SecAI

## Deployment & Automation
- **GitHub Actions**: “Deploy to Staging” — builds public-web, deploys SWA; builds and pushes public-api + registry-api to ACR; deploys both to Container Apps.
- **Secrets**: `AZURE_CREDENTIALS`, `AZURE_STATIC_WEB_APPS_API_TOKEN`, `DATABASE_URL`, `GHCR_PAT` (read:packages for Container Apps to pull from ghcr.io); optional `VITE_API_BASE`, `CONTAINER_APPS_ENV`.

## Cost Implications
See **[SECAI-INFRA-COST-IMPLICATIONS.md](./SECAI-INFRA-COST-IMPLICATIONS.md)** for per-resource and total order-of-magnitude monthly costs (~\$22–55 SecAI-only; ~\$40–105 if allocating a Postgres share).

Legacy stack (SWA Free, Functions, OpenAI) scenarios remain in [COST-ESTIMATION.md](./COST-ESTIMATION.md).

## Outstanding / Follow-Ups
- Configure Azure Cost Management budgets (e.g. total, Container Apps, Log Analytics).
- Document private DNS / hub-spoke mappings if adopted.

## Data Sources
- [SECAI-INFRA-COST-IMPLICATIONS.md](./SECAI-INFRA-COST-IMPLICATIONS.md)
- [COST-ESTIMATION.md](./COST-ESTIMATION.md) (legacy scenarios)
- `infra/mcp-infrastructure-existing-db.bicep`, `.github/workflows/deploy-staging.yml`
- [CONTAINER-APP-REVISION-TROUBLESHOOTING.md](../CONTAINER-APP-REVISION-TROUBLESHOOTING.md)
