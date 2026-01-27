# SWA Standard and Container Readiness

## SWA Standard required before linking containers

**You need Azure Static Web Apps in Standard tier before creating and linking Container Apps** (or other backends) to the static site.

- **Free tier** does not support backend links / custom backends, staging environments, or custom domains in the same way Standard does.
- **Standard** is required for:
  - Linking to APIs (Container Apps, Azure Functions, etc.)
  - Custom domains and SSL as used for production
  - Staging slots and approval flows

**Order of operations:**

1. ~~**Upgrade SWA to Standard**~~ **Done:** `secai-radar` is on **Standard** (upgraded via `az staticwebapp update --sku Standard`).
2. **Then** create and deploy the API containers (e.g. to Container Apps).
3. **Then** link the SWA to the API backend(s) and configure environment (e.g. `VITE_API_BASE` or SWA app settings).

### Upgrade command (for reference)

```bash
az staticwebapp update --name secai-radar --resource-group secai-radar-rg --sku Standard
```

Or run from repo root: `./scripts/upgrade-swa-to-standard.sh`

### Current status

- **secai-radar** (resource group `secai-radar-rg`): **Standard**  
- **Staging environments:** Enabled  
- **Custom domain:** secairadar.cloud  
- **Linked backends:** None yet — ready for Container Apps / API link

---

## Containers and local build status

| Container            | Dockerfile path                  | Built locally | Image tag (local)              | Role / use in Azure          |
|---------------------|-----------------------------------|---------------|---------------------------------|------------------------------|
| **Public API**      | `apps/public-api/Dockerfile`      | Yes           | `secai-radar-public-api:local`  | Container App (main read API)|
| **Registry API**    | `apps/registry-api/Dockerfile`    | Yes           | `secai-radar-registry-api:local`| Container App (private API)  |
| **Publisher**       | `apps/workers/publisher/Dockerfile` | Yes         | `secai-radar-publisher:local`   | Pipeline job / optional CA   |

**Workers without Dockerfiles (run via pipeline, not as linked backends):**  
Scout, Curator, Evidence Miner, Scorer, Drift Sentinel, Sage Meridian, Graph Builder. These are run by the daily GitHub Actions workflow (or similar) and are not “containers linked to SWA.”

---

## All containers built locally

As of the last check:

- **secai-radar-public-api:local** — built
- **secai-radar-registry-api:local** — built
- **secai-radar-publisher:local** — built

To rebuild everything:

```bash
./scripts/build-containers.sh
```

Or build individually:

```bash
# APIs (for Azure Container Apps)
docker build -t secai-radar-public-api:local apps/public-api
docker build -t secai-radar-registry-api:local apps/registry-api

# Publisher (for pipeline/optional deployment)
docker build -t secai-radar-publisher:local apps/workers/publisher
```

---

## Linking SWA to the Public API (Standard tier)

After the Public API is deployed as a Container App:

**Option A – Linked backends (Azure)**  
1. Azure Portal → Static Web App **secai-radar** → **Backends**.  
2. Add backend → choose the Public API Container App (or enter its URL, e.g. `https://secai-radar-public-api.<region>.azurecontainerapps.io`).  
3. Use the assigned backend path (e.g. `/api`) in app settings or in the frontend so requests go to that backend.

**Option B – Frontend env only (no SWA backend link)**  
1. Set build-time variable `VITE_API_BASE` to the Public API base URL, e.g. `https://<public-api-fqdn>/api`.  
2. In GitHub: repo → Settings → Secrets and variables → Actions → add/update `VITE_API_BASE`.  
3. The workflow builds the app with that value baked in; the SPA then calls the API on that origin.  
4. Ensure the API allows the SWA origin in CORS (public-api already allows `["*"]` for now).

**Suggested for quickest path:** Option B. Deploy public-api, put its URL in `VITE_API_BASE`, redeploy the SWA from the same branch.

---

## Next steps

1. ~~**Upgrade SWA to Standard**~~ Done for `secai-radar`.
2. Deploy or reuse infrastructure (e.g. ACR, Container Apps environment, existing DB).
3. Build and push the API images to ACR, then deploy **public-api** (and **registry-api** when needed).
4. Set `VITE_API_BASE` (or use SWA Linked backends) so the static app uses the correct API.
