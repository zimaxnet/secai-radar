#!/bin/bash
# Implement DNS Security Improvements in Azure DNS
# This script implements high-priority DNS security features for SecAI Radar

set -e

# Configuration
DOMAIN="zimax.net"
SUB_DOMAIN="secai-radar"
RESOURCE_GROUP="dns-rg"
SUBSCRIPTION_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"
SECURITY_EMAIL="security@zimax.net"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Azure DNS Security Implementation${NC}"
echo -e "${BLUE}Domain: ${SUB_DOMAIN}.${DOMAIN}${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Please run: az login"
    exit 1
fi

# Set subscription
az account set --subscription "$SUBSCRIPTION_ID" &> /dev/null
echo -e "${GREEN}✓ Using subscription: ${SUBSCRIPTION_ID}${NC}"
echo ""

# Verify DNS zone exists
echo "1. Verifying DNS zone..."
if ! az network dns zone show --resource-group "$RESOURCE_GROUP" --name "$DOMAIN" &> /dev/null; then
    echo -e "${RED}❌ DNS zone '${DOMAIN}' not found in resource group '${RESOURCE_GROUP}'${NC}"
    exit 1
fi
echo -e "${GREEN}✓ DNS zone verified${NC}"
echo ""

# Check current DNSSEC status
echo "2. Checking DNSSEC status..."
DNSSEC_STATUS=$(az network dns zone show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DOMAIN" \
    --query "dnssecEnabled" -o tsv 2>/dev/null || echo "null")

if [ "$DNSSEC_STATUS" = "true" ]; then
    echo -e "${GREEN}✓ DNSSEC is already enabled${NC}"
elif [ "$DNSSEC_STATUS" = "null" ] || [ -z "$DNSSEC_STATUS" ]; then
    echo -e "${YELLOW}Attempting to enable DNSSEC...${NC}"
    if az network dns zone update \
        --resource-group "$RESOURCE_GROUP" \
        --name "$DOMAIN" \
        --set dnssecEnabled=true 2>/dev/null; then
        echo -e "${GREEN}✓ DNSSEC enabled successfully${NC}"
        echo -e "${YELLOW}  Note: You may need to configure DS records at your domain registrar${NC}"
        echo -e "${YELLOW}  Check Azure Portal for DS record details${NC}"
    else
        echo -e "${YELLOW}⚠ DNSSEC may not be available in your Azure region or subscription${NC}"
        echo -e "${YELLOW}  DNSSEC is currently available in limited regions${NC}"
        echo -e "${YELLOW}  See: https://docs.microsoft.com/azure/dns/dnssec-overview${NC}"
    fi
else
    echo -e "${YELLOW}⚠ DNSSEC status: ${DNSSEC_STATUS}${NC}"
fi
echo ""

# Add CAA records for the root domain
echo "3. Adding CAA records for root domain..."
CAA_EXISTS=$(az network dns record-set caa show \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --name "@" \
    --query "name" -o tsv 2>/dev/null || echo "")

if [ -z "$CAA_EXISTS" ]; then
    echo "   Creating CAA record set..."
    az network dns record-set caa create \
        --resource-group "$RESOURCE_GROUP" \
        --zone-name "$DOMAIN" \
        --name "@" \
        --ttl 3600 &> /dev/null
fi

# Add CAA records
echo "   Adding CAA records..."

# Remove existing records if any (to avoid duplicates)
az network dns record-set caa remove-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issue \
    --value "letsencrypt.org" 2>/dev/null || true

az network dns record-set caa remove-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issuewild \
    --value "letsencrypt.org" 2>/dev/null || true

az network dns record-set caa remove-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag iodef \
    --value "mailto:${SECURITY_EMAIL}" 2>/dev/null || true

# Add new CAA records
az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issue \
    --value "letsencrypt.org"

az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issuewild \
    --value "letsencrypt.org"

az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag iodef \
    --value "mailto:${SECURITY_EMAIL}"

echo -e "${GREEN}✓ CAA records added for root domain${NC}"
echo ""

# Add CAA records for secai-radar subdomain
echo "4. Adding CAA records for secai-radar subdomain..."
CAA_SUB_EXISTS=$(az network dns record-set caa show \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --name "${SUB_DOMAIN}" \
    --query "name" -o tsv 2>/dev/null || echo "")

if [ -z "$CAA_SUB_EXISTS" ]; then
    echo "   Creating CAA record set for subdomain..."
    az network dns record-set caa create \
        --resource-group "$RESOURCE_GROUP" \
        --zone-name "$DOMAIN" \
        --name "${SUB_DOMAIN}" \
        --ttl 3600 &> /dev/null
fi

# Remove existing records if any
az network dns record-set caa remove-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "${SUB_DOMAIN}" \
    --flags 0 \
    --tag issue \
    --value "letsencrypt.org" 2>/dev/null || true

az network dns record-set caa remove-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "${SUB_DOMAIN}" \
    --flags 0 \
    --tag issuewild \
    --value "letsencrypt.org" 2>/dev/null || true

# Add new CAA records
az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "${SUB_DOMAIN}" \
    --flags 0 \
    --tag issue \
    --value "letsencrypt.org"

az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "${SUB_DOMAIN}" \
    --flags 0 \
    --tag issuewild \
    --value "letsencrypt.org"

echo -e "${GREEN}✓ CAA records added for ${SUB_DOMAIN} subdomain${NC}"
echo ""

# Optimize TTL values for existing records
echo "5. Optimizing TTL values..."
# Update secai-radar A record TTL if it exists
A_RECORD_TTL=$(az network dns record-set a show \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --name "${SUB_DOMAIN}" \
    --query "ttl" -o tsv 2>/dev/null || echo "")

if [ -n "$A_RECORD_TTL" ] && [ "$A_RECORD_TTL" != "3600" ]; then
    echo "   Updating A record TTL to 3600 seconds..."
    az network dns record-set a update \
        --resource-group "$RESOURCE_GROUP" \
        --zone-name "$DOMAIN" \
        --name "${SUB_DOMAIN}" \
        --set ttl=3600 &> /dev/null
    echo -e "${GREEN}✓ A record TTL updated${NC}"
fi

# Update wiki.secai-radar CNAME TTL if it exists
WIKI_CNAME_TTL=$(az network dns record-set cname show \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --name "wiki.${SUB_DOMAIN}" \
    --query "ttl" -o tsv 2>/dev/null || echo "")

if [ -n "$WIKI_CNAME_TTL" ] && [ "$WIKI_CNAME_TTL" != "3600" ]; then
    echo "   Updating wiki CNAME TTL to 3600 seconds..."
    az network dns record-set cname update \
        --resource-group "$RESOURCE_GROUP" \
        --zone-name "$DOMAIN" \
        --name "wiki.${SUB_DOMAIN}" \
        --set ttl=3600 &> /dev/null
    echo -e "${GREEN}✓ CNAME record TTL updated${NC}"
fi

echo ""

# Set up DNS monitoring (Log Analytics)
echo "6. Setting up DNS monitoring..."
LOG_ANALYTICS_WORKSPACE="law-secai-radar-dns"

# Check if Log Analytics workspace exists
WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
    --query "customerId" -o tsv 2>/dev/null || echo "")

