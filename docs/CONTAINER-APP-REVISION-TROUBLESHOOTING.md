# Container App revision failed – troubleshooting

When **secai-radar-public-api** Revision management shows failures (e.g. in [Azure Portal Revision management](https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/containerApps/secai-radar-public-api/revisionManagement)), use this guide.

**App:** `secai-radar-public-api`  
**Resource group:** `secai-radar-rg`

---

## 1. See why the revision failed (Portal)

1. Open the app → **Application** → **Revisions and replica** (or **Revision management**).
2. Click the **failed** revision name.
3. Use **“Log stream”** or **“System logs”** (and **“View details”** next to System logs).
4. At the bottom of system logs, look for:
   - **ErrImagePull** – image not found or ACR auth failed.
   - **CrashLoopBackOff** / **Exit Code 1** – app exits on startup (e.g. missing env, DB connection, Python error).
   - **Timeout** – app didn’t respond to probes in time.

---

## 2. See revisions and logs (Azure CLI)

```bash
# List revisions and status
az containerapp revision list \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --output table

# Stream logs (latest revision)
az containerapp logs show \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --follow

# Or for a specific revision
az containerapp logs show \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --revision <REVISION_NAME> \
  --follow
```

Replace `<REVISION_NAME>` with a revision from the list (e.g. `secai-radar-public-api--abc123`).

---

## 3. Common causes and fixes

| Symptom | Likely cause | What to do |
|--------|----------------|------------|
| **ErrImagePull** | ACR credentials or image path wrong | Confirm workflow uses correct `ACR_NAME` and that the image `*.azurecr.io/secai-radar-public-api:latest` exists. Re-run “Build and push public-api” then “Deploy public-api to Container Apps”. |
| **Exit 1 / CrashLoopBackOff** | App crashes on startup | Check container logs (Portal or `az containerapp logs show`). Typical: invalid **DATABASE_URL**, missing env, or Python exception at import/startup. Ensure **DATABASE_URL** secret is set in GitHub and that the app can reach the DB (e.g. firewall allows Container Apps). |
| **Timeout / probe failure** | App not responding on port 8000 or `/health` | App must listen on `0.0.0.0:8000` and serve `GET /health` with 200. The Dockerfile was updated to use a stdlib-only healthcheck; ensure the image was rebuilt and that no custom liveness/readiness path overrides this. |
| **Revision stays “Provisioning”** | Image pull or platform delay | Wait a few minutes. If it never becomes “Running”, check system logs for image or runtime errors. |

---

## 4. Health check and probes

The public API container:

- Listens on **port 8000**.
- Exposes **GET /health** returning `{"status":"ok",...}`.

The Dockerfile uses a HEALTHCHECK that calls `http://127.0.0.1:8000/health` via Python `urllib` (no extra deps). If Azure Container Apps is configured with custom liveness/readiness probes, they should use **path** `/health` and **port** 8000. The default HTTP probe may use `/`; if the app returns 404 on `/`, that can fail. Prefer setting an explicit **readiness** (and if needed **liveness**) probe to `/health` on port 8000 in the app’s container template.

---

## 5. Re-deploy after fixes

1. Fix code/config (e.g. Dockerfile, env, or probes).
2. Commit and push to `main`, or run the **“Deploy to Staging”** workflow manually.
3. When the workflow finishes, a new revision is created. In **Revision management**, confirm the new revision is **Running** and receiving traffic.

To force a new revision without code changes (e.g. after fixing only secrets):

- In GitHub Actions, re-run the **“Deploy public-api to Container Apps”** job, or
- Run the same `az containerapp update` / `az containerapp secret set` steps locally with the correct env and secrets.
