# DB credentials: when both ctxEco and secai-radar don’t work

**Shared server:** `ctxeco-db` (ctxeco-rg). Same admin user and password for both systems.

Use this when you’ve reset the server password (or something is wrong) and **both** ctxEco (Zep, backend, worker) and secai-radar (public-api) are failing with auth errors.

**Credential stores:** Credentials are stored **only** in **.env** (local), **GitHub secrets** (deploy/CI), and **Key Vault (KV)** (Azure runtime). The script updates KV and, when you run the extra command, GitHub secrets. Apps consume from KV (reference) or from deploy-time injection from GitHub secrets.

---

## One script, one run

From the **secai-radar** repo:

```bash
cd secai-radar
POSTGRES_PASSWORD='the-password-ctxeco-db-accepts' ./scripts/fix-all-db-credentials.sh
```

Replace `the-password-ctxeco-db-accepts` with the **actual** password for user **ctxecoadmin** on **ctxeco-db**.  
Or run `./scripts/fix-all-db-credentials.sh` and type the password when asked (hidden).

The script updates **Key Vault** only (no other stores):

1. **ctxecokv:** `postgres-password`, `zep-postgres-dsn`, `postgres-connection-string` (URL-encoded where needed)
2. **secai-radar-kv:** `database-url` for the secairadar DB
3. **Zep:** restarts with a new revision so it refetches the DSN from ctxecokv (reads from KV).

ctxEco apps (Zep, backend, worker) use KV; they pick up the new credentials after the script runs. The **secai-radar public-api** gets `DATABASE_URL` at deploy from the **GitHub** secret, so update that (see below) and redeploy for the public-api to use the new credentials.

---

## If you don’t know the password

1. Set it on the server (Portal or CLI):
   ```bash
   az postgres flexible-server update -g ctxeco-rg -n ctxeco-db --admin-password 'YourNewPassword'
   ```
2. Run the script with that value:
   ```bash
   POSTGRES_PASSWORD='YourNewPassword' ./scripts/fix-all-db-credentials.sh
   ```

---

## After the script: update GitHub secret (required for secai-radar public-api)

The public-api receives `DATABASE_URL` at deploy from the **GitHub** secret. Sync that from Key Vault so the next deploy uses the new credentials:

```bash
gh secret set DATABASE_URL --body "$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv)"
```

Run from the **secai-radar** repo (needs `gh` and read access to secai-radar-kv). Then run **Deploy to Staging** (or push to `main`) so the public-api is updated.

---

## Quick checks

| What | Command |
|------|--------|
| Zep logs (no more “password authentication failed”) | `az containerapp logs show -g ctxeco-rg -n ctxeco-zep --tail 30` |
| Public API health | `curl -s https://<public-api-fqdn>/api/v1/public/health` |
| Public API FQDN | `az containerapp show -n secai-radar-public-api -g secai-radar-rg --query 'properties.configuration.ingress.fqdn' -o tsv` |

---

## Why both were broken

- **ctxEco:** Zep and backend/worker read from **ctxecokv** (Key Vault). If those secrets don’t match the server, you see auth failures. The script updates KV and restarts Zep so it refetches the DSN from KV.
- **secai-radar:** The public-api gets `DATABASE_URL` at deploy from the **GitHub** secret. So credentials for it live in **GitHub secrets** (and we keep **secai-radar-kv** `database-url` in sync as the KV source of truth). Update the GitHub secret from KV, then redeploy.

Credentials stay only in **.env**, **GitHub secrets**, and **Key Vault**. For workspace-level detail see **INTEGRATED-WORKSPACE-DATABASE.md** (workspace root).
