# Database Ready ✅

## Status

**Database successfully created on existing PostgreSQL server!**

- ✅ **Database:** `secairadar` created on `ctxeco-db`
- ✅ **Firewall:** Azure services already allowed
- ✅ **Server:** Ready (PostgreSQL 16)
- ✅ **Multi-Database:** Server hosts both `ctxeco` and `secairadar` databases (isolated)

**Note:** This server is shared with the ctxeco application. Each application uses its own database, providing complete data isolation while sharing server resources. See `DATABASE-SHARING-EXPLANATION.md` for details.

## Connection Details

```
FQDN: ctxeco-db.postgres.database.azure.com
User: ctxecoadmin
Database: secairadar
Port: 5432
```

## Next Steps

### 1. Get Admin Password

You'll need the admin password for `ctxecoadmin`. Check:
- Azure Key Vault
- Your password manager
- Or reset it in Azure Portal if needed

### 2. Set Environment Variable

```bash
export DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
```

### 3. Run Migrations

```bash
cd apps/public-api
python scripts/migrate.py
```

This will create all tables, indexes, and materialized views.

### 4. Seed Sample Data (Optional)

```bash
python scripts/seed.py
```

## For Container Apps

When deploying, set the DATABASE_URL as an environment variable:

```bash
az containerapp update \
  --name secai-radar-public-api \
  --resource-group secai-radar-rg \
  --set-env-vars DATABASE_URL="postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar"
```

Or store in Key Vault for security.

## Verification

Test connection:
```bash
psql "postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar" -c "\dt"
```

## Resources

- **Azure Portal:** https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/ctxeco-rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/ctxeco-db/overview
