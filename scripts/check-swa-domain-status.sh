#!/bin/bash
# Script to check Azure Static Web App custom domain validation and certificate status

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
echo "Static Web App Domain Status Check"
echo "=========================================="
echo ""
echo "Domain: $CUSTOM_DOMAIN"
echo "Time: $(date)"
echo ""

# Check Azure login
if ! az account show &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    exit 1
fi

# Get domain status
echo "Checking domain status..."
DOMAIN_INFO=$(az staticwebapp hostname show \
    --name "$SWA_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --hostname "$CUSTOM_DOMAIN" \
    -o json 2>/dev/null)

if [ -z "$DOMAIN_INFO" ] || [ "$DOMAIN_INFO" == "null" ]; then
    echo -e "${RED}❌ Domain not found in Static Web App${NC}"
    exit 1
fi

STATUS=$(echo "$DOMAIN_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'Unknown'))" 2>/dev/null || echo "Unknown")
VALIDATION_STATE=$(echo "$DOMAIN_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('validationState', 'Unknown'))" 2>/dev/null || echo "Unknown")
CREATED_ON=$(echo "$DOMAIN_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('createdOn', 'Unknown'))" 2>/dev/null || echo "Unknown")

echo "=========================================="
echo "Domain Status"
echo "=========================================="
echo ""

# Status indicators
case "$STATUS" in
    "Ready")
        echo -e "${GREEN}✅ Status: Ready${NC}"
        ;;
    "Validating")
        echo -e "${YELLOW}⏳ Status: Validating${NC}"
        ;;
    "Failed")
        echo -e "${RED}❌ Status: Failed${NC}"
        ERROR_MSG=$(echo "$DOMAIN_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('errorMessage', 'No error message'))" 2>/dev/null || echo "Unknown error")
        echo "   Error: $ERROR_MSG"
        ;;
    *)
        echo -e "${BLUE}ℹ️  Status: $STATUS${NC}"
        ;;
esac

# Validation state
case "$VALIDATION_STATE" in
    "Valid"|"Approved")
        echo -e "${GREEN}✅ Validation: $VALIDATION_STATE${NC}"
        ;;
    "Pending"|"Validating")
        echo -e "${YELLOW}⏳ Validation: $VALIDATION_STATE${NC}"
        ;;
    "Invalid"|"Failed")
        echo -e "${RED}❌ Validation: $VALIDATION_STATE${NC}"
        ;;
    *)
        echo -e "${BLUE}ℹ️  Validation: $VALIDATION_STATE${NC}"
        ;;
esac

echo "   Created: $CREATED_ON"
echo ""

# Check DNS resolution
echo "=========================================="
echo "DNS Resolution Check"
echo "=========================================="
echo ""

# Check TXT record
TXT_RECORD=$(dig +short "$CUSTOM_DOMAIN" TXT 2>/dev/null | grep -o "_7rdm8xrwpltbnbaj5691my0c39x7afd" || echo "")
if [ -n "$TXT_RECORD" ]; then
    echo -e "${GREEN}✅ TXT validation record found${NC}"
else
    echo -e "${YELLOW}⚠️  TXT validation record not found (may still be propagating)${NC}"
fi

# Check CNAME/ALIAS resolution
CNAME_RESULT=$(dig +short "$CUSTOM_DOMAIN" CNAME 2>/dev/null || echo "")
A_RECORD=$(dig +short "$CUSTOM_DOMAIN" A 2>/dev/null | head -1 || echo "")

SWA_HOSTNAME=$(az staticwebapp show \
    --name "$SWA_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "defaultHostname" -o tsv)

if [ -n "$CNAME_RESULT" ]; then
    if echo "$CNAME_RESULT" | grep -q "$SWA_HOSTNAME"; then
        echo -e "${GREEN}✅ CNAME correctly points to SWA${NC}"
        echo "   Resolved to: $CNAME_RESULT"
    else
        echo -e "${YELLOW}⚠️  CNAME found but points elsewhere${NC}"
        echo "   Found: $CNAME_RESULT"
        echo "   Expected: $SWA_HOSTNAME"
    fi
elif [ -n "$A_RECORD" ]; then
    echo -e "${GREEN}✅ A record found (ALIAS/ANAME working)${NC}"
    echo "   Resolved to: $A_RECORD"
else
    echo -e "${YELLOW}⚠️  DNS not resolving yet (may still be propagating)${NC}"
fi

echo ""

# Timeline estimate
if [ "$STATUS" == "Validating" ] || [ "$VALIDATION_STATE" == "Pending" ]; then
    echo "=========================================="
    echo "Timeline Estimate"
    echo "=========================================="
    echo ""
    echo "Current Phase: DNS Validation"
    echo ""
    echo "Expected Timeline:"
    echo "  - DNS Propagation: 1-24 hours (usually 1-2 hours)"
    echo "  - Azure Validation: Automatic after DNS propagates"
    echo "  - Certificate Provisioning: 24-48 hours after validation"
    echo ""
    echo "Total Estimated Time: 25-72 hours from DNS record creation"
    echo ""
    echo "Next Check: Run this script again in a few hours"
    echo ""
elif [ "$STATUS" == "Ready" ] && [ "$VALIDATION_STATE" == "Valid" ]; then
    echo "=========================================="
    echo "✅ Domain is Ready!"
    echo "=========================================="
    echo ""
    echo "Your domain should be accessible at:"
    echo "  https://$CUSTOM_DOMAIN"
    echo ""
    echo "Certificate provisioning may still be in progress"
    echo "Check again in 24-48 hours if HTTPS doesn't work yet"
    echo ""
fi

# Check if domain is set as default
echo "=========================================="
echo "Default Domain Check"
echo "=========================================="
echo ""

DEFAULT_HOSTNAME=$(az staticwebapp show \
    --name "$SWA_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "defaultHostname" -o tsv)

if [ "$DEFAULT_HOSTNAME" == "$CUSTOM_DOMAIN" ]; then
    echo -e "${GREEN}✅ Custom domain is set as default${NC}"
else
    echo -e "${BLUE}ℹ️  Default hostname: $DEFAULT_HOSTNAME${NC}"
    echo "   Custom domain: $CUSTOM_DOMAIN"
    echo "   (Both should work once certificate is provisioned)"
fi

echo ""
echo "=========================================="
echo "Quick Status"
echo "=========================================="
echo ""
echo "Domain: $CUSTOM_DOMAIN"
echo "Status: $STATUS"
echo "Validation: $VALIDATION_STATE"
echo ""
echo "Azure Portal:"
echo "https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$SWA_NAME/customDomains"
echo ""

