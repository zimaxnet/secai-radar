#!/bin/bash
# Script to configure DNS in Azure for SecAI Radar

# Configuration
DOMAIN="secai-radar.zimax.net"
DNS_ZONE="zimax.net"
SUBSCRIPTION_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"
GITHUB_USERNAME=""  # Replace with your GitHub username

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "SecAI Radar DNS Configuration"
echo "=========================================="
echo ""

# Check if logged in to Azure
echo "Checking Azure login..."
if ! az account show &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Please run: az login"
    exit 1
fi

echo -e "${GREEN}✅ Logged in to Azure${NC}"
echo ""

# Set subscription
echo "Setting subscription..."
az account set --subscription "$SUBSCRIPTION_ID"
echo -e "${GREEN}✅ Subscription set${NC}"
echo ""

# Check for DNS zone
echo "Checking for DNS zone: $DNS_ZONE"
DNS_ZONES=$(az network dns zone list --query "[?name=='$DNS_ZONE']" -o json)

if [ "$DNS_ZONES" == "[]" ]; then
    echo -e "${YELLOW}⚠️  DNS zone '$DNS_ZONE' not found in Azure${NC}"
    echo ""
    echo "Options:"
    echo "1. Create DNS zone in Azure"
    echo "2. Use external DNS provider (if zone is managed elsewhere)"
    echo ""
    read -p "Do you want to create the DNS zone in Azure? (y/n): " CREATE_ZONE
    
    if [ "$CREATE_ZONE" == "y" ] || [ "$CREATE_ZONE" == "Y" ]; then
        read -p "Enter resource group name for DNS zone: " RG_NAME
        
        if [ -z "$RG_NAME" ]; then
            echo -e "${RED}❌ Resource group name required${NC}"
            exit 1
        fi
        
        echo "Creating DNS zone..."
        az network dns zone create \
            --resource-group "$RG_NAME" \
            --name "$DNS_ZONE"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ DNS zone created${NC}"
            RG="$RG_NAME"
        else
            echo -e "${RED}❌ Failed to create DNS zone${NC}"
            exit 1
        fi
    else
        echo "Skipping DNS zone creation. Please configure DNS externally."
        exit 0
    fi
else
    RG=$(echo "$DNS_ZONES" | jq -r '.[0].resourceGroup')
    echo -e "${GREEN}✅ DNS zone '$DNS_ZONE' found${NC}"
    echo "   Resource Group: $RG"
fi

echo ""

# Get GitHub username if not set
if [ -z "$GITHUB_USERNAME" ]; then
    read -p "Enter your GitHub username or organization name: " GITHUB_USERNAME
    
    if [ -z "$GITHUB_USERNAME" ]; then
        echo -e "${RED}❌ GitHub username required${NC}"
        exit 1
    fi
fi

CNAME_VALUE="${GITHUB_USERNAME}.github.io"

# Check if CNAME record exists
echo "Checking for existing CNAME record..."
EXISTING_CNAME=$(az network dns record-set cname show \
    --resource-group "$RG" \
    --zone-name "$DNS_ZONE" \
    --name "secai-radar" \
    2>/dev/null)

if [ $? -eq 0 ]; then
    CURRENT_VALUE=$(az network dns record-set cname show \
        --resource-group "$RG" \
        --zone-name "$DNS_ZONE" \
        --name "secai-radar" \
        --query "cnameRecord.cname" -o tsv)
    
    echo -e "${YELLOW}⚠️  CNAME record already exists${NC}"
    echo "   Current value: $CURRENT_VALUE"
    echo "   New value: $CNAME_VALUE"
    echo ""
    read -p "Do you want to update the CNAME record? (y/n): " UPDATE_CNAME
    
    if [ "$UPDATE_CNAME" == "y" ] || [ "$UPDATE_CNAME" == "Y" ]; then
        echo "Updating CNAME record..."
        az network dns record-set cname set-record \
            --resource-group "$RG" \
            --zone-name "$DNS_ZONE" \
            --record-set-name "secai-radar" \
            --cname "$CNAME_VALUE" \
            --ttl 3600
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ CNAME record updated${NC}"
        else
            echo -e "${RED}❌ Failed to update CNAME record${NC}"
            exit 1
        fi
    else
        echo "Skipping CNAME update"
    fi
else
    echo "Creating CNAME record..."
    az network dns record-set cname create \
        --resource-group "$RG" \
        --zone-name "$DNS_ZONE" \
        --name "secai-radar" \
        --cname "$CNAME_VALUE" \
        --ttl 3600
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ CNAME record created${NC}"
        echo "   Name: secai-radar"
        echo "   Value: $CNAME_VALUE"
        echo "   TTL: 3600"
    else
        echo -e "${RED}❌ Failed to create CNAME record${NC}"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "DNS Configuration Summary"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "DNS Zone: $DNS_ZONE"
echo "Resource Group: $RG"
echo "CNAME Record:"
echo "  Name: secai-radar"
echo "  Value: $CNAME_VALUE"
echo "  TTL: 3600"
echo ""
echo "Main App URL: https://$DOMAIN"
echo "Wiki URL: https://$DOMAIN/wiki"
echo ""
echo -e "${GREEN}✅ DNS configuration complete${NC}"
echo ""
echo "Note: DNS propagation may take 1-24 hours (usually 1-2 hours)"
echo ""

