#!/bin/bash
# Comprehensive infrastructure verification and cost monitoring script
# Verifies all Azure resources are deployed and provides cost insights

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - can be overridden by environment variables
RESOURCE_GROUP="${RESOURCE_GROUP:-secai-radar-dev-rg}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
APP_NAME="${APP_NAME:-secai-radar}"
LOCATION="${LOCATION:-eastus2}"

# Resource names based on bicep template
STORAGE_ACCOUNT="${STORAGE_ACCOUNT:-secairadardevsa}"
FUNCTION_APP_NAME="${FUNCTION_APP_NAME:-${APP_NAME}-${ENVIRONMENT}-api}"
FUNCTION_PLAN_NAME="${FUNCTION_PLAN_NAME:-${APP_NAME}-${ENVIRONMENT}-plan}"
SWA_NAME="${SWA_NAME:-${APP_NAME}}"
APP_INSIGHTS_NAME="${APP_INSIGHTS_NAME:-${APP_NAME}-${ENVIRONMENT}-appi}"
COSMOS_ACCOUNT_NAME="${COSMOS_ACCOUNT_NAME:-secai-radar-cosmos}"
KEY_VAULT_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo "=========================================="
echo "SecAI Radar Infrastructure Verification"
echo "=========================================="
echo ""
echo "Subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
echo "Resource Group: $RESOURCE_GROUP"
echo "Environment: $ENVIRONMENT"
echo "Location: $LOCATION"
echo ""
echo "=========================================="
echo ""

# Track verification results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Function to check resource existence and status
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local resource_group=$3
    local check_type=$4  # "exists", "status", or "both"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    case $check_type in
        "exists")
            if az $resource_type show --name "$resource_name" --resource-group "$resource_group" &>/dev/null; then
                echo -e "${GREEN}✅${NC} $resource_type: $resource_name exists"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
                return 0
            else
                echo -e "${RED}❌${NC} $resource_type: $resource_name NOT FOUND"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
                return 1
            fi
            ;;
        "status")
            local status=$(az $resource_type show --name "$resource_name" --resource-group "$resource_group" --query "properties.provisioningState" -o tsv 2>/dev/null || echo "NotFound")
            if [ "$status" == "Succeeded" ]; then
                echo -e "${GREEN}✅${NC} $resource_type: $resource_name - Status: $status"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
                return 0
            elif [ "$status" == "NotFound" ]; then
                echo -e "${RED}❌${NC} $resource_type: $resource_name NOT FOUND"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
                return 1
            else
                echo -e "${YELLOW}⚠️${NC}  $resource_type: $resource_name - Status: $status"
                WARNINGS=$((WARNINGS + 1))
                return 1
            fi
            ;;
        "both")
            if az $resource_type show --name "$resource_name" --resource-group "$resource_group" &>/dev/null; then
                local status=$(az $resource_type show --name "$resource_name" --resource-group "$resource_group" --query "properties.provisioningState" -o tsv 2>/dev/null || echo "Unknown")
                if [ "$status" == "Succeeded" ] || [ "$status" == "Running" ] || [ "$status" == "Ready" ]; then
                    echo -e "${GREEN}✅${NC} $resource_type: $resource_name - Status: $status"
                    PASSED_CHECKS=$((PASSED_CHECKS + 1))
                    return 0
                else
                    echo -e "${YELLOW}⚠️${NC}  $resource_type: $resource_name - Status: $status"
                    WARNINGS=$((WARNINGS + 1))
                    return 1
                fi
            else
                echo -e "${RED}❌${NC} $resource_type: $resource_name NOT FOUND"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
                return 1
            fi
            ;;
    esac
}

# Check if resource group exists
echo "=== Resource Group ==="
if az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    RG_LOCATION=$(az group show --name "$RESOURCE_GROUP" --query location -o tsv)
    echo -e "${GREEN}✅${NC} Resource Group: $RESOURCE_GROUP exists (Location: $RG_LOCATION)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "${RED}❌${NC} Resource Group: $RESOURCE_GROUP NOT FOUND"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo ""
    echo "Cannot continue without resource group. Exiting."
    exit 1
