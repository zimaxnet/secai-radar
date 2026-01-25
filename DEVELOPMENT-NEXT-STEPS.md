# Development Next Steps (According to Plan)

**Reference:** 7-step refactoring process, `REFACTORING-PROGRESS.md`, `DEPLOYMENT-NEXT-STEPS.md`  
**Last updated:** 2026-01-25

## Current State

- **Phases 0–4:** Implemented (monorepo, public-api, registry-api, workers, scoring, graph).
- **SWA:** Standard tier ✅; app_location `apps/public-web`, output `dist`.
- **Database:** `secairadar` on `ctxeco-db` (ctxeco-rg); migrations ready, not yet run.
- **Containers:** public-api, registry-api, publisher built locally; ready to push to ACR.

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

### 5. Link SWA to Public API (Standard tier)

With SWA on **Standard** you can attach a backend:

- **Option A – SWA “Linked backends”:**  
  In Azure Portal: Static Web App → **Backends** → Link backend → choose the Public API Container App (or its FQDN).  
  Then set **Application settings** so the frontend calls that backend (e.g. `VITE_API_BASE` or use the SWA proxy path).

- **Option B – Frontend env only:**  
  Set `VITE_API_BASE` in GitHub (or SWA app settings) to the Public API base URL, e.g.  
  `https://<public-api-fqdn>/api`  
  so the SPA calls the API directly. No SWA backend link needed for that.

### 6. Configure frontend API base

- **GitHub:** Repository → Settings → Secrets and variables → Actions → add or update `VITE_API_BASE` (e.g. `https://<public-api-host>/api`).
- **SWA:** Configuration → Application settings → add `VITE_API_BASE` if build reads it from there.

### 7. Test end-to-end

- [ ] SWA loads at secairadar.cloud (or default hostname).
- [ ] Public API: `GET /health` and `GET /api/v1/public/health` return 200.
- [ ] MCP pages load and hit the API (Overview, Rankings, Server Detail, Daily Brief).
- [ ] Feeds: `/mcp/feed.json` (and RSS if implemented) return valid data.

### 8. Daily pipeline

- Workflow: `.github/workflows/daily-pipeline.yml` (e.g. 02:30 UTC).
- First run: trigger manually from Actions; confirm workers run and DB is updated.

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
