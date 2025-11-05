# SecAI Radar — Dev & Deploy Checklist (Cursor-Ready)

This single file captures the exact steps to finish deployment, wire auth, and start building the web UI in **Cursor**. Drop it into `docs/` and pin it in your Context.

---

## 0) Prereqs

- **Local tools:** Python 3.10+, Node 18+, Azure Functions Core Tools v4, Docker (for Azurite) or Azurite npm, Git.
- **Azure:** Resource Group, Storage Account, Static Web App (SWA), DNS CNAME (✅ you created these).
- **Repo:** `secai-radar` with `/api` (Functions Python) and `/web` (Vite React).

---

## 1) Flip Functions to anonymous (SWA enforces auth)

SWA is the front gate (Entra ID). Each Functions HTTP trigger should allow anonymous so SWA can call it.

Update these files:  
`api/**/function.json` → set:

```json
"authLevel": "anonymous"
```

Files to change:
- `api/domains/function.json`
- `api/tools/function.json`
- `api/controls/function.json`
- `api/summary/function.json`
- `api/gaps/function.json`
- `api/tenant_tools/function.json`
- `api/import_controls/function.json`

Commit & push to `main` to redeploy.

---

## 2) SWA routing & auth config

Create `web/staticwebapp.config.json`:

```json
{
  "auth": { "rolesSource": "roles" },
  "routes": [
    { "route": "/", "serve": "/index.html" },
    { "route": "/tenant/*", "allowedRoles": ["authenticated"] },
    { "route": "/api/*", "allowedRoles": ["authenticated"] }
  ],
  "navigationFallback": { "rewrite": "/index.html" }
}
```

This puts both UI and API behind Entra ID once the provider is configured.

---

## 3) Entra ID (Azure AD) in SWA

Azure Portal → Static Web App → **Authentication**:
1. **Add identity provider** → Microsoft (Entra ID).
2. Create/Select an app registration.
3. Callback URL must match your domain:
   - `https://secai-radar.zimax.net/.auth/login/aad/callback`
4. Save.

**Tip:** If custom domain isn’t ready, you can start using the default SWA URL callback and change later.

---

## 4) DNS & SSL quick verify

- Propagation:
  ```
  dig secai-radar.zimax.net CNAME +short
  ```
  Expect: `purple-moss-0942f9e10.3.azurestaticapps.net`

- In SWA → **Custom domains**:
  - Status: **Validated**
  - SSL: **Issued**

---

## 5) Environment settings (already set ✅)

In SWA → **Environment variables** (API):
- `AzureWebJobsStorage` = (storage conn string)
- `TABLES_CONN` = (storage conn string)
- `BLOBS_CONN` = (storage conn string)
- `BLOB_CONTAINER` = `assessments`
- `TENANT_ID` = `NICO`

> Later: move to **Managed Identity** + RBAC.

---

## 6) Smoke test the live API (after deploy)

Open in browser (signed-in):
- `https://secai-radar.zimax.net/api/domains`
- `https://secai-radar.zimax.net/api/tools/catalog`

Add a tool (Wiz CSPM):
```bash
curl -X POST "https://secai-radar.zimax.net/api/tenant/NICO/tools"   -H "Content-Type: application/json"   --data '{"vendorToolId":"wiz-cspm","Enabled":true,"ConfigScore":0.8}'
```

Import a tiny controls CSV (create `sample.csv` with the headers from the brief):
```bash
curl -X POST "https://secai-radar.zimax.net/api/tenant/NICO/import"   -H "Content-Type: text/csv"   --data-binary @sample.csv
```

Check aggregates:
- `https://secai-radar.zimax.net/api/tenant/NICO/summary`
- `https://secai-radar.zimax.net/api/tenant/NICO/gaps`

---

## 7) Local dev in Cursor

### 7.1 API (Functions)
```bash
# Start Azurite (storage emulator)
docker run -p 10000-10002:10000-10002 mcr.microsoft.com/azure-storage/azurite

cd secai-radar/api
python -m venv .venv
# Win: .venv\Scripts\activate   mac/linux: source .venv/bin/activate
pip install -r requirements.txt
func start
```

### 7.2 Web (Vite + React)
If `web/` is not yet scaffolded:
```bash
cd ../web
npm create vite@latest . -- --template react-ts
npm i @tanstack/react-table recharts zod react-hook-form @hookform/resolvers
npm i -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Create `web/.env` for local dev:
```
VITE_API_BASE=http://localhost:7071/api
VITE_DEFAULT_TENANT=NICO
```

Minimal API client `src/lib/api.ts`:
```ts
const API = import.meta.env.VITE_API_BASE;
const TENANT = import.meta.env.VITE_DEFAULT_TENANT || "NICO";

export const getDomains = () => fetch(`${API}/domains`).then(r=>r.json());
export const getSummary = (tenant=TENANT) => fetch(`${API}/tenant/${tenant}/summary`).then(r=>r.json());
export const getControls = (tenant=TENANT, p: {domain?:string;status?:string;q?:string} = {}) => {
  const qs = new URLSearchParams(p as any).toString();
  return fetch(`${API}/tenant/${tenant}/controls${qs?`?${qs}`:""}`).then(r=>r.json());
};
export const getGaps = (tenant=TENANT) => fetch(`${API}/tenant/${tenant}/gaps`).then(r=>r.json());
export const importControls = (tenant=TENANT, csv:string) =>
  fetch(`${API}/tenant/${tenant}/import`, { method:"POST", headers:{"Content-Type":"text/csv"}, body: csv }).then(r=>r.json());
export const postTools = (tenant=TENANT, body:any) =>
  fetch(`${API}/tenant/${tenant}/tools`, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)}).then(r=>r.json());
```

Run:
```bash
npm run dev
```

---

## 8) First four pages to build

1. **/tenant/:id/dashboard**  
   - `GET /summary` → tiles + Recharts radar chart per domain
2. **/tenant/:id/controls**  
   - `GET /controls` table with domain/status filters  
   - CSV import (textarea or file) → `POST /import`
3. **/tenant/:id/tools**  
   - `GET/POST /tools` → enable tools + `ConfigScore` sliders
4. **/tenant/:id/gaps**  
   - `GET /gaps` → list coverage %, Hard/Soft gaps, capabilities, suggestions

**Tip:** Keep `docs/` brief + ADRs pinned in Cursor context. Use your Cursor rules to ensure all docs land under `docs/`.

---

## 9) Troubleshooting quick hits

- **401/403 on API:** ensure triggers use `"authLevel":"anonymous"` and SWA auth is enabled.
- **Empty data:** add at least one tool (**TenantTools**) and import a small CSV into **Controls**.
- **CORS locally:** use `VITE_API_BASE=http://localhost:7071/api`.
- **Custom domain not secure:** SSL issuance can trail validation; recheck SWA → Custom domains.
- **Function errors:** check SWA Functions logs; validate `requirements.txt` installed.

---

## 10) Short backlog (after MVP)

- Control detail view (capability breakdown + “why”)
- Evidence upload (Blob SAS) + review flags
- Catalog editor for tool strengths & control requirements
- RBAC per tenant; audit history of edits

---

## 11) References

- **Brief:** `docs/SEC_AI_Radar_Brief.md`
- **ADRs:** `docs/adr/0001-0005` (architecture, auth, consolidation, scoring, evidence)

---

**You’re ready:** push the `authLevel` change, add SWA config, finalize Entra ID in the portal, then smoke test `/api` endpoints and start building the 4 pages in Cursor.
