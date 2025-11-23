#!/bin/bash
# Script to check Cosmos DB costs and usage
# Requires Azure CLI and appropriate permissions

COSMOS_ACCOUNT_NAME="secai-radar-cosmos"
RESOURCE_GROUP="secai-radar-rg"
SUBSCRIPTION_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"

echo "=== Cosmos DB Cost and Usage Report ==="
echo ""

# Check if account exists
EXISTING=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Cosmos DB account not found: $COSMOS_ACCOUNT_NAME"
    echo "   Run create-cosmos-db.sh to create it"
    exit 1
fi

echo "Account: $COSMOS_ACCOUNT_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo ""

# Check Free Tier status
FREE_TIER=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "enableFreeTier" -o tsv)

if [ "$FREE_TIER" == "true" ]; then
    echo "✅ Free Tier: ENABLED"
    echo "   - 1,000 RU/s free"
    echo "   - 25 GB storage free"
    echo "   - Valid for 12 months from account creation"
else
    echo "⚠️  Free Tier: NOT ENABLED"
    echo "   Account is using provisioned throughput pricing"
fi

echo ""

# Get account creation date to calculate free tier expiration
CREATED_TIME=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "systemData.createdAt" -o tsv)

if [ -n "$CREATED_TIME" ]; then
    echo "Account Created: $CREATED_TIME"
    if [ "$FREE_TIER" == "true" ]; then
        # Calculate expiration (12 months from creation)
        EXPIRY_DATE=$(date -u -d "$CREATED_TIME + 12 months" +%Y-%m-%d 2>/dev/null || date -u -v+12m -j -f "%Y-%m-%dT%H:%M:%S" "$CREATED_TIME" +%Y-%m-%d 2>/dev/null || echo "Unknown")
        echo "Free Tier Expires: $EXPIRY_DATE"
    fi
fi

echo ""

# Get current throughput configuration
echo "=== Throughput Configuration ==="
DATABASES=$(az cosmosdb sql database list \
  --account-name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "[].{name:id}" -o tsv)

for DB in $DATABASES; do
    echo "Database: $DB"
    CONTAINERS=$(az cosmosdb sql container list \
      --account-name "$COSMOS_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --database-name "$DB" \
      --query "[].{name:id}" -o tsv)
    
    for CONTAINER in $CONTAINERS; do
        THROUGHPUT=$(az cosmosdb sql container throughput show \
          --account-name "$COSMOS_ACCOUNT_NAME" \
          --resource-group "$RESOURCE_GROUP" \
          --database-name "$DB" \
          --name "$CONTAINER" \
          --query "resource.throughput" -o tsv 2>/dev/null)
        
        if [ -n "$THROUGHPUT" ] && [ "$THROUGHPUT" != "null" ]; then
            echo "  Container: $CONTAINER - Throughput: $THROUGHPUT RU/s"
        else
            echo "  Container: $CONTAINER - Throughput: Using Free Tier (shared 1,000 RU/s)"
        fi
    done
done

echo ""

# Get storage usage
echo "=== Storage Usage ==="
STORAGE=$(az cosmosdb show \
  --name "$COSMOS_ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "systemData" -o json 2>/dev/null)

echo "Note: Detailed storage metrics available in Azure Portal"
echo "      Navigate to: Cosmos DB Account > Metrics > Data + Index Size"

echo ""

# Cost estimation
echo "=== Cost Estimation ==="
if [ "$FREE_TIER" == "true" ]; then
    echo "Current Cost: \$0/month (Free Tier active)"
    echo ""
    echo "Free Tier Limits:"
    echo "  - Throughput: Up to 1,000 RU/s across all containers"
    echo "  - Storage: Up to 25 GB"
    echo ""
    echo "⚠️  If you exceed these limits, you'll be charged:"
    echo "  - Additional RU/s: ~\$0.008/hour per 100 RU/s"
    echo "  - Additional Storage: \$0.25/GB/month"
else
    echo "⚠️  Free Tier not enabled - using provisioned pricing"
    echo "  Estimated cost: ~\$23-230/month depending on throughput"
fi

echo ""

# Azure Cost Management links
echo "=== View Detailed Costs ==="
echo "Azure Portal:"
echo "  https://portal.azure.com/#@/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DocumentDB/databaseAccounts/$COSMOS_ACCOUNT_NAME/costAnalysis"
echo ""
echo "Cost Management:"
echo "  https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/costanalysis"
echo ""
echo "To get current month costs via CLI:"
echo "  az consumption usage list \\"
echo "    --start-date \$(date -u -d 'first day of this month' +%Y-%m-%d) \\"
echo "    --end-date \$(date -u +%Y-%m-%d) \\"
echo "    --query \"[?instanceName=='$COSMOS_ACCOUNT_NAME']\""