fi
echo ""

# Check core infrastructure resources
echo "=== Core Infrastructure (from Bicep) ==="

# Storage Account
check_resource "storage account" "$STORAGE_ACCOUNT" "$RESOURCE_GROUP" "both"
STORAGE_SKU=$(az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --query "sku.name" -o tsv 2>/dev/null || echo "Unknown")
if [ "$STORAGE_SKU" != "Unknown" ]; then
    echo "    SKU: $STORAGE_SKU"
fi

# Function Plan
check_resource "functionapp plan" "$FUNCTION_PLAN_NAME" "$RESOURCE_GROUP" "both"
FUNCTION_PLAN_SKU=$(az functionapp plan show --name "$FUNCTION_PLAN_NAME" --resource-group "$RESOURCE_GROUP" --query "sku.name" -o tsv 2>/dev/null || echo "Unknown")
if [ "$FUNCTION_PLAN_SKU" != "Unknown" ]; then
    echo "    SKU: $FUNCTION_PLAN_SKU"
    MAX_WORKERS=$(az functionapp plan show --name "$FUNCTION_PLAN_NAME" --resource-group "$RESOURCE_GROUP" --query "sku.maximumElasticWorkerCount" -o tsv 2>/dev/null || echo "Unknown")
    if [ "$MAX_WORKERS" != "Unknown" ]; then
        echo "    Max Elastic Workers: $MAX_WORKERS"
    fi
    PRE_WARMED=$(az functionapp plan show --name "$FUNCTION_PLAN_NAME" --resource-group "$RESOURCE_GROUP" --query "sku.preWarmedInstanceCount" -o tsv 2>/dev/null || echo "Unknown")
    if [ "$PRE_WARMED" != "Unknown" ]; then
        echo "    Pre-warmed Instances: $PRE_WARMED"
    fi
fi

# Function App
check_resource "functionapp" "$FUNCTION_APP_NAME" "$RESOURCE_GROUP" "both"
FUNCTION_STATE=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "state" -o tsv 2>/dev/null || echo "Unknown")
if [ "$FUNCTION_STATE" != "Unknown" ]; then
    echo "    State: $FUNCTION_STATE"
    FUNCTION_URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv 2>/dev/null || echo "Unknown")
    if [ "$FUNCTION_URL" != "Unknown" ]; then
        echo "    URL: https://$FUNCTION_URL"
    fi
fi

# Application Insights
check_resource "monitor component" "$APP_INSIGHTS_NAME" "$RESOURCE_GROUP" "both"
APP_INSIGHTS_DAILY_CAP=$(az monitor app-insights component show --app "$APP_INSIGHTS_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.DailyQuota" -o tsv 2>/dev/null || echo "Unknown")
if [ "$APP_INSIGHTS_DAILY_CAP" != "Unknown" ] && [ "$APP_INSIGHTS_DAILY_CAP" != "null" ]; then
    echo "    Daily Cap: ${APP_INSIGHTS_DAILY_CAP} GB"
fi

echo ""

# Check optional resources
echo "=== Optional Resources ==="

# Static Web App
if az staticwebapp show --name "$SWA_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    SWA_STATE=$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.provisioningState" -o tsv)
    SWA_URL=$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostname" -o tsv)
    if [ "$SWA_STATE" == "Succeeded" ]; then
        echo -e "${GREEN}✅${NC} Static Web App: $SWA_NAME - Status: $SWA_STATE"
        echo "    URL: https://$SWA_URL"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️${NC}  Static Web App: $SWA_NAME - Status: $SWA_STATE"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "${YELLOW}⚠️${NC}  Static Web App: $SWA_NAME NOT FOUND (may be in different resource group)"
    WARNINGS=$((WARNINGS + 1))
fi

