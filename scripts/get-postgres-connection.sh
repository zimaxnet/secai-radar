#!/bin/bash
# Get PostgreSQL connection details from existing server

set -e

RESOURCE_GROUP="ctxeco-rg"
SERVER_NAME="ctxeco-db"
DATABASE_NAME="secairadar"  # Will be created if doesn't exist

echo "Getting PostgreSQL connection details..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Server Name: $SERVER_NAME"
echo ""

# Get server FQDN
FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query "fullyQualifiedDomainName" \
  --output tsv)

echo "Server FQDN: $FQDN"

# Get admin username
ADMIN_USER=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query "administratorLogin" \
  --output tsv)

echo "Admin User: $ADMIN_USER"
echo ""
echo "⚠️  You'll need to provide the admin password manually"
echo ""
echo "Connection string format:"
echo "postgresql://${ADMIN_USER}:<PASSWORD>@${FQDN}:5432/${DATABASE_NAME}"
echo ""
echo "To create the database, run:"
echo "az postgres flexible-server db create \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --server-name $SERVER_NAME \\"
echo "  --database-name $DATABASE_NAME"
echo ""
echo "To check firewall rules:"
echo "az postgres flexible-server firewall-rule list \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --name $SERVER_NAME"
echo ""
echo "To allow Azure services:"
echo "az postgres flexible-server firewall-rule create \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --name $SERVER_NAME \\"
echo "  --rule-name AllowAzureServices \\"
echo "  --start-ip-address 0.0.0.0 \\"
echo "  --end-ip-address 0.0.0.0"
