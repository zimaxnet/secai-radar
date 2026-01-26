# Fix status: have all fixes been applied?

## Code and docs (done)

| Repo | Status | What was pushed |
|------|--------|------------------|
| **secai-radar** | Pushed to `main` | `fix-all-db-credentials.sh`, `update-db-credentials-secai-ctxeco.sh`, `docs/DB-CREDENTIALS-FIX.md`, `docs/CREDENTIALS-SETUP.md` (credential-stores = .env, GH secrets, KV only). Earlier: assets exclude, Overview loading, deploy summary, GET-SECAI-WORKING. |
| **ctxEco** | Pushed to `main` | `scripts/fix-zep-db-auth.sh`, runbook updated to use it and state credentials only in .env, GH secrets, KV. |

Workspace-root files **DB-CREDENTIALS-FIX.md** and **INTEGRATED-WORKSPACE-DATABASE.md** live in the workspace folder (not in a git repo); **secai-radar/docs/DB-CREDENTIALS-FIX.md** is the versioned copy.

---

## Runtime / operations (you must do these)

For **all workloads** (ctxEco + secai-radar) to be fixed at runtime:

### 1. Run the credential fix script (once)

From **secai-radar**:

```bash
POSTGRES_PASSWORD='the-password-ctxeco-db-accepts' ./scripts/fix-all-db-credentials.sh
```

This updates **Key Vault** (ctxecokv + secai-radar-kv) and restarts **Zep**. ctxEco backend/worker and Zep then use the new credentials from KV.

### 2. Update GitHub DATABASE_URL and redeploy secai-radar

So the **public-api** gets the new credentials on the next deploy:

```bash
gh secret set DATABASE_URL --body "$(az keyvault secret show --vault-name secai-radar-kv --name database-url --query value -o tsv)"
```

Then run **Deploy to Staging** (or push to `main`) so the public-api is updated.

### 3. Verify

| Workload | Check |
|----------|--------|
| Zep | `az containerapp logs show -g ctxeco-rg -n ctxeco-zep --tail 30` — no "password authentication failed" |
| secai public-api | `curl -s https://<public-api-fqdn>/api/v1/public/health` |
| secai frontend | Open SWA URL, go to /mcp — no endless spinner; dashboard or explicit error + Retry |

---

## Summary

- **In repo:** All credential-related scripts and docs are committed and pushed in secai-radar and ctxEco.
- **In production:** You still need to run `fix-all-db-credentials.sh` with the real server password, update the GitHub `DATABASE_URL` secret from KV, and redeploy secai-radar so both workloads use the same, correct credentials.
