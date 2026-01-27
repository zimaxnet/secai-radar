#!/bin/bash
# Script to add custom domains with managed certificates to Azure Container App
# Domains: api.secairadar.cloud and registry.secairadar.com

set -e

# Configuration
CONTAINER_APP_NAME="secai-radar-public-api"
RESOURCE_GROUP="secai-radar-rg"
ENVIRONMENT_NAME="secai-radar-dev-env"
DOMAIN_1="api.secairadar.cloud"
DOMAIN_2="registry.secairadar.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Add Custom Domains to Container App"
echo "=========================================="
echo ""
echo "Container App: $CONTAINER_APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Environment: $ENVIRONMENT_NAME"
echo ""

# Check Azure login
if ! az account show &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Please run: az login"
    exit 1
fi

echo -e "${GREEN}✅ Logged in to Azure${NC}"
echo ""

# Get current Container App details
echo "Getting Container App details..."
FQDN=$(az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null)

if [ -z "$FQDN" ]; then
    echo -e "${RED}❌ Container App not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Container App${NC}"
echo "   Default FQDN: $FQDN"
echo ""

# Get current custom domains
echo "Checking existing custom domains..."
CURRENT_HOSTNAMES=$(az containerapp hostname list \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[].name" -o tsv 2>/dev/null || echo "")

if [ -n "$CURRENT_HOSTNAMES" ]; then
    echo "   Existing domains:"
    echo "$CURRENT_HOSTNAMES" | while read -r domain; do
        BINDING=$(az containerapp hostname list \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --query "[?name=='$domain'].bindingType" -o tsv 2>/dev/null || echo "Unknown")
        echo "     - $domain (binding: $BINDING)"
    done
else
    echo "   No custom domains configured yet"
fi
echo ""

# Function to check DNS
check_dns() {
    local domain=$1
    local target=$2
    echo "   Checking DNS for $domain..."
    
    # Try to resolve CNAME
    CNAME_RESULT=$(dig +short "$domain" CNAME 2>/dev/null || echo "")
    if [ -n "$CNAME_RESULT" ]; then
        if echo "$CNAME_RESULT" | grep -q "$target"; then
            echo -e "   ${GREEN}✅ DNS CNAME correctly points to $target${NC}"
            return 0
        else
            echo -e "   ${YELLOW}⚠️  DNS CNAME points to: $CNAME_RESULT${NC}"
            echo "   Expected: $target"
            return 1
        fi
    fi
    
    # Try A record
    A_RESULT=$(dig +short "$domain" A 2>/dev/null || echo "")
    if [ -n "$A_RESULT" ]; then
        echo -e "   ${YELLOW}⚠️  Found A record: $A_RESULT${NC}"
        echo "   Note: CNAME is required for Container Apps"
        return 1
    fi
    
    echo -e "   ${YELLOW}⚠️  No DNS record found (may still be propagating)${NC}"
    return 1
}

# Function to add a custom domain
add_custom_domain() {
    local domain=$1
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Processing domain: $domain${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Check if domain already exists
    DOMAIN_EXISTS=$(echo "$CURRENT_HOSTNAMES" | grep -q "^${domain}$" && echo "yes" || echo "no")
    
    if [ "$DOMAIN_EXISTS" = "yes" ]; then
        BINDING=$(az containerapp hostname list \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --query "[?name=='$domain'].bindingType" -o tsv 2>/dev/null || echo "")
        
        if [ "$BINDING" = "SniEnabled" ]; then
            echo -e "${GREEN}✅ Domain $domain is already configured with certificate${NC}"
            CERT_ID=$(az containerapp hostname list \
                --name "$CONTAINER_APP_NAME" \
                --resource-group "$RESOURCE_GROUP" \
                --query "[?name=='$domain'].certificateId" -o tsv 2>/dev/null || echo "")
            if [ -n "$CERT_ID" ]; then
                echo "   Certificate ID: $CERT_ID"
            fi
            return 0
        else
            echo "   Domain exists but binding is: $BINDING"
            echo "   Attempting to bind with managed certificate..."
        fi
    else
        # Check DNS first
        if ! check_dns "$domain" "$FQDN"; then
            echo ""
            echo -e "${YELLOW}⚠️  DNS not configured yet${NC}"
            echo "   Please configure DNS first:"
            echo "   Type: CNAME"
            echo "   Name: $domain"
            echo "   Value: $FQDN"
            echo "   TTL: 3600"
            echo ""
            read -p "   Continue anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "   Skipping $domain"
                return 1
            fi
        fi
        
        # Add new custom domain
        echo "   Adding custom domain..."
        if az containerapp hostname add \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --hostname "$domain" 2>/dev/null; then
            echo -e "${GREEN}✅ Domain $domain added${NC}"
        else
            echo -e "${RED}❌ Failed to add domain $domain${NC}"
            return 1
        fi
    fi
    
    # Bind with managed certificate
    echo "   Binding with managed certificate..."
    if az containerapp hostname bind \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --hostname "$domain" \
        --environment "$ENVIRONMENT_NAME" \
        --validation-method "HTTP" 2>/dev/null; then
        echo -e "${GREEN}✅ Certificate binding initiated for $domain${NC}"
        echo "   Azure will provision the managed certificate (5-15 minutes)"
        return 0
    else
        echo -e "${YELLOW}⚠️  Certificate binding may require DNS to be configured first${NC}"
        echo "   If DNS is configured, wait a few minutes and try again"
        return 1
    fi
}

# Process domains
echo "=========================================="
echo "Adding/Updating Custom Domains"
echo "=========================================="

add_custom_domain "$DOMAIN_1"
add_custom_domain "$DOMAIN_2"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""

# Get updated custom domains
echo "Current custom domains:"
az containerapp hostname list \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    -o table 2>/dev/null || echo "   Error retrieving domains"

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. DNS Configuration (if not done):"
echo "   - Add CNAME for $DOMAIN_1 → $FQDN"
echo "   - Add CNAME for $DOMAIN_2 → $FQDN"
echo ""
echo "2. Wait for certificate provisioning (5-15 minutes)"
echo "   Azure will automatically provision managed certificates"
echo "   once DNS is configured and propagated"
echo ""
echo "3. Verify domains:"
echo "   az containerapp hostname list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "4. Test domains:"
echo "   curl https://$DOMAIN_1/api/v1/public/health"
echo "   curl https://$DOMAIN_2/api/v1/public/health"
echo ""
