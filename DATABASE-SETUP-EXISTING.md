# Database Setup - Using Existing PostgreSQL Server

## Overview

We're using the existing PostgreSQL Flexible Server in `ctxeco-rg` instead of creating a new one.

**Existing Server:**
- **Resource Group:** `ctxeco-rg`
- **Server Name:** `ctxeco-db`
- **Azure Portal:** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview

## Setup Steps

### 1. Get Connection Details (2 minutes)

```bash
./scripts/get-postgres-connection.sh
```

This will show you:
- Server FQDN
- Admin username
- Connection string format

### 2. Configure Firewall (5 minutes)

Allow Azure services and your current IP:

```bash
./scripts/configure-postgres-firewall.sh
```

This will:
- Add rule to allow Azure services (0.0.0.0)
- Optionally add your current IP for local development

### 3. Create Database (2 minutes)

Create the `secairadar` database on the existing server:

```bash
./scripts/setup-existing-database.sh
```

Or manually:
```bash
az postgres flexible-server db create \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db \
  --database-name secairadar
```

### 4. Get Admin Password

You'll need the admin password. It may be stored in:
- Azure Key Vault
- Your password manager
- Azure Portal → PostgreSQL server → Reset password (if needed)

### 5. Set Environment Variable

```bash
export DATABASE_URL="postgresql://<admin-user>:<password>@<fqdn>:5432/secairadar"
```

### 6. Run Migrations (5 minutes)

```bash
cd apps/public-api
python scripts/migrate.py
```

### 7. Seed Sample Data (Optional)

```bash
python scripts/seed.py
```

## Connection String Format

```
postgresql://<username>:<password>@<fqdn>:5432/secairadar
```

Example:
```
postgresql://adminuser:MyPassword123@ctxeco-db.postgres.database.azure.com:5432/secairadar
```

## For Container Apps Deployment

When deploying to Azure Container Apps, set the `DATABASE_URL` as an environment variable:

```bash
az containerapp update \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --set-env-vars DATABASE_URL="postgresql://<user>:<pass>@<fqdn>:5432/secairadar"
```

Or store in Azure Key Vault and reference:
```bash
az containerapp update \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --set-env-vars DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://<kv-name>.vault.azure.net/secrets/database-url/)"
```

## Firewall Rules

The PostgreSQL server needs firewall rules to allow:
1. **Azure Services** - `0.0.0.0` to `0.0.0.0` (for Container Apps)
2. **Your Development IP** - Your current public IP (for local testing)
3. **Container Apps Outbound IPs** - If using VNet integration

## Troubleshooting

### Connection Refused
- Check firewall rules allow your IP or Azure services
- Verify server is running
- Check FQDN is correct

### Authentication Failed
- Verify username and password
- Check if password needs to be reset
- Ensure you're using the admin user

### Database Not Found
- Run `setup-existing-database.sh` to create the database
- Verify database name is `secairadar`

## Next Steps

After database setup:
1. ✅ Database created
2. ✅ Migrations run
3. ✅ Sample data seeded (optional)
4. → Deploy Public API (see `DEPLOYMENT-NEXT-STEPS.md`)
5. → Configure GitHub secrets with DATABASE_URL
