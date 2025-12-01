#!/bin/bash
# Script to configure Azure Static Web App with secairadar.cloud domain
# DNS is already working in the tenant

set -e

# Configuration
SWA_NAME="secai-radar"
RESOURCE_GROUP="secai-radar-rg"
CUSTOM_DOMAIN="secairadar.cloud"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Configure SWA Custom Domain: secairadar.cloud"
echo "=========================================="
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
echo "   Custom Domain: $CUSTOM_DOMAIN"
echo ""

# Check DNS resolution
echo "Verifying DNS resolution..."
DNS_RESULT=$(dig +short "$CUSTOM_DOMAIN" CNAME 2>/dev/null || dig +short "$CUSTOM_DOMAIN" A 2>/dev/null || echo "")

if [ -n "$DNS_RESULT" ]; then
    echo -e "${GREEN}✅ DNS is resolving${NC}"
    echo "   Resolved to: $DNS_RESULT"
    
    # Check if it points to SWA
    if echo "$DNS_RESULT" | grep -q "$SWA_HOSTNAME"; then
        echo -e "${GREEN}✅ DNS correctly points to SWA${NC}"
    else
        echo -e "${YELLOW}⚠️  DNS does not point to SWA hostname${NC}"
        echo "   Expected: $SWA_HOSTNAME"
        echo "   Found: $DNS_RESULT"
        echo ""
        echo "Please ensure DNS CNAME record points to: $SWA_HOSTNAME"
    fi
else
    echo -e "${YELLOW}⚠️  Could not resolve DNS (may still be propagating)${NC}"
fi

echo ""

# Check if custom domain already exists
echo "Checking for existing custom domain..."
EXISTING_DOMAIN=$(az staticwebapp hostname list \
    --name "$SWA_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[?hostname=='$CUSTOM_DOMAIN'].hostname" -o tsv)

if [ -n "$EXISTING_DOMAIN" ]; then
    echo -e "${BLUE}ℹ️  Custom domain already exists${NC}"
    
    # Get validation state
    VALIDATION_STATE=$(az staticwebapp hostname show \
        --name "$SWA_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --hostname "$CUSTOM_DOMAIN" \
        --query "validationState" -o tsv 2>/dev/null || echo "Unknown")
    
    STATUS=$(az staticwebapp hostname show \
        --name "$SWA_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --hostname "$CUSTOM_DOMAIN" \
        --query "status" -o tsv 2>/dev/null || echo "Unknown")
    
    echo "   Validation State: $VALIDATION_STATE"
    echo "   Status: $STATUS"
    echo ""
    
    if [ "$STATUS" == "Failed" ]; then
        echo -e "${YELLOW}⚠️  Domain addition previously failed${NC}"
        echo "Removing failed domain to retry..."
        az staticwebapp hostname delete \
            --name "$SWA_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --hostname "$CUSTOM_DOMAIN" \
            --yes
        
        echo "Waiting 15 seconds for Azure to process removal..."
        sleep 15
        EXISTING_DOMAIN=""
    elif [ "$VALIDATION_STATE" == "Valid" ] || [ "$VALIDATION_STATE" == "Approved" ]; then
        echo -e "${GREEN}✅ Domain is validated and should be working${NC}"
        echo ""
        echo "Certificate provisioning typically takes 24-48 hours after validation"
        exit 0
    fi
fi

# Add custom domain if not exists or was removed
if [ -z "$EXISTING_DOMAIN" ]; then
    echo "Adding custom domain to Static Web App..."
    echo -e "${YELLOW}⚠️  This may take a few minutes...${NC}"
    echo ""
    
    # Try adding with CNAME delegation (automatic validation)
    echo "Attempting to add domain with CNAME delegation..."
    ADD_RESULT=$(az staticwebapp hostname set \
        --name "$SWA_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --hostname "$CUSTOM_DOMAIN" \
        --validation-method cname-delegation 2>&1)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Custom domain added successfully${NC}"
        echo ""
        echo "Waiting for validation (this may take a few minutes)..."
        
        # Wait and check validation status
        for i in {1..12}; do
            sleep 10
            VALIDATION_STATE=$(az staticwebapp hostname show \
                --name "$SWA_NAME" \
                --resource-group "$RESOURCE_GROUP" \
                --hostname "$CUSTOM_DOMAIN" \
                --query "validationState" -o tsv 2>/dev/null || echo "Pending")
            
            STATUS=$(az staticwebapp hostname show \
                --name "$SWA_NAME" \
                --resource-group "$RESOURCE_GROUP" \
                --hostname "$CUSTOM_DOMAIN" \
                --query "status" -o tsv 2>/dev/null || echo "Pending")
            
            echo "   Status: $STATUS | Validation: $VALIDATION_STATE"
            
            if [ "$STATUS" == "Ready" ] || [ "$VALIDATION_STATE" == "Valid" ] || [ "$VALIDATION_STATE" == "Approved" ]; then
                echo -e "${GREEN}✅ Domain validated successfully!${NC}"
                break
            elif [ "$STATUS" == "Failed" ]; then
                echo -e "${RED}❌ Domain validation failed${NC}"
                break
            fi
        done
    else
        echo -e "${YELLOW}⚠️  CNAME delegation method failed, trying manual validation...${NC}"
        echo "$ADD_RESULT"
        echo ""
        
        # Try manual validation
        az staticwebapp hostname set \
            --name "$SWA_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --hostname "$CUSTOM_DOMAIN" \
            --validation-method manual
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Custom domain added (manual validation)${NC}"
            echo ""
            echo "You may need to add a TXT record for validation"
        else
            echo -e "${RED}❌ Failed to add custom domain${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Configuration Summary"
echo "=========================================="
echo ""
echo "Static Web App: $SWA_NAME"
echo "Default Hostname: $SWA_HOSTNAME"
echo "Custom Domain: $CUSTOM_DOMAIN"
echo ""
echo "Next Steps:"
echo "1. Certificate provisioning takes 24-48 hours after DNS validation"
echo "2. Check status in Azure Portal:"
echo "   https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$SWA_NAME/customDomains"
echo ""
echo "3. Verify DNS CNAME record points to: $SWA_HOSTNAME"
echo "4. Once certificate is provisioned, access your app at:"
echo "   https://$CUSTOM_DOMAIN"
echo ""

