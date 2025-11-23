#!/bin/bash
# Script to create Azure Cosmos DB account with Free Tier enabled
# Free Tier: 1,000 RU/s and 25 GB storage free for 12 months

COSMOS_ACCOUNT_NAME="secai-radar-cosmos"
RESOURCE_GROUP="secai-radar-rg"
LOCATION="eastus"
SUBSCRIPTION_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"

echo "Creating Cosmos DB account with Free Tier enabled..."
echo "Account: $COSMOS_ACCOUNT_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Check if account already exists
EXISTING=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  2>/dev/null)

if [ $? -eq 0 ]; then
    echo "Cosmos DB account already exists: $COSMOS_ACCOUNT_NAME"
    
    # Check if free tier is enabled
    FREE_TIER=$(az cosmosdb show \
      --name "$COSMOS_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "enableFreeTier" -o tsv)
    
    if [ "$FREE_TIER" == "true" ]; then
        echo "✅ Free Tier is ENABLED on this account"
        echo "   You get 1,000 RU/s and 25 GB storage free for 12 months"
    else
        echo "⚠️  Free Tier is NOT enabled on this account"
        echo "   To enable free tier, you must create a new account (free tier can only be set at creation)"
        echo "   Current account will use provisioned throughput pricing"
    fi
    
    # Get endpoint and key
    ENDPOINT=$(az cosmosdb show \
      --name "$COSMOS_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "documentEndpoint" -o tsv)
    
    KEY=$(az cosmosdb keys list \
      --name "$COSMOS_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "primaryMasterKey" -o tsv)
    
    echo ""
    echo "Connection Information:"
    echo "  Endpoint: $ENDPOINT"
    echo "  Key: $KEY (stored securely, set as COSMOS_KEY env var)"
    echo ""
    echo "Set these environment variables:"
    echo "  export COSMOS_ENDPOINT=\"$ENDPOINT\""
    echo "  export COSMOS_KEY=\"$KEY\""
    
else
    echo "Creating new Cosmos DB account with Free Tier..."
    
    # Create Cosmos DB account with Free Tier enabled
    az cosmosdb create \
      --name "$COSMOS_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --default-consistency-level "Session" \
      --locations regionName="$LOCATION" failoverPriority=0 \
      --enable-free-tier true \
      --subscription "$SUBSCRIPTION_ID"
    
    if [ $? -eq 0 ]; then
        echo "✅ Cosmos DB account created successfully with Free Tier enabled!"
        echo ""
        echo "Free Tier Benefits:"
        echo "  - 1,000 RU/s free (shared across all containers)"
        echo "  - 25 GB storage free"
        echo "  - Valid for 12 months from account creation"
        echo ""
        
        # Get endpoint and key
        ENDPOINT=$(az cosmosdb show \
          --name "$COSMOS_ACCOUNT_NAME" \
          --resource-group "$RESOURCE_GROUP" \
          --query "documentEndpoint" -o tsv)
        
        KEY=$(az cosmosdb keys list \
          --name "$COSMOS_ACCOUNT_NAME" \
          --resource-group "$RESOURCE_GROUP" \
          --query "primaryMasterKey" -o tsv)
        
        echo "Connection Information:"
        echo "  Endpoint: $ENDPOINT"
        echo "  Key: $KEY (stored securely, set as COSMOS_KEY env var)"
        echo ""
        echo "Set these environment variables:"
        echo "  export COSMOS_ENDPOINT=\"$ENDPOINT\""
        echo "  export COSMOS_KEY=\"$KEY\""
    else
        echo "❌ Failed to create Cosmos DB account"
        exit 1
    fi
fi

echo ""
echo "To view costs in Azure Portal:"
echo "  1. Go to: https://portal.azure.com"
echo "  2. Navigate to: Cost Management + Billing"
echo "  3. Select your subscription"
echo "  4. View 'Cost by resource' to see Cosmos DB costs"
echo ""
echo "Or use Azure CLI:"
echo "  az consumption usage list --start-date $(date -u -d '1 month ago' +%Y-%m-%d) --end-date $(date -u +%Y-%m-%d)"

