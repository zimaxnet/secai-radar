# Development Next Steps (According to Plan)

**Reference:** 7-step refactoring process, `REFACTORING-PROGRESS.md`, `DEPLOYMENT-NEXT-STEPS.md`  
**Last updated:** 2026-01-25

## Current State

- **Phases 0–4:** Implemented (monorepo, public-api, registry-api, workers, scoring, graph).
- **SWA:** Standard tier ✅; app_location `apps/public-web`, output `dist`.
- **Database:** `secairadar` on `ctxeco-db` (ctxeco-rg); migrations and seed run ✅.
- **Containers:** public-api and registry-api deploy via GitHub Actions to Azure Container Apps ✅.
- **Public API FQDN:** `secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io`
- **VITE_API_BASE:** Set in GitHub secrets → frontend will call the deployed API after the next deploy.

## Ordered Plan (Do in This Order)

### 1. Run database migrations

Required before the Public API can serve real data.

**Option A – from repo root (recommended):**
```bash
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
./scripts/run-migrations.sh
```

**Option B – from apps/public-api with venv:**
```bash
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
cd apps/public-api
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python scripts/migrate.py
```

- Uses `docs/implementation/database-schema.sql` (repo root).
- Run once per environment; schema is not idempotent.
- **Credentials:** Store `DATABASE_URL` in Key Vault and set GH secrets via `./scripts/update-credentials.sh` and **docs/CREDENTIALS-SETUP.md**.
- If you see "Connection refused", set `DATABASE_URL` to the Azure Postgres URL (and ensure firewall allows your IP or Azure services).

### 2. Seed sample data (optional)

```bash
cd apps/public-api
python scripts/seed.py
```

### 3. Deploy infrastructure (no new DB) ✅

Uses existing PostgreSQL; creates Storage, Key Vault, Container Apps Environment, ACR.

```bash
cd infra
az deployment group create \
  --resource-group secai-radar-rg \
  --template-file mcp-infrastructure-existing-db.bicep \
  --parameters parameters/dev-existing-db.bicepparam
```

**Status:** Deployed 2026-01-25. Get ACR and env names:
```bash
az deployment group show -g secai-radar-rg -n mcp-infrastructure-existing-db --query "properties.outputs" -o table
```

### 4. Build and push containers + Deploy to Container Apps (GitHub Actions)

**Handled by:** `.github/workflows/deploy-staging.yml` (on push to `main` or `workflow_dispatch`).

The workflow:

- Builds and pushes `secai-radar-public-api` and `secai-radar-registry-api` to ACR.
- **Deploys public-api:** creates the Container App on first run (requires `DATABASE_URL` secret), or updates the image on subsequent runs. Uses ACR admin credentials from `az acr credential show` (no extra secrets).
- **Deploys registry-api:** create or update in the same way.

**Required secrets (Settings → Secrets and variables → Actions):**

- `AZURE_CREDENTIALS` – service principal JSON
- `ACR_NAME` – e.g. `secairadardevacr`
- `AZURE_STATIC_WEB_APPS_API_TOKEN`
- `DATABASE_URL` – required when creating public-api for the first time (PostgreSQL connection string)

**Optional:**

- `VITE_API_BASE` – e.g. `https://<public-api-fqdn>/api` (so the frontend calls the deployed API)
- Variable `CONTAINER_APPS_ENV` – defaults to `secai-radar-dev-env` if unset

**Manual one-off (if you prefer not to use the workflow for create):** run the same `az containerapp create` locally once, then the workflow will only perform `az containerapp update --image ...` on future runs.

### 5. Link SWA to Public API (Standard tier) ✅

**Done:** `VITE_API_BASE` set in GitHub secrets so the SPA calls the deployed public-api; deploy was re-triggered to rebuild the frontend.

With SWA on **Standard** you can also attach a backend:

- **Option A – SWA “Linked backends”:**  
  In Azure Portal: Static Web App → **Backends** → Link backend → choose the Public API Container App (or its FQDN).  
  Then set **Application settings** so the frontend calls that backend (e.g. `VITE_API_BASE` or use the SWA proxy path).

- **Option B – Frontend env only:**  
  Set `VITE_API_BASE` in GitHub (or SWA app settings) to the Public API base URL, e.g.  
  `https://<public-api-fqdn>/api`  
  so the SPA calls the API directly. No SWA backend link needed for that.

### 6. Configure frontend API base ✅

- **Done:** `VITE_API_BASE` is in repository Secrets; the deploy-staging workflow uses it when building public-web.

### 7. Test end-to-end

Run from repo root:
```bash
./scripts/test-e2e.sh
```
Override API base if needed: `PUBLIC_API_BASE=https://your-api.example.com ./scripts/test-e2e.sh`

Manual checks:
- [ ] SWA loads: try **https://purple-moss-0942f9e10.3.azurestaticapps.net** first (default hostname). If that works but **https://secairadar.cloud** does not, see **docs/SWA-SITE-TROUBLESHOOTING.md** (DNS/custom domain).
- [ ] MCP pages load and use the API (Overview, Rankings, Server Detail, Daily Brief).
- [ ] Feeds: `/api/v1/public/mcp/feed.json` returns valid JSON.

### 8. Daily pipeline

- **Workflow:** `.github/workflows/daily-pipeline.yml` (schedule: 02:30 UTC daily; or **Run workflow** from Actions).
- **Secrets:** Uses `DATABASE_URL` (already set).
- **Note:** Scout and Curator have runnable workers. Evidence Miner, Drift Sentinel, and Sage Meridian still need `src/` entrypoints; the pipeline will fail at the first missing worker until those are implemented.

---

## Backlog (After Above)

- **Private registry:** Auth (Entra ID), RBAC, registry-api and app.secairadar.cloud.
- **GK explorer:** Graph UI and any graph-specific endpoints.
- **Production hardening:** Secrets in Key Vault, WAF/Front Door, monitoring.

---

## Key Files

| Purpose | Path |
|--------|------|
| Migration script | `apps/public-api/scripts/migrate.py` |
| Schema | `docs/implementation/database-schema.sql` |
| Infra (existing DB) | `infra/mcp-infrastructure-existing-db.bicep` |
| Public API app | `apps/public-api/main.py` |
| SWA config / build | `apps/public-web/`, `.github/workflows/azure-static-web-apps.yml` |
| Plan summary | `REFACTORING-PROGRESS.md` |
| Containers / SWA Standard | `docs/SWA-STANDARD-AND-CONTAINERS.md` |
