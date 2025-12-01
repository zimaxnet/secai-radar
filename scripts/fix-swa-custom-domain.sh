#!/bin/bash
# Script to fix Azure Static Web App custom domain and certificate issues
# This addresses common problems with SWA custom domain certificate provisioning

set -e

# Configuration
SWA_NAME="secai-radar"
RESOURCE_GROUP="secai-radar-rg"
CUSTOM_DOMAIN="secai-radar.zimax.net"
DNS_ZONE="zimax.net"
DNS_RG="dns-rg"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Azure Static Web App Custom Domain Fix"
echo "=========================================="
echo ""
echo "SWA Name: $SWA_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Custom Domain: $CUSTOM_DOMAIN"
echo ""

# Check Azure login
if ! az account show &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Please run: az login"
    exit 1
fi

echo -e "${GREEN}✅ Logged in to Azure${NC}"
echo ""

# Get SWA default hostname
echo "Getting Static Web App details..."
SWA_HOSTNAME=$(az staticwebapp show \
    --name "$SWA_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "defaultHostname" -o tsv)

if [ -z "$SWA_HOSTNAME" ]; then
    echo -e "${RED}❌ Static Web App not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Static Web App${NC}"
echo "   Default Hostname: $SWA_HOSTNAME"
echo ""

# Check current custom domains
echo "Checking current custom domains..."
CURRENT_DOMAINS=$(az staticwebapp hostname list \
    --name "$SWA_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[].hostname" -o tsv)

if echo "$CURRENT_DOMAINS" | grep -q "$CUSTOM_DOMAIN"; then
    echo -e "${YELLOW}⚠️  Custom domain already exists in SWA${NC}"
    
    # Check validation state
    VALIDATION_STATE=$(az staticwebapp hostname show \
        --name "$SWA_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --hostname "$CUSTOM_DOMAIN" \
        --query "validationState" -o tsv 2>/dev/null || echo "Unknown")
    
    echo "   Validation State: $VALIDATION_STATE"
    echo ""
    
    if [ "$VALIDATION_STATE" != "Valid" ] && [ "$VALIDATION_STATE" != "Approved" ]; then
        echo -e "${YELLOW}⚠️  Domain validation is not complete${NC}"
        echo "   This is likely why the certificate isn't deploying"
        echo ""
    fi
else
    echo -e "${BLUE}ℹ️  Custom domain not yet added to SWA${NC}"
    echo ""
fi

# Check DNS CNAME record
echo "Checking DNS CNAME record..."
CNAME_VALUE=$(az network dns record-set cname show \
    --resource-group "$DNS_RG" \
    --zone-name "$DNS_ZONE" \
    --name "secai-radar" \
    --query "cnameRecord.cname" -o tsv 2>/dev/null || echo "")

if [ -z "$CNAME_VALUE" ]; then
    echo -e "${RED}❌ CNAME record not found${NC}"
    echo ""
    echo "Creating CNAME record pointing to SWA..."
    az network dns record-set cname create \
        --resource-group "$DNS_RG" \
        --zone-name "$DNS_ZONE" \
        --name "secai-radar" \
        --ttl 300
    
    az network dns record-set cname set-record \
        --resource-group "$DNS_RG" \
        --zone-name "$DNS_ZONE" \
        --record-set-name "secai-radar" \
        --cname "$SWA_HOSTNAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ CNAME record created${NC}"
        echo "   Name: secai-radar"
        echo "   Value: $SWA_HOSTNAME"
    else
        echo -e "${RED}❌ Failed to create CNAME record${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ CNAME record found${NC}"
    echo "   Current Value: $CNAME_VALUE"
    echo "   Should Point To: $SWA_HOSTNAME"
    echo ""
    
    if [ "$CNAME_VALUE" != "$SWA_HOSTNAME" ]; then
        echo -e "${YELLOW}⚠️  CNAME record points to wrong value!${NC}"
        echo "   This is likely causing certificate provisioning to fail"
        echo ""
        read -p "Do you want to update the CNAME record to point to $SWA_HOSTNAME? (y/n): " UPDATE_DNS
        
        if [ "$UPDATE_DNS" == "y" ] || [ "$UPDATE_DNS" == "Y" ]; then
            echo "Updating CNAME record..."
            az network dns record-set cname set-record \
                --resource-group "$DNS_RG" \
                --zone-name "$DNS_ZONE" \
                --record-set-name "secai-radar" \
                --cname "$SWA_HOSTNAME" \
                --ttl 300
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ CNAME record updated${NC}"
            else
                echo -e "${RED}❌ Failed to update CNAME record${NC}"
                exit 1
            fi
        else
            echo "Skipping DNS update"
        fi
    else
        echo -e "${GREEN}✅ CNAME record is correct${NC}"
    fi
fi

echo ""

# Add custom domain to SWA if not already added
if ! echo "$CURRENT_DOMAINS" | grep -q "$CUSTOM_DOMAIN"; then
    echo "Adding custom domain to Static Web App..."
    echo -e "${YELLOW}⚠️  This may take several minutes...${NC}"
    
    az staticwebapp hostname set \
        --name "$SWA_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --hostname "$CUSTOM_DOMAIN" \
        --validation-method "cname-delegation"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Custom domain added to SWA${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Certificate provisioning can take 24-48 hours${NC}"
        echo "   The certificate will be automatically provisioned once DNS validates"
    else
        echo -e "${RED}❌ Failed to add custom domain${NC}"
        echo ""
        echo "Trying alternative method (manual validation)..."
        
        # Try with manual validation
        az staticwebapp hostname set \
            --name "$SWA_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --hostname "$CUSTOM_DOMAIN" \
            --validation-method "manual"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Custom domain added (manual validation)${NC}"
            echo ""
            echo "You may need to add a TXT record for validation"
        else
            echo -e "${RED}❌ Failed to add custom domain${NC}"
            exit 1
        fi
    fi
else
    echo -e "${BLUE}ℹ️  Custom domain already added to SWA${NC}"
    echo ""
    echo "If certificate is still not provisioning, try:"
    echo "1. Wait 24-48 hours for automatic provisioning"
    echo "2. Remove and re-add the custom domain"
    echo "3. Check DNS propagation (may take up to 24 hours)"
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Verify DNS propagation:"
echo "   dig +short $CUSTOM_DOMAIN CNAME"
echo "   Should return: $SWA_HOSTNAME"
echo ""
echo "2. Check certificate status in Azure Portal:"
echo "   https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$SWA_NAME/customDomains"
echo ""
echo "3. Certificate provisioning typically takes:"
echo "   - DNS validation: 1-24 hours"
echo "   - Certificate issuance: 24-48 hours after validation"
echo ""
echo "4. If certificate still doesn't provision after 48 hours:"
echo "   - Remove the custom domain from SWA"
echo "   - Wait 1 hour"
echo "   - Re-add the custom domain"
echo "   - Ensure CNAME points exactly to: $SWA_HOSTNAME"
echo ""

