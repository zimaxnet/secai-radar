#!/bin/bash
# Configure PostgreSQL firewall to allow Azure services and Container Apps

set -e

RESOURCE_GROUP="ctxeco-rg"
SERVER_NAME="ctxeco-db"

echo "Configuring PostgreSQL firewall rules..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Server Name: $SERVER_NAME"
echo ""

# Allow Azure services (0.0.0.0)
echo "Adding rule to allow Azure services..."
az postgres flexible-server firewall-rule create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --rule-name "AllowAzureServices" \
  --start-ip-address "0.0.0.0" \
  --end-ip-address "0.0.0.0" \
  --output none 2>/dev/null || echo "Rule may already exist"

# Get current public IP (for local development)
CURRENT_IP=$(curl -s https://api.ipify.org)
echo ""
echo "Your current public IP: $CURRENT_IP"
read -p "Add firewall rule for your current IP? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Adding rule for current IP..."
  az postgres flexible-server firewall-rule create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$SERVER_NAME" \
    --rule-name "AllowCurrentIP" \
    --start-ip-address "$CURRENT_IP" \
    --end-ip-address "$CURRENT_IP" \
    --output none 2>/dev/null || echo "Rule may already exist"
  echo "✅ Firewall rule added"
fi

echo ""
echo "✅ Firewall configuration complete!"
echo ""
echo "Current firewall rules:"
az postgres flexible-server firewall-rule list \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --output table
