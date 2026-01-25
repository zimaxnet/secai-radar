#!/bin/bash
# Update Azure Static Web App configuration for monorepo structure

set -e

RESOURCE_GROUP="secai-radar-rg"
STATIC_WEB_APP="secai-radar"

echo "Updating Azure Static Web App configuration..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Static Web App: $STATIC_WEB_APP"

# Update build configuration
az staticwebapp update \
  --name "$STATIC_WEB_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --app-location "apps/public-web" \
  --output-location "dist" \
  --api-location "" \
  --output json

echo ""
echo "✅ Static Web App configuration updated!"
echo ""
echo "New configuration:"
echo "  - App location: apps/public-web"
echo "  - Output location: dist"
echo "  - API location: (empty - separate Container App)"
echo ""
echo "Next steps:"
echo "  1. Verify in Azure Portal: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$STATIC_WEB_APP/staticsite"
echo "  2. Trigger a new deployment to test the configuration"
echo "  3. Check deployment logs if issues occur"