if [ -z "$WORKSPACE_ID" ]; then
    echo "   Creating Log Analytics workspace..."
    LOCATION=$(az network dns zone show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$DOMAIN" \
        --query "location" -o tsv)
    
    az monitor log-analytics workspace create \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
        --location "$LOCATION" &> /dev/null
    
    WORKSPACE_ID=$(az monitor log-analytics workspace show \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
        --query "customerId" -o tsv)
    
    echo -e "${GREEN}✓ Log Analytics workspace created${NC}"
else
    echo -e "${GREEN}✓ Log Analytics workspace already exists${NC}"
fi

# Enable diagnostic settings for DNS zone (if not already enabled)
DNS_ZONE_RESOURCE_ID=$(az network dns zone show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DOMAIN" \
    --query "id" -o tsv)

DIAGNOSTIC_EXISTS=$(az monitor diagnostic-settings list \
    --resource "$DNS_ZONE_RESOURCE_ID" \
    --query "[?name=='dns-query-logging'].name" -o tsv 2>/dev/null || echo "")

if [ -z "$DIAGNOSTIC_EXISTS" ]; then
    echo "   Configuring diagnostic logging..."
    # Note: Azure DNS doesn't support diagnostic settings directly
    # DNS query logs are available through Azure Monitor Metrics
    echo -e "${YELLOW}  Note: DNS query metrics are available in Azure Monitor${NC}"
    echo -e "${YELLOW}  View metrics in Azure Portal: Monitor > Metrics > DNS Zone${NC}"
else
    echo -e "${GREEN}✓ Diagnostic logging already configured${NC}"
fi

echo ""

# Create alert rule for DNS zone changes
echo "7. Setting up DNS change alerts..."
ALERT_RULE_NAME="dns-zone-changes"

# Check if alert rule exists
ALERT_EXISTS=$(az monitor metrics alert show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ALERT_RULE_NAME" \
    --query "name" -o tsv 2>/dev/null || echo "")

if [ -z "$ALERT_EXISTS" ]; then
    echo "   Creating alert rule for DNS record count changes..."
    # Create action group for notifications
    ACTION_GROUP_NAME="dns-alerts-action-group"
    
    ACTION_GROUP_EXISTS=$(az monitor action-group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$ACTION_GROUP_NAME" \
        --query "name" -o tsv 2>/dev/null || echo "")
    
    if [ -z "$ACTION_GROUP_EXISTS" ]; then
        echo "   Creating action group..."
        az monitor action-group create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$ACTION_GROUP_NAME" \
            --short-name "dns-alerts" \
            --email-receivers name="Admin" email="${SECURITY_EMAIL}" &> /dev/null
    fi
    
    echo -e "${GREEN}✓ Alert configuration ready${NC}"
    echo -e "${YELLOW}  Configure alerts manually in Azure Portal for DNS metrics${NC}"
else
    echo -e "${GREEN}✓ Alert rule already exists${NC}"
fi

echo ""

# Display summary
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Implementation Summary${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

echo "DNS Zone: ${DOMAIN}"
echo "Resource Group: ${RESOURCE_GROUP}"
echo ""

echo "CAA Records:"
echo "  ✓ Root domain (@) - Let's Encrypt authorized"
echo "  ✓ Subdomain (${SUB_DOMAIN}) - Let's Encrypt authorized"
echo ""

echo "DNSSEC:"
if [ "$DNSSEC_STATUS" = "true" ]; then
    echo -e "  ${GREEN}✓ Enabled${NC}"
    echo "  Note: Configure DS records at your registrar"
else
    echo -e "  ${YELLOW}⚠ Status: ${DNSSEC_STATUS}${NC}"
    echo "  Note: May not be available in your region"
fi
echo ""

echo "Monitoring:"
echo "  ✓ Log Analytics workspace: ${LOG_ANALYTICS_WORKSPACE}"
echo "  ✓ Metrics available in Azure Monitor"
echo ""

echo "TTL Values:"
echo "  ✓ Optimized to 3600 seconds (1 hour)"
echo ""

echo -e "${GREEN}Next Steps:${NC}"
echo "1. Verify CAA records: dig CAA ${DOMAIN}"
echo "2. Check DNSSEC status: dig +dnssec ${DOMAIN}"
echo "3. If DNSSEC enabled, configure DS records at registrar"
echo "4. Set up custom alerts in Azure Portal"
echo "5. Review DNS metrics in Azure Monitor"
echo ""

echo -e "${GREEN}✅ DNS security improvements implemented!${NC}"
echo ""

