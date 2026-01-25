#!/bin/bash
# Quick database setup for existing PostgreSQL server

set -e

RESOURCE_GROUP="ctxeco-rg"
SERVER_NAME="ctxeco-db"
DATABASE_NAME="secairadar"

echo "🚀 Quick Database Setup"
echo "======================"
echo ""

# Check if database exists
echo "Checking if database exists..."
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

# Check firewall rule for Azure services
echo ""
echo "Checking firewall rules..."
AZURE_RULE=$(az postgres flexible-server firewall-rule show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --rule-name "AllowAzureServices" \
  --output tsv 2>/dev/null || echo "notfound")

if [ "$AZURE_RULE" = "notfound" ]; then
  echo "Adding firewall rule for Azure services..."
  az postgres flexible-server firewall-rule create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$SERVER_NAME" \
    --rule-name "AllowAzureServices" \
    --start-ip-address "0.0.0.0" \
    --end-ip-address "0.0.0.0"
  echo "✅ Firewall rule added"
else
  echo "✅ Firewall rule already exists"
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
echo "Connection Details:"
echo "  FQDN: $FQDN"
echo "  User: $ADMIN_USER"
echo "  Database: $DATABASE_NAME"
echo ""
echo "Next steps:"
echo "  1. Set DATABASE_URL environment variable:"
echo "     export DATABASE_URL=\"postgresql://${ADMIN_USER}:<PASSWORD>@${FQDN}:5432/${DATABASE_NAME}\""
echo ""
echo "  2. Run migrations:"
echo "     cd apps/public-api && python scripts/migrate.py"
echo ""
echo "  3. Seed data (optional):"
echo "     python scripts/seed.py"
