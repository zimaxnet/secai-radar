#!/bin/bash
# Script to check certificate status for Container App custom domains

set -e

# Configuration
CONTAINER_APP_NAME="secai-radar-public-api"
RESOURCE_GROUP="secai-radar-rg"
ENVIRONMENT_NAME="secai-radar-dev-env"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Certificate Status Check"
echo "=========================================="
echo ""
echo "Container App: $CONTAINER_APP_NAME"
echo "Environment: $ENVIRONMENT_NAME"
echo ""

# Check Azure login
if ! az account show &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Logged in to Azure${NC}"
echo ""

# Get Container App FQDN
FQDN=$(az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null)

echo "Default FQDN: $FQDN"
echo ""

# List custom domains
echo "=========================================="
echo "Custom Domains"
echo "=========================================="
echo ""

DOMAINS=$(az containerapp hostname list \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    -o json 2>/dev/null)

if [ -z "$DOMAINS" ] || [ "$DOMAINS" = "[]" ]; then
    echo "No custom domains configured"
else
    echo "$DOMAINS" | python3 -c "
import sys, json
domains = json.load(sys.stdin)
for domain in domains:
    name = domain.get('name', 'Unknown')
    binding = domain.get('bindingType', 'Unknown')
    cert_id = domain.get('certificateId', '')
    
    if binding == 'SniEnabled':
        print(f'✅ {name}')
        print(f'   Binding: {binding}')
        if cert_id:
            cert_name = cert_id.split('/')[-1]
            print(f'   Certificate: {cert_name}')
    elif binding == 'Disabled':
        print(f'⚠️  {name}')
        print(f'   Binding: {binding} (certificate pending)')
    else:
        print(f'❓ {name}')
        print(f'   Binding: {binding}')
    print()
"
fi

# Check managed certificates
echo "=========================================="
echo "Managed Certificates"
echo "=========================================="
echo ""

CERTIFICATES=$(az resource list \
    --resource-group "$RESOURCE_GROUP" \
    --resource-type "Microsoft.App/managedEnvironments/managedCertificates" \
    --query "[].{name:name, provisioningState:properties.provisioningState, subjectName:properties.subjectName}" \
    -o json 2>/dev/null || echo "[]")

if [ "$CERTIFICATES" = "[]" ] || [ -z "$CERTIFICATES" ]; then
    echo "No managed certificates found"
else
    echo "$CERTIFICATES" | python3 -c "
import sys, json
certs = json.load(sys.stdin)
for cert in certs:
    name = cert.get('name', 'Unknown')
    state = cert.get('provisioningState', 'Unknown')
    subject = cert.get('subjectName', 'Unknown')
    
    if state == 'Succeeded':
        print(f'✅ {name}')
        print(f'   Subject: {subject}')
        print(f'   Status: {state}')
    elif state == 'Pending':
        print(f'⏳ {name}')
        print(f'   Subject: {subject}')
        print(f'   Status: {state} (provisioning...)')
    elif state == 'Failed':
        print(f'❌ {name}')
        print(f'   Subject: {subject}')
        print(f'   Status: {state}')
    else:
        print(f'❓ {name}')
        print(f'   Subject: {subject}')
        print(f'   Status: {state}')
    print()
"
fi

# Check DNS for registry.secairadar.com
echo "=========================================="
echo "DNS Status"
echo "=========================================="
echo ""

if [ -n "$FQDN" ]; then
    echo "Checking DNS for registry.secairadar.com..."
    CNAME=$(dig +short registry.secairadar.com CNAME 2>/dev/null || echo "")
    
    if [ -n "$CNAME" ]; then
        if echo "$CNAME" | grep -q "$FQDN"; then
            echo -e "${GREEN}✅ DNS CNAME correctly configured${NC}"
            echo "   Points to: $CNAME"
        else
            echo -e "${YELLOW}⚠️  DNS CNAME points to: $CNAME${NC}"
            echo "   Expected: $FQDN"
        fi
    else
        echo -e "${YELLOW}⚠️  No CNAME record found${NC}"
        echo "   DNS may still be propagating"
    fi
fi

echo ""
echo "=========================================="
echo "Timeline & Next Steps"
echo "=========================================="
echo ""
echo "Certificate Provisioning Timeline:"
echo "  - DNS Propagation: 5-15 minutes"
echo "  - Certificate Validation: 5-15 minutes after DNS"
echo "  - Certificate Provisioning: 5-15 minutes after validation"
echo "  - Total: Usually 15-45 minutes (can take up to 2 hours)"
echo ""
echo "If certificate is pending:"
echo "  1. Verify DNS is correctly configured"
echo "  2. Wait 15-30 minutes and check again"
echo "  3. Check Azure Portal for detailed status"
echo ""
echo "Azure Portal:"
echo "  https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME"
echo ""
