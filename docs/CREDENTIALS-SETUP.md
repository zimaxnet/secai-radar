# Credentials setup: Key Vault, GitHub secrets, env vars

**Credential stores:** Credentials may be stored **only** in **.env** (local), **GitHub secrets** (deploy/CI), and **Key Vault (KV)** (Azure runtime). Apps consume from KV (reference) or from deploy-time injection from GitHub secrets.

Single place for securing **PostgreSQL** and **deployment** credentials for secai-radar (ctxeco-db, SWA, daily pipeline).  
For the **integrated workspace** (secai-radar + ctxEco sharing one server), **INTEGRATED-WORKSPACE-DATABASE.md** at the workspace root is the canonical reference.

---

## Key Vaults and managed identity (RBAC)

- **ctxecokv** (in `ctxeco-rg`): **ctxEco** app Key Vault. Contains `postgres-password` (ctxeco-db server admin / ctxecoadmin password), plus `zep-api-key`, `azure-ai-key`, `anthropic-api-key`, `voicelive-api-key`, Foundry secrets, etc. To build the admin connection string for secai-radar or to run `create-secairadar-db-user.py`, you can use:
  ```bash
  export ADMIN_DATABASE_URL="postgresql://ctxecoadmin:$(az keyvault secret show --vault-name ctxecokv --name postgres-password --query value -o tsv)@ctxeco-db.postgres.database.azure.com:5432/secairadar?sslmode=require"
  ```
  (Requires read access to ctxecokv. Azure Flexible Server requires SSL.)
- **secai-radar-kv** (in `secai-radar-rg`): Uses **RBAC**. A user-assigned managed identity **secairadarkvidentity** has **Key Vault Secrets Officer** so it can get/set secrets. Use this identity for Container Apps, automation, or Azure services that need vault access. The signed-in user can be granted **read** access via `./scripts/grant-kv-read-access.sh` (Key Vault Secrets User).
- **secai-radar-dev-kv**: Created by `infra/mcp-infrastructure-existing-db.bicep`; the same template creates a managed identity and RBAC for that vault when (re)deployed.

To (re)apply RBAC and create the managed identity for a vault:

```bash
KEY_VAULT_NAME=secai-radar-kv RESOURCE_GROUP=secai-radar-rg ./scripts/setup-keyvault-rbac.sh
```

To grant the **currently signed-in user** read access to secrets (e.g. for `run-migrations.sh` or `az keyvault secret show`):

```bash
KEY_VAULT_NAME=secai-radar-kv RESOURCE_GROUP=secai-radar-rg ./scripts/grant-kv-read-access.sh
```

Override `KEY_VAULT_NAME` for other vaults (e.g. `secai-radar-dev-kv`). See `scripts/setup-keyvault-rbac.sh` and `scripts/grant-kv-read-access.sh`.

---

## 1. PostgreSQL (ctxeco-db)

**Server:** `ctxeco-db` in resource group `ctxeco-rg`  
**Portal:** [ctxeco-db overview](https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview)

- **Database:** `secairadar`
- **Admin user:** `ctxecoadmin`
- **FQDN:** `ctxeco-db.postgres.database.azure.com`

**Get or reset password:**

- **ctxEco Key Vault:** `ctxecokv` (in `ctxeco-rg`) has secret **postgres-password** — that is the ctxeco-db server admin (ctxecoadmin) password. If you have read access: `az keyvault secret show --vault-name ctxecokv --name postgres-password --query value -o tsv`
- Azure Portal → ctxeco-db → **Settings** → **Reset password**, or use existing admin password from your secrets store.

**Update both ctxEco and secai-radar after a password reset:**  
From secai-radar repo: `./scripts/update-db-credentials-secai-ctxeco.sh` (prompts for password) or `POSTGRES_PASSWORD='...' ./scripts/update-db-credentials-secai-ctxeco.sh`. This writes to **ctxecokv** (postgres-password, zep-postgres-dsn) and **secai-radar-kv** (database-url), then restarts Zep. See workspace **INTEGRATED-WORKSPACE-DATABASE.md**.

**Connection string format:**

```text
postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar?sslmode=require
```
(Azure Flexible Server requires SSL.)

**Dedicated app user (recommended):** Use a separate PostgreSQL user for secai-radar instead of the server admin. Same pattern as ctxEco (see `ctxEco/.env`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.). Create user `secairadar_app` once, then use it everywhere:

1. **One-time:** Connect as `ctxecoadmin` and create the app user:

   ```bash
   # Admin URL (ctxecoadmin password from portal or env)
   export ADMIN_DATABASE_URL="postgresql://ctxecoadmin:<ADMIN_PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
   # Optional: set a password; if unset, one is generated and printed
   # export SECAIRADAR_APP_PASSWORD="your-secure-password"
   ./scripts/run-create-secairadar-user.sh
   ```
   Or run `python3 scripts/create-secairadar-db-user.py` directly if psycopg2 is installed.

   The script prints a connection string for `secairadar_app`. Copy it.

2. **Store that string** in Key Vault as `database-url` (see section 2), and use it as `DATABASE_URL` for migrations, apps, and GitHub secrets.

3. **Local env:** Use the same `POSTGRES_*` layout as ctxEco. See `.env.example`: `POSTGRES_USER=secairadar_app`, `POSTGRES_PASSWORD=...`, `POSTGRES_DB=secairadar`.

