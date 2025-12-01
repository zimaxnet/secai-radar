#!/bin/bash
# Quick cost monitoring script for SecAI Radar infrastructure
# Run this regularly to track spending

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-secai-radar-dev-rg}"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

# Get date range for current month
if [[ "$OSTYPE" == "darwin"* ]]; then
    MONTH_START=$(date -v1d +%Y-%m-%d)
    MONTH_END=$(date -v1d -v+1m -v-1d +%Y-%m-%d)
else
    MONTH_START=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d)
    MONTH_END=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%Y-%m-%d)
fi
TODAY=$(date +%Y-%m-%d)

echo "=========================================="
echo "SecAI Radar - Cost Monitoring Report"
echo "=========================================="
echo ""
echo "Subscription: $SUBSCRIPTION_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Period: $MONTH_START to $TODAY"
echo ""
echo "=========================================="
echo ""

# Check if Cost Management API is accessible
echo "=== Current Month Costs ==="
COST_QUERY=$(az consumption usage list \
    --start-date "$MONTH_START" \
    --end-date "$TODAY" \
    --query "[?contains(instanceName, 'secai-radar') || contains(instanceName, 'secai')]" \
    -o json 2>/dev/null || echo "[]")

if [ "$COST_QUERY" == "[]" ] || [ -z "$COST_QUERY" ]; then
    echo -e "${YELLOW}⚠️  Cost data not available via CLI${NC}"
    echo ""
    echo "This may be because:"
    echo "  1. Cost Management Reader role is not assigned"
    echo "  2. Costs haven't been calculated yet (can take 24-48 hours)"
    echo "  3. No resources have incurred costs this month"
    echo ""
    echo "View costs in Azure Portal:"
    echo "  https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/costanalysis"
    echo ""
    echo "Or set up a budget alert:"
    echo "  https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/Budgets"
else
    # Try to calculate total (requires jq)
    if command -v jq &> /dev/null; then
        TOTAL_COST=$(echo "$COST_QUERY" | jq -r '[.[] | .pretaxCost | tonumber] | add' 2>/dev/null || echo "0")
        if [ "$TOTAL_COST" != "0" ] && [ -n "$TOTAL_COST" ]; then
            echo -e "${GREEN}Total Cost (MTD): \$${TOTAL_COST}${NC}"
            echo ""
            
            # Breakdown by resource
            echo "Cost Breakdown:"
            echo "$COST_QUERY" | jq -r '.[] | "\(.instanceName): $\(.pretaxCost)"' | sort
        else
            echo -e "${BLUE}No costs recorded yet this month${NC}"
        fi
    else
        echo -e "${BLUE}Cost data available (install 'jq' for detailed breakdown)${NC}"
        echo ""
        echo "Install jq:"
        echo "  macOS: brew install jq"
        echo "  Linux: sudo apt-get install jq"
    fi
fi

echo ""
echo "=========================================="
echo "Resource-Specific Cost Estimates"
echo "=========================================="
echo ""

# Function App Plan costs
FUNCTION_PLAN=$(az functionapp plan list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")
if [ -n "$FUNCTION_PLAN" ]; then
    SKU=$(az functionapp plan show --name "$FUNCTION_PLAN" --resource-group "$RESOURCE_GROUP" --query "sku.name" -o tsv 2>/dev/null || echo "Unknown")
    PRE_WARMED=$(az functionapp plan show --name "$FUNCTION_PLAN" --resource-group "$RESOURCE_GROUP" --query "sku.preWarmedInstanceCount" -o tsv 2>/dev/null || echo "0")
    
    echo "Function Plan ($SKU):"
    case $SKU in
        "EP1")
            if [ "$PRE_WARMED" == "0" ]; then
                echo "  Estimated: ~\$50-100/month (pay-per-use, no pre-warmed)"
            else
                echo "  Estimated: ~\$146/month (base + usage)"
            fi
            ;;
        "EP2")
            echo "  Estimated: ~\$292/month (base + usage)"
            ;;
        "EP3")
            echo "  Estimated: ~\$584/month (base + usage)"
            ;;
        *)
            echo "  Check Azure pricing calculator for $SKU"
            ;;
    esac
    echo "  Pre-warmed instances: $PRE_WARMED"
