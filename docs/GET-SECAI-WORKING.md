# Get SecAI Radar Working (deploy checklist)

Use this when bringing up or fixing the staging app so you can proceed with updates.

---

## 1. GitHub secrets (required for deploy)

In the repo: **Settings → Secrets and variables → Actions**, ensure:

| Secret | Purpose |
|--------|---------|
| `AZURE_CREDENTIALS` | Service principal JSON for `secai-radar-rg` (and SWA) |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | From the Static Web App → Manage deployment token |
| `DATABASE_URL` | PostgreSQL connection string for public-api (e.g. `postgresql://ctxecoadmin:PASSWORD@ctxeco-db.postgres.database.azure.com:5432/secairadar?sslmode=require`) |
| `GHCR_PAT` | GitHub PAT with `read:packages` + `write:packages` so the workflow can push images to ghcr.io |

Optional:

| Secret / variable | Purpose |
|-------------------|---------|
| `VITE_API_BASE` | Frontend API base URL, e.g. `https://<public-api-fqdn>/api`. If unset, the workflow uses a default; if the app spins or shows "Unable to load dashboard", set this and re-run deploy. |
| `CONTAINER_APPS_ENV` (variable) | Container Apps environment name; default `secai-radar-dev-env`. |

**Database URL:** If you use the shared ctxeco-db, see [CREDENTIALS-SETUP.md](CREDENTIALS-SETUP.md) and the workspace **INTEGRATED-WORKSPACE-DATABASE.md**. The script `./scripts/update-db-credentials-secai-ctxeco.sh` can sync the password into **secai-radar-kv** `database-url`; use that value (or build it from ctxecokv `postgres-password`) for `DATABASE_URL` in GitHub.

---

## 2. Run deploy

- **Push to `main`** or run **Actions → Deploy to Staging → Run workflow**.

The workflow will:

1. Build public-web (with `VITE_API_BASE` from secret or default) and deploy to Azure Static Web Apps.
2. Build and push public-api + registry-api to ghcr.io, then deploy them to Container Apps.
3. Print a **Deploy summary** with the public-api FQDN and the exact `VITE_API_BASE` to use.

---

## 3. If the app spins or shows "Unable to load dashboard"

- **Spinning forever:** Static assets were not excluded from the SPA fallback. The repo uses `staticwebapp.config.json` with `"exclude": ["/api/*", "/assets/*", ...]`. Ensure the workflow copies it into `dist/` and redeploy.
- **"Unable to load dashboard":** The frontend is calling the wrong API URL or the API is down.

Do this:

1. Open the last **Deploy to Staging** run → **Deploy summary** step. It prints something like:
   ```text
   VITE_API_BASE for next build: https://secai-radar-public-api.<env>.<region>.azurecontainerapps.io/api
   ```
2. Add or update GitHub secret **VITE_API_BASE** with that value (including `/api`).
3. Re-run the workflow so the frontend is rebuilt with the correct API base.
4. Confirm public-api is healthy: open `https://<public-api-fqdn>/health` and `https://<public-api-fqdn>/api/v1/public/health`. If those fail, check Container App logs and `DATABASE_URL`.

---

## 4. Quick verification

- **Static site:** Open the SWA URL (from Azure Portal → your Static Web App).
- **Public API:** `curl https://<public-api-fqdn>/api/v1/public/health`
- **Dashboard:** Go to `/mcp`; you should see the Verified MCP dashboard or an explicit error + Retry, not an endless spinner.

---

## Related

- [CREDENTIALS-SETUP.md](CREDENTIALS-SETUP.md) – PostgreSQL, Key Vaults, GitHub secrets in detail.
- [.github/workflows/deploy-staging.yml](../.github/workflows/deploy-staging.yml) – workflow and required secrets.
- **INTEGRATED-WORKSPACE-DATABASE.md** (workspace root) – shared DB, credential update flow, Zep.
