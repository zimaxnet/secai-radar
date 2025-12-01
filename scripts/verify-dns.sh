#!/bin/bash
# Script to verify DNS configuration in Azure for SecAI Radar

# Configuration
DOMAIN="secai-radar.zimax.net"
DNS_ZONE="zimax.net"
SUBSCRIPTION_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"

echo "=========================================="
echo "SecAI Radar DNS Verification"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "DNS Zone: $DNS_ZONE"
echo ""

# Check if logged in to Azure
echo "Checking Azure login..."
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "✅ Logged in to Azure"
echo ""

# Set subscription
echo "Setting subscription..."
az account set --subscription "$SUBSCRIPTION_ID"
echo "✅ Subscription set to: $SUBSCRIPTION_ID"
echo ""

# Check for DNS zone
echo "Checking for DNS zone: $DNS_ZONE"
DNS_ZONE_EXISTS=$(az network dns zone list --query "[?name=='$DNS_ZONE'].name" -o tsv)

if [ -z "$DNS_ZONE_EXISTS" ]; then
    echo "⚠️  DNS zone '$DNS_ZONE' not found in Azure"
    echo "   You may need to create it or use external DNS provider"
    echo ""
else
    echo "✅ DNS zone '$DNS_ZONE' found in Azure"
    
    # List resource groups containing DNS zone
    RG=$(az network dns zone list --query "[?name=='$DNS_ZONE'].resourceGroup" -o tsv | head -1)
    echo "   Resource Group: $RG"
    echo ""
fi

# Check for CNAME record
echo "Checking for CNAME record: secai-radar"
if [ -n "$DNS_ZONE_EXISTS" ]; then
    CNAME_EXISTS=$(az network dns record-set cname list \
        --resource-group "$RG" \
        --zone-name "$DNS_ZONE" \
        --query "[?name=='secai-radar'].name" -o tsv)
    
    if [ -z "$CNAME_EXISTS" ]; then
        echo "❌ CNAME record 'secai-radar' not found in DNS zone"
        echo ""
        echo "To create the CNAME record, run:"
        echo "  az network dns record-set cname create \\"
        echo "    --resource-group $RG \\"
        echo "    --zone-name $DNS_ZONE \\"
        echo "    --name secai-radar \\"
        echo "    --cname your-username.github.io"
        echo ""
        echo "Replace 'your-username' with your actual GitHub username"
    else
        echo "✅ CNAME record 'secai-radar' found"
        
        # Get CNAME value
        CNAME_VALUE=$(az network dns record-set cname show \
            --resource-group "$RG" \
            --zone-name "$DNS_ZONE" \
            --name "secai-radar" \
            --query "cnameRecord.cname" -o tsv)
        
        echo "   CNAME Value: $CNAME_VALUE"
        echo ""
        
        # Verify CNAME value
        if [[ "$CNAME_VALUE" == *".github.io" ]]; then
            echo "✅ CNAME points to GitHub Pages (correct)"
        else
            echo "⚠️  CNAME does not point to GitHub Pages"
            echo "   Expected: *.github.io"
            echo "   Found: $CNAME_VALUE"
        fi
    fi
else
    echo "⚠️  Cannot check CNAME record - DNS zone not found in Azure"
fi

echo ""
echo "=========================================="
echo "DNS Resolution Check"
echo "=========================================="
echo ""

# Check DNS resolution
echo "Checking DNS resolution for $DOMAIN..."
if command -v dig &> /dev/null; then
    echo ""
    echo "Using dig:"
    dig +short "$DOMAIN" CNAME
    echo ""
elif command -v nslookup &> /dev/null; then
    echo ""
    echo "Using nslookup:"
    nslookup -type=CNAME "$DOMAIN"
    echo ""
else
    echo "⚠️  dig or nslookup not available for DNS resolution check"
fi

# Check GitHub Pages DNS
echo "Checking GitHub Pages DNS..."
if command -v dig &> /dev/null; then
    GITHUB_DNS=$(dig +short "$DOMAIN" CNAME | head -1)
    if [[ "$GITHUB_DNS" == *".github.io" ]]; then
        echo "✅ DNS resolves to GitHub Pages"
        echo "   Resolved to: $GITHUB_DNS"
    else
        echo "⚠️  DNS does not resolve to GitHub Pages"
        echo "   Resolved to: $GITHUB_DNS"
    fi
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Main App URL: https://$DOMAIN"
echo "Wiki URL: https://$DOMAIN/wiki"
echo ""
echo "Expected DNS Configuration:"
echo "  Type: CNAME"
echo "  Name: secai-radar"
echo "  Value: your-username.github.io"
echo "  TTL: 3600"
echo ""
echo "Note: Both app and wiki use the same domain and DNS record"
echo ""