fi

# Storage Account
STORAGE_ACCOUNT=$(az storage account list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")
if [ -n "$STORAGE_ACCOUNT" ]; then
    SKU=$(az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --query "sku.name" -o tsv 2>/dev/null || echo "Unknown")
    echo ""
    echo "Storage Account ($SKU):"
    echo "  Estimated: ~\$0.92/month per 50GB (first 50GB free)"
    echo "  Transactions: ~\$0.004 per 10,000 operations"
fi

# Application Insights
APP_INSIGHTS=$(az monitor app-insights component list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")
if [ -n "$APP_INSIGHTS" ]; then
    DAILY_CAP=$(az monitor app-insights component show --app "$APP_INSIGHTS" --resource-group "$RESOURCE_GROUP" --query "properties.DailyQuota" -o tsv 2>/dev/null || echo "null")
    echo ""
    echo "Application Insights:"
    if [ "$DAILY_CAP" != "null" ] && [ -n "$DAILY_CAP" ]; then
        if command -v bc &> /dev/null; then
            MONTHLY_EST=$(echo "scale=2; $DAILY_CAP * 30 * 2.30" | bc 2>/dev/null || echo "N/A")
        else
            MONTHLY_EST=$(awk "BEGIN {printf \"%.2f\", $DAILY_CAP * 30 * 2.30}" 2>/dev/null || echo "N/A")
        fi
        echo "  Daily Cap: ${DAILY_CAP} GB"
        echo "  Estimated: ~\$${MONTHLY_EST}/month (if cap is reached daily)"
    else
        echo "  Estimated: ~\$2.30/GB ingested (first 5GB free/month)"
        echo "  ⚠️  No daily cap configured"
    fi
fi

# Static Web App
SWA=$(az staticwebapp list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")
if [ -z "$SWA" ]; then
    # Try to find in any resource group
    SWA=$(az staticwebapp list --query "[?contains(name, 'secai-radar')].name" -o tsv | head -1)
fi

if [ -n "$SWA" ]; then
    SWA_RG=$(az staticwebapp show --name "$SWA" --query "resourceGroup" -o tsv 2>/dev/null || echo "$RESOURCE_GROUP")
    SKU=$(az staticwebapp show --name "$SWA" --resource-group "$SWA_RG" --query "sku.name" -o tsv 2>/dev/null || echo "Free")
    echo ""
    echo "Static Web App:"
    if [ "$SKU" == "Free" ]; then
        echo "  Cost: \$0/month (Free tier)"
    else
        echo "  Cost: ~\$9/month (Standard tier)"
    fi
fi

# Cosmos DB
COSMOS=$(az cosmosdb list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")
if [ -n "$COSMOS" ]; then
    FREE_TIER=$(az cosmosdb show --name "$COSMOS" --resource-group "$RESOURCE_GROUP" --query "enableFreeTier" -o tsv 2>/dev/null || echo "false")
    echo ""
    echo "Cosmos DB:"
    if [ "$FREE_TIER" == "true" ]; then
        echo "  Cost: \$0/month (Free Tier active)"
        echo "  Free Tier includes: 1,000 RU/s + 25GB storage"
    else
        echo "  Estimated: ~\$23-230/month (depending on throughput)"
    fi
fi

echo ""
echo "=========================================="
echo "Cost Management Links"
echo "=========================================="
echo ""
echo "Azure Portal Cost Analysis:"
echo "  https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/costanalysis"
echo ""
echo "Resource Group Costs:"
echo "  https://portal.azure.com/#@/resource/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/costAnalysis"
echo ""
echo "Set up Budget Alerts:"
echo "  https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/Budgets"
echo ""
echo "Azure Pricing Calculator:"
echo "  https://azure.microsoft.com/pricing/calculator/"
echo ""