# Cosmos DB
if az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    COSMOS_STATE=$(az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --query "provisioningState" -o tsv)
    if [ "$COSMOS_STATE" == "Succeeded" ]; then
        echo -e "${GREEN}✅${NC} Cosmos DB: $COSMOS_ACCOUNT_NAME - Status: $COSMOS_STATE"
        FREE_TIER=$(az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --query "enableFreeTier" -o tsv)
        if [ "$FREE_TIER" == "true" ]; then
            echo "    Free Tier: ENABLED"
        else
            echo "    Free Tier: DISABLED"
        fi
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️${NC}  Cosmos DB: $COSMOS_ACCOUNT_NAME - Status: $COSMOS_STATE"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${BLUE}ℹ️${NC}  Cosmos DB: $COSMOS_ACCOUNT_NAME not found (optional resource)"
fi

# Key Vault
if az keyvault show --name "$KEY_VAULT_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    KV_STATE=$(az keyvault show --name "$KEY_VAULT_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.provisioningState" -o tsv)
    if [ "$KV_STATE" == "Succeeded" ]; then
        echo -e "${GREEN}✅${NC} Key Vault: $KEY_VAULT_NAME - Status: $KV_STATE"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${YELLOW}⚠️${NC}  Key Vault: $KEY_VAULT_NAME - Status: $KV_STATE"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${BLUE}ℹ️${NC}  Key Vault: $KEY_VAULT_NAME not found (optional resource)"
fi

echo ""

# Check storage queues
echo "=== Storage Queues ==="
if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    QUEUE_NAME="ai-jobs"
    STORAGE_KEY=$(az storage account keys list --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --query "[0].value" -o tsv)
    if az storage queue exists --name "$QUEUE_NAME" --account-name "$STORAGE_ACCOUNT" --account-key "$STORAGE_KEY" --query "exists" -o tsv 2>/dev/null | grep -q "true"; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        echo -e "${GREEN}✅${NC} Storage Queue: $QUEUE_NAME exists"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        echo -e "${YELLOW}⚠️${NC}  Storage Queue: $QUEUE_NAME not found"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

echo ""

# Cost Analysis Section
echo "=========================================="
echo "Cost Analysis & Monitoring"
echo "=========================================="
echo ""

# Get current month start date
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    MONTH_START=$(date -v1d +%Y-%m-%d)
else
    # Linux
    MONTH_START=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d)
fi
TODAY=$(date +%Y-%m-%d)

echo "=== Resource Group Cost Summary ==="
echo "Period: $MONTH_START to $TODAY"
echo ""

# Try to get cost data (requires Cost Management Reader role)
COST_DATA=$(az consumption usage list \
    --start-date "$MONTH_START" \
    --end-date "$TODAY" \
    --query "[?instanceName=='$RESOURCE_GROUP' || contains(instanceName, 'secai-radar')]" \
    -o json 2>/dev/null || echo "[]")

if [ "$COST_DATA" != "[]" ] && [ -n "$COST_DATA" ]; then
    TOTAL_COST=$(echo "$COST_DATA" | jq -r '[.[] | .pretaxCost | tonumber] | add' 2>/dev/null || echo "0")
    if [ "$TOTAL_COST" != "0" ] && [ -n "$TOTAL_COST" ]; then
        echo -e "${GREEN}Current Month Cost: \$${TOTAL_COST}${NC}"
    else
        echo -e "${BLUE}Cost data available but calculation requires jq${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cost data not available via CLI${NC}"
    echo "   (May require Cost Management Reader role)"
    echo "   View costs in Azure Portal:"
    echo "   https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/costanalysis"
fi

echo ""

# Cost breakdown by resource type
echo "=== Estimated Monthly Costs (Based on SKUs) ==="

# Function Plan costs (Elastic Premium)
if [ "$FUNCTION_PLAN_SKU" != "Unknown" ]; then
    case $FUNCTION_PLAN_SKU in
        "EP1")
            FUNCTION_COST="~\$0.20/hour base + usage = ~\$146/month (if always on)"
            echo -e "${YELLOW}Function Plan (EP1):${NC} $FUNCTION_COST"
            echo "   Note: With preWarmedInstanceCount=0, costs are lower when idle"
            ;;
        "EP2")
            FUNCTION_COST="~\$0.40/hour base + usage = ~\$292/month (if always on)"
            echo -e "${YELLOW}Function Plan (EP2):${NC} $FUNCTION_COST"
            ;;
        "EP3")
            FUNCTION_COST="~\$0.80/hour base + usage = ~\$584/month (if always on)"
            echo -e "${YELLOW}Function Plan (EP3):${NC} $FUNCTION_COST"
            ;;
        *)
            echo -e "${BLUE}Function Plan (${FUNCTION_PLAN_SKU}):${NC} Check Azure pricing calculator"
            ;;
    esac
