# Database Authentication Inventory

## Current Status: Database Credentials Need Audit

Last Updated: January 30, 2026
Issue: Multiple services failing authentication to `ctxeco-db.postgres.database.azure.com`

---

## Services Requiring PostgreSQL Authentication

### 1. ✅ **Zep Memory Service** (ctxeco-zep Container)
- **Location**: Azure Container Apps / ctxeco-zep
- **Status**: ✅ FIXED (today)
- **Auth Method**: Config file with DSN
- **Credential Source**: Azure Key Vault (ctxecokv)
- **Key Vault Secrets Used**:
  - `postgres-password` → embedded in DSN string
  - `zep-config-yaml` → full config file with DSN
- **Config Path**: `/config/config.yaml` (mounted from secret)
- **DSN Format**: `postgresql://ctxecoadmin:PASSWORD@ctxeco-db.postgres.database.azure.com:5432/zep?sslmode=require`
- **Logs**: ✅ Connected successfully, pgvector initialized

### 2. ❌ **GitHub Actions Pipeline** (daily-pipeline.yml)
- **Location**: `.github/workflows/daily-pipeline.yml`
- **Status**: ❌ FAILING (just now)
- **Auth Method**: Environment variable `DATABASE_URL` from GitHub secret
- **Credential Source**: GitHub Secrets (repository settings)
- **Error**: `FATAL: password authentication failed for user "ctxecoadmin"`
- **Affected Script**: `apps/public-api/scripts/record_pipeline_run.py`
- **Problem**: GitHub secret likely outdated or uses wrong password/database

### 3. ❓ **Public API Backend** (apps/public-api)
- **Location**: Azure Static Web Apps + Azure Functions
- **Status**: Unknown - need to verify
- **Auth Method**: Likely environment variable or config file
- **Credential Source**: Needs investigation
- **Relevant Files**:
  - `apps/public-api/.env.production` (if exists)
  - `apps/public-api/config/` (if exists)
  - Azure Functions environment variables

### 4. ❓ **SecAI Radar Backend** (apps/backend or api)
- **Location**: TBD - need to locate
- **Status**: Unknown - need to verify
- **Auth Method**: TBD
- **Credential Source**: TBD

### 5. ❓ **Other Services**
- Additional backends/workers not yet identified

---

## Key Vault Credentials Status

### ctxecokv (Primary - ctxEco project)
```
Available Secrets:
✅ postgres-password (used by Zep)
✅ postgres-connection-string (may be outdated)
✅ zep-postgres-dsn
✅ zep-config-yaml (full config file)
⚠️  DATABASE_URL (does NOT exist - GitHub Actions is using outdated value?)
```

### secai-radar-kv (Secondary - SecAI Radar project)
```
Status: Unknown - need to check what secrets exist
```

---

## GitHub Actions Secrets Status

### Current Secrets Defined:
Need to check repository settings at:
https://github.com/zimaxnet/secai-radar/settings/secrets/actions

**Issues Found**:
- ❌ DATABASE_URL is likely set to an old/incorrect password
- ❌ No consistent credential rotation mechanism

---

## The Problem

**Different credential values across services:**

1. **Zep (Container)**: Using password from `postgres-password` key vault secret
2. **GitHub Actions**: Using DATABASE_URL GitHub secret (value unknown)
3. **Public API**: Unknown (probably hardcoded or using old secret)
4. **Other services**: Unknown

**When password rotates**, only one place was updated → cascading failures.

---

## Required Actions

### IMMEDIATE (Next steps)
- [ ] Check GitHub Actions `DATABASE_URL` secret value
- [ ] Compare with actual `postgres-password` from Key Vault
- [ ] Update if mismatch found
- [ ] Audit all .env files for hardcoded credentials

### SHORT-TERM (Today)
- [ ] Locate all authentication code in backend/public-api
- [ ] Document exact credential requirements for each service
- [ ] Create unified secret rotation procedure

### LONG-TERM (This week)
- [ ] Implement Azure Managed Identity for container-to-database auth (eliminates password management)
- [ ] Remove hardcoded credentials from environment variables
- [ ] Centralize credential management with automated rotation

---

## Next Diagnostic Steps

1. Check current GitHub Actions DATABASE_URL:
   ```bash
   # Currently: Cannot view directly (encrypted)
   # Need to check via: GitHub repo settings → Secrets
   ```

2. Get current Key Vault password:
   ```bash
   az keyvault secret show --vault-name ctxecokv --name postgres-password --query value -o tsv
   ```

3. Test authentication with both values:
   ```bash
   psql "postgresql://ctxecoadmin:PASSWORD@ctxeco-db.postgres.database.azure.com:5432/zep?sslmode=require"
   ```

4. Locate all database connection code:
   ```bash
   grep -r "DATABASE_URL\|psycopg2\|postgres" --include="*.py" apps/
   grep -r "password\|credentials" --include="*.env*" .
   ```

---

## Files to Review

- [ ] `apps/public-api/scripts/record_pipeline_run.py` (currently failing)
- [ ] `apps/public-api/.env.production` (if exists)
- [ ] `apps/public-api/app.py` or equivalent (database initialization)
- [ ] `.github/workflows/daily-pipeline.yml` (just fixed YAML, but DATABASE_URL secret wrong)
- [ ] `apps/backend/` (if separate backend exists)
- [ ] Any `docker-compose.yml` with credentials
- [ ] Terraform/infrastructure code that sets secrets

---

## Decision Point

**Option A: Quick Fix (Today)**
- Update GitHub Actions DATABASE_URL secret
- Create matching secret in any other locations
- Document in this file what was done

**Option B: Proper Fix (This week)**
- Implement Azure Managed Identity
- Remove all password-based auth
- Use Key Vault references where possible

**Recommendation**: Do Option A today to get pipeline working, then schedule Option B for proper solution.
