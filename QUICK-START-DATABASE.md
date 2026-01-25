# Quick Start: Database Setup

## PostgreSQL Server Details ✅

**Server:** `ctxeco-db` in `ctxeco-rg`
- **FQDN:** `ctxeco-db.postgres.database.azure.com`
- **Admin User:** `ctxecoadmin`
- **Version:** PostgreSQL 16
- **State:** Ready

## Quick Setup (5 minutes)

### Step 1: Create Database

```bash
az postgres flexible-server db create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --database-name secairadar
```

### Step 2: Configure Firewall

Allow Azure services (for Container Apps):

```bash
az postgres flexible-server firewall-rule create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

Allow your current IP (for local development):

```bash
./scripts/configure-postgres-firewall.sh
```

### Step 3: Get Connection String

You'll need the admin password. Connection string format:

```
postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar
```

### Step 4: Run Migrations

```bash
cd apps/public-api
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
python scripts/migrate.py
```

### Step 5: Seed Data (Optional)

```bash
python scripts/seed.py
```

## Using Scripts

All-in-one setup:

```bash
# 1. Get connection details
./scripts/get-postgres-connection.sh

# 2. Configure firewall
./scripts/configure-postgres-firewall.sh

# 3. Create database
./scripts/setup-existing-database.sh

# 4. Run migrations (after setting DATABASE_URL)
cd apps/public-api
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
python scripts/migrate.py
```

## Next Steps

After database setup:
1. ✅ Database created
2. ✅ Migrations run
3. → Deploy infrastructure (without PostgreSQL): `infra/mcp-infrastructure-existing-db.bicep`
4. → Deploy Public API Container App
5. → Update GitHub secrets with DATABASE_URL

See `DATABASE-SETUP-EXISTING.md` for detailed guide.
