#!/bin/bash
# Setup database on existing PostgreSQL server

set -e

RESOURCE_GROUP="ctxeco-rg"
SERVER_NAME="ctxeco-db"
DATABASE_NAME="secairadar"

echo "Setting up database on existing PostgreSQL server..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Server Name: $SERVER_NAME"
echo "Database Name: $DATABASE_NAME"
echo ""

# Check if database exists
DB_EXISTS=$(az postgres flexible-server db show \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$SERVER_NAME" \
  --database-name "$DATABASE_NAME" \
  --output tsv 2>/dev/null || echo "notfound")

if [ "$DB_EXISTS" = "notfound" ]; then
  echo "Creating database: $DATABASE_NAME"
  az postgres flexible-server db create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$SERVER_NAME" \
    --database-name "$DATABASE_NAME"
  echo "✅ Database created"
else
  echo "✅ Database already exists"
fi

# Get connection details
FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query "fullyQualifiedDomainName" \
  --output tsv)

ADMIN_USER=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query "administratorLogin" \
  --output tsv)

echo ""
echo "✅ Database setup complete!"
echo ""
echo "Connection details:"
echo "  FQDN: $FQDN"
echo "  User: $ADMIN_USER"
echo "  Database: $DATABASE_NAME"
echo ""
echo "Next steps:"
echo "  1. Get the admin password from Azure Key Vault or your password manager"
echo "  2. Set DATABASE_URL environment variable:"
echo "     export DATABASE_URL=\"postgresql://${ADMIN_USER}:<PASSWORD>@${FQDN}:5432/${DATABASE_NAME}\""
echo "  3. Run migrations:"
echo "     cd apps/public-api && python scripts/migrate.py"
echo "  4. Seed data (optional):"
echo "     python scripts/seed.py"