---

## 2. Store in Azure Key Vault

**Store the secret in secai-radar-kv (recommended):**

1. **Get the Postgres password** from Azure Portal:  
   [ctxeco-db overview](https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview) → **Settings** → **Reset password** (or use your existing admin password).

2. **Store `database-url` in Key Vault** (from repo root):

   - **If you use the dedicated app user** (after `create-secairadar-db-user.py`): set `DATABASE_URL` to the printed connection string, then run  
     `KEY_VAULT_NAME=secai-radar-kv ./scripts/update-credentials.sh` (it will use `DATABASE_URL` from the environment).
   - **If you use ctxecoadmin:** run  
     `KEY_VAULT_NAME=secai-radar-kv ./scripts/update-credentials.sh`  
     and when prompted, enter the PostgreSQL password for `ctxecoadmin`. The script writes the full connection string to secret `database-url` in **secai-radar-kv**.

3. **Read access:** If you need to read secrets (e.g. for `run-migrations.sh` or `az keyvault secret show`), grant yourself Key Vault Secrets User:

   ```bash
   KEY_VAULT_NAME=secai-radar-kv RESOURCE_GROUP=secai-radar-rg ./scripts/grant-kv-read-access.sh
   ```

**Other options:**

- **Prompted to secai-radar-dev-kv:** run `./scripts/update-credentials.sh` (default vault is secai-radar-dev-kv).
- **From env:**  
  `export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"`  
  then `KEY_VAULT_NAME=secai-radar-kv ./scripts/update-credentials.sh`.

**Overrides:**

- `KEY_VAULT_NAME` – default `secai-radar-dev-kv`. Use `secai-radar-kv` to store in the RBAC vault with managed identity **secairadarkvidentity**.
- `RESOURCE_GROUP` – default `secai-radar-rg`

**Access:** For **secai-radar-kv**, the managed identity has Secrets Officer; your user can get read access via `grant-kv-read-access.sh`. For other vaults, ensure your user or identity has the right role via IAM.

---

## 3. GitHub Actions secrets

In the repo: **Settings → Secrets and variables → Actions**, add:

| Secret | Used by | How to get / set |
|--------|---------|-------------------|
| **DATABASE_URL** | `daily-pipeline.yml` (workers), migrations, any job that needs DB | Same value as Key Vault `database-url`. One-liner below. |
| **AZURE_STATIC_WEB_APPS_API_TOKEN** | `azure-static-web-apps.yml` (SWA deploy) | Azure Portal → Static Web App **secai-radar** → **Manage deployment token** |
| **VITE_API_BASE** | `azure-static-web-apps.yml` (build-time env for frontend) | Optional. e.g. `https://<public-api-fqdn>/api` when using Container App. Default in workflow: `https://secai-radar-api.azurewebsites.net/api` |
| **AZURE_CREDENTIALS** | `deploy-infrastructure.yml`, `deploy-staging.yml` | JSON for Azure service principal: `{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"..."}`. See [Azure/login docs](https://github.com/Azure/login#configure-deployment-credentials). |

**Set DATABASE_URL from Key Vault (after storing `database-url` in KV):**

```bash
gh secret set DATABASE_URL --body "$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv)"
```
Use `secai-radar-dev-kv` if you stored the secret there instead.

**Or set manually:**

```bash
gh secret set DATABASE_URL
# paste the connection string when prompted
```

---

## 4. Local / environment variables

For **migrations**, **seeding**, and **local API/workers** you need `DATABASE_URL` in the environment.

**Option A – export (current shell):**

```bash
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
./scripts/run-migrations.sh
```

**Option B – copy from Key Vault (requires read access, e.g. after `grant-kv-read-access.sh`):**

```bash
export DATABASE_URL="$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv)"
./scripts/run-migrations.sh
```
Or run `./scripts/run-migrations.sh` alone; it will try to load `database-url` from **secai-radar-kv** when `DATABASE_URL` is unset.

**Option C – `.env` (do not commit):**

Create `secai-radar/.env` or project-specific `.env` with:

```bash
DATABASE_URL=postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar
```

Load it before running scripts (e.g. `set -a && source .env && set +a` or use a tool that loads `.env`). Prefer Key Vault or a local secrets manager over committing `.env`.

See **`.env.example`** in the repo for a template (no real values).

---

## 5. Container App (Public API)

When deploying the Public API as a Container App, set `DATABASE_URL` via:

- **Key Vault reference** (recommended): add a secret in the Container App that references the Key Vault secret, or use `--env-vars "DATABASE_URL=secretref:database-url"` and configure the secret from Key Vault.
- **Literal:** only for short-lived dev; avoid in production.

---

## Quick checklist

- [ ] Postgres password obtained (or reset) from [ctxeco-db](https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview)
- [ ] `KEY_VAULT_NAME=secai-radar-kv ./scripts/update-credentials.sh` run → `database-url` in **secai-radar-kv**
- [ ] Read access: `./scripts/grant-kv-read-access.sh` (for secai-radar-kv) if you need to read secrets locally or in migrations
- [ ] GitHub secrets set: **DATABASE_URL**, **AZURE_STATIC_WEB_APPS_API_TOKEN** (and **VITE_API_BASE** / **AZURE_CREDENTIALS** if used)
- [ ] Local usage: `DATABASE_URL` exported or in `.env` for migrations/seed; or pulled from Key Vault when needed
