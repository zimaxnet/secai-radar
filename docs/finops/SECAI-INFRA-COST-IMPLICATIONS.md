# SecAI Infrastructure – Cost Implications

> **Scope:** All infrastructure used by SecAI Radar (Verified MCP).  
> **Last updated:** 2026-01-23

This document summarizes **cost implications of every Azure resource** used by SecAI, with order-of-magnitude monthly estimates. Actuals depend on region (e.g. Central US), usage, and your agreement.

---

## Current Stack (Verified MCP)

| Resource | SKU / model | Purpose | Est. monthly cost |
|----------|-------------|---------|--------------------|
| **Azure Static Web Apps** | **Standard** | Public UI (secairadar.cloud); backend link / staging | **~$9** base + usage (e.g. bandwidth over included) |
| **Azure Container Apps** | Consumption | **secai-radar-public-api**, **secai-radar-registry-api** | **~$5–25** (see below) |
| **Image registry** | **GitHub Container Registry (ghcr.io)** or ACR Basic | Build/push public-api and registry-api; Container Apps pull from ghcr.io | **$0** (ghcr.io) or **~$5** (ACR Basic if you keep it) |
| **Log Analytics** | PerGB2018, 30-day retention | Container Apps env logs | **~$2–10** (ingestion ~$2–3/GB; low volume usually &lt;$10) |
| **Storage Account** | Standard_LRS | Blob: evidence-private, public-assets, exports-private | **~$1–5** (small data + transactions) |
| **Key Vault** | Standard | Secrets (e.g. DATABASE_URL reference); RBAC | **&lt;$1** (ops-based) |
| **Container Apps Environment** | (hosted by Apps) | Shared env for public-api + registry-api | Billed as part of app consumption above |
| **PostgreSQL** | **Existing** ctxeco-db (Flexible Server, ctxeco-rg) | secairadar DB; not created by SecAI Bicep | **$0** if fully allocated to ctxEco; otherwise allocate a **~$15–50** slice of the server if you charge back |

*Infra: `infra/mcp-infrastructure-existing-db.bicep` + `deploy-staging.yml`. Default deploy uses **ghcr.io** (no ACR). See [USING-GHCR-INSTEAD-OF-ACR.md](./USING-GHCR-INSTEAD-OF-ACR.md).*

---

## Container Apps (public-api + registry-api)

- **Free per month (per subscription):** 180,000 vCPU-seconds, 360,000 GiB-seconds, 2 million HTTP requests.
- **Beyond free:** ~\$0.000024/vCPU-second, ~\$0.000003/MB-second (memory), plus HTTP request charges.
- **Typical SecAI:** Two small apps, low–moderate traffic. With min replicas and some idle usage, expect **~\$5–25/month** total once past free tier. Scale-to-zero or very low traffic can keep it at **\$0** within the free grant.

---

## PostgreSQL (ctxeco-db)

- SecAI uses the **existing** PostgreSQL Flexible Server **ctxeco-db** in **ctxeco-rg**; it is **not** provisioned by SecAI Bicep.
- Cost is part of ctxEco’s bill. If you allocate a share to SecAI (e.g. by app or database), a rough slice for a small DB on a B_Standard_B1ms–type server is **~\$15–50/month** (region- and sizing-dependent). Otherwise treat as **\$0** for SecAI-specific reporting.

---

## Order-of-Magnitude Totals (monthly)

| Scenario | Approx total | Notes |
|----------|----------------|------|
| **SecAI-only (no Postgres allocation)** | **~\$17–50** | SWA ~\$9 + Container Apps ~\$5–25 + Log Analytics ~\$2–10 + Storage ~\$1–5 + KV &lt;\$1. Assumes **ghcr.io** (no ACR). |
| **With Postgres share** | **~\$35–100** | Add ~\$15–50 for allocated share of ctxeco-db |
| **Lowest (heavy free-tier use)** | **~\$12–18** | Container Apps and Log Analytics mostly within free/low usage; SWA + storage + KV dominate (ghcr.io \$0) |

---

## What drives cost

1. **Static Web Apps Standard** – Fixed ~\$9/mo once on Standard.
2. **Container Apps** – Variable; scales with vCPU/memory seconds and HTTP requests (min replicas and traffic matter).
3. **Image registry** – **\$0** with ghcr.io (default); or ~\$5/mo if you keep ACR Basic.
4. **Log Analytics** – Variable with log volume (Container Apps → Log Analytics).
5. **PostgreSQL** – Depends on allocation policy (shared vs SecAI chargeback).

---

## Reference

- **Deployment inventory:** [azure-deployment-inventory.md](./azure-deployment-inventory.md)  
- **Legacy (SWA Free + Functions + Storage + OpenAI):** [COST-ESTIMATION.md](./COST-ESTIMATION.md)  
- **Infra:** `secai-radar/infra/mcp-infrastructure-existing-db.bicep`, `.github/workflows/deploy-staging.yml`
