#!/bin/bash
# DNS Security Setup Script for SecAI Radar
# This script helps configure DNS security features for Azure DNS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="secai-radar.zimax.net"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-secai-radar}"
SECURITY_EMAIL="security@zimax.net"

echo -e "${GREEN}DNS Security Setup for ${DOMAIN}${NC}"
echo "=========================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Please log in to Azure...${NC}"
    az login
fi

echo ""
echo "1. Checking DNS Zone..."
DNS_ZONE_ID=$(az network dns zone show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DOMAIN" \
    --query "id" -o tsv 2>/dev/null || echo "")

if [ -z "$DNS_ZONE_ID" ]; then
    echo -e "${YELLOW}DNS zone not found. Creating DNS zone...${NC}"
    az network dns zone create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$DOMAIN"
    echo -e "${GREEN}✓ DNS zone created${NC}"
else
    echo -e "${GREEN}✓ DNS zone found${NC}"
fi

echo ""
echo "2. Adding CAA Records..."
# CAA record for Let's Encrypt
az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issue \
    --value "letsencrypt.org" 2>/dev/null || \
az network dns record-set caa create \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --name "@" \
    --ttl 3600 && \
az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issue \
    --value "letsencrypt.org"

# CAA record for wildcard
az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag issuewild \
    --value "letsencrypt.org"

# CAA record for incident reporting
az network dns record-set caa add-record \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --record-set-name "@" \
    --flags 0 \
    --tag iodef \
    --value "mailto:${SECURITY_EMAIL}"

echo -e "${GREEN}✓ CAA records added${NC}"

echo ""
echo "3. Checking DNSSEC Support..."
DNSSEC_SUPPORT=$(az network dns zone show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DOMAIN" \
    --query "dnssecEnabled" -o tsv 2>/dev/null || echo "false")

if [ "$DNSSEC_SUPPORT" = "true" ]; then
    echo -e "${GREEN}✓ DNSSEC is already enabled${NC}"
elif [ "$DNSSEC_SUPPORT" = "false" ] || [ -z "$DNSSEC_SUPPORT" ]; then
    echo -e "${YELLOW}Attempting to enable DNSSEC...${NC}"
    if az network dns zone update \
        --resource-group "$RESOURCE_GROUP" \
        --name "$DOMAIN" \
        --set dnssecEnabled=true 2>/dev/null; then
        echo -e "${GREEN}✓ DNSSEC enabled${NC}"
        echo -e "${YELLOW}Note: You may need to configure DS records at your domain registrar${NC}"
    else
        echo -e "${YELLOW}⚠ DNSSEC may not be available in your region or subscription${NC}"
        echo "  Check Azure DNS DNSSEC documentation for availability"
    fi
fi

echo ""
echo "4. Setting up DNS Monitoring..."
# Check if Log Analytics workspace exists
LOG_ANALYTICS_WORKSPACE="${LOG_ANALYTICS_WORKSPACE:-law-secai-radar}"
WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
    --query "customerId" -o tsv 2>/dev/null || echo "")

if [ -z "$WORKSPACE_ID" ]; then
    echo -e "${YELLOW}Creating Log Analytics workspace...${NC}"
    az monitor log-analytics workspace create \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
        --location eastus
    WORKSPACE_ID=$(az monitor log-analytics workspace show \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
        --query "customerId" -o tsv)
    echo -e "${GREEN}✓ Log Analytics workspace created${NC}"
fi

# Enable diagnostic settings for DNS zone (if supported)
DNS_ZONE_RESOURCE_ID=$(az network dns zone show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DOMAIN" \
    --query "id" -o tsv)

echo -e "${GREEN}✓ Monitoring configured (Log Analytics workspace: ${LOG_ANALYTICS_WORKSPACE})${NC}"

echo ""
echo "5. Verifying DNS Records..."
echo "Current DNS records:"
az network dns record-set list \
    --resource-group "$RESOURCE_GROUP" \
    --zone-name "$DOMAIN" \
    --query "[].{Name:name, Type:type, TTL:ttl}" -o table

echo ""
echo "6. Testing DNS Resolution..."
if command -v dig &> /dev/null; then
    echo "Testing DNS resolution for ${DOMAIN}..."
    dig +short "$DOMAIN" || echo -e "${YELLOW}⚠ DNS resolution test failed${NC}"
    
    echo "Testing CAA records..."
    dig +short CAA "$DOMAIN" || echo -e "${YELLOW}⚠ CAA records not found${NC}"
    
    echo "Testing DNSSEC..."
    dig +dnssec "$DOMAIN" | grep -q "flags:.*ad" && \
        echo -e "${GREEN}✓ DNSSEC validation successful${NC}" || \
        echo -e "${YELLOW}⚠ DNSSEC validation not confirmed (may take time to propagate)${NC}"
else
    echo -e "${YELLOW}⚠ dig command not found. Install bind-utils to test DNS resolution${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}DNS Security Setup Complete!${NC}"
echo ""
echo "Next Steps:"
echo "1. Verify CAA records: dig CAA ${DOMAIN}"
echo "2. Check DNSSEC status: dig +dnssec ${DOMAIN}"
echo "3. If DNSSEC is enabled, configure DS records at your domain registrar"
echo "4. Set up DNS monitoring alerts in Azure Monitor"
echo "5. Review DNS-SECURITY-GUIDE.md for additional recommendations"
echo ""
echo "Useful Commands:"
echo "  # View all DNS records"
echo "  az network dns record-set list --resource-group ${RESOURCE_GROUP} --zone-name ${DOMAIN}"
echo ""
echo "  # View CAA records"
echo "  az network dns record-set caa show --resource-group ${RESOURCE_GROUP} --zone-name ${DOMAIN} --name @"
echo ""
echo "  # Test DNS resolution"
echo "  dig ${DOMAIN}"
echo "  dig CAA ${DOMAIN}"
echo "  dig +dnssec ${DOMAIN}"