fi

# Storage Account costs
if [ "$STORAGE_SKU" != "Unknown" ]; then
    echo -e "${BLUE}Storage Account (${STORAGE_SKU}):${NC} ~\$0.0184/GB/month + transactions"
    echo "   (First 50GB free, then ~\$0.92/month per 50GB)"
fi

# Application Insights costs
echo -e "${BLUE}Application Insights:${NC}"
if [ "$APP_INSIGHTS_DAILY_CAP" != "Unknown" ] && [ "$APP_INSIGHTS_DAILY_CAP" != "null" ]; then
    if command -v bc &> /dev/null; then
        MONTHLY_EST=$(echo "scale=2; $APP_INSIGHTS_DAILY_CAP * 30 * 2.30" | bc 2>/dev/null || echo "N/A")
    else
        # Simple calculation without bc
        MONTHLY_EST=$(awk "BEGIN {printf \"%.2f\", $APP_INSIGHTS_DAILY_CAP * 30 * 2.30}" 2>/dev/null || echo "N/A")
    fi
    echo "   Daily Cap: ${APP_INSIGHTS_DAILY_CAP} GB/day = ~\$${MONTHLY_EST}/month"
else
    echo "   ~\$2.30/GB ingested (first 5GB free/month)"
fi

# Cosmos DB costs
if az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    FREE_TIER=$(az cosmosdb show --name "$COSMOS_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --query "enableFreeTier" -o tsv)
    if [ "$FREE_TIER" == "true" ]; then
        echo -e "${GREEN}Cosmos DB:${NC} \$0/month (Free Tier active - 1,000 RU/s + 25GB free)"
    else
        echo -e "${YELLOW}Cosmos DB:${NC} ~\$23-230/month (depending on throughput)"
    fi
fi

# Static Web App costs
if az staticwebapp show --name "$SWA_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    SWA_SKU=$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RESOURCE_GROUP" --query "sku.name" -o tsv 2>/dev/null || echo "Free")
    if [ "$SWA_SKU" == "Free" ]; then
        echo -e "${GREEN}Static Web App:${NC} \$0/month (Free tier)"
    else
        echo -e "${YELLOW}Static Web App:${NC} ~\$9/month (Standard tier)"
    fi
fi

echo ""

# Cost optimization recommendations
echo "=== Cost Optimization Recommendations ==="
if [ "$PRE_WARMED" == "0" ] || [ "$PRE_WARMED" == "Unknown" ]; then
    echo -e "${GREEN}✅${NC} Pre-warmed instances set to 0 (good for cost savings)"
else
    echo -e "${YELLOW}⚠️${NC}  Consider setting preWarmedInstanceCount to 0 to reduce idle costs"
fi

if [ "$APP_INSIGHTS_DAILY_CAP" != "Unknown" ] && [ "$APP_INSIGHTS_DAILY_CAP" != "null" ] && [ "$APP_INSIGHTS_DAILY_CAP" != "0" ]; then
    echo -e "${GREEN}✅${NC} Application Insights daily cap configured (${APP_INSIGHTS_DAILY_CAP} GB)"
else
    echo -e "${YELLOW}⚠️${NC}  Consider setting Application Insights daily cap to prevent unexpected costs"
fi

echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo "Total Checks: $TOTAL_CHECKS"
echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
if [ $FAILED_CHECKS -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
fi
echo ""

if [ $FAILED_CHECKS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All infrastructure verified successfully!${NC}"
    exit 0
elif [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Infrastructure verified with warnings${NC}"
    exit 0
else
    echo -e "${RED}❌ Some infrastructure checks failed${NC}"
    exit 1
fi

