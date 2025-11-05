#!/bin/bash

# Complete Deployment Script for SecAI Radar
# This script automates what can be done and provides instructions for manual steps

set -e

echo "🚀 SecAI Radar - Complete Deployment Setup"
echo "=========================================="
echo ""

# Configuration
RG="secai-radar-rg"
SWA_NAME="secai-radar"
FUNCTION_APP_NAME="secai-radar-api"
GITHUB_REPO="https://github.com/zimaxnet/secai-radar"
GITHUB_BRANCH="main"

echo "✅ Step 1: Checking Static Web App status..."
SWA_STATUS=$(az staticwebapp show \
  --name "$SWA_NAME" \
  --resource-group "$RG" \
  --query "{name:name, defaultHostname:defaultHostname, repositoryUrl:repositoryUrl}" \
  --output json)

echo "$SWA_STATUS" | jq -r '.'
REPO_URL=$(echo "$SWA_STATUS" | jq -r '.repositoryUrl // empty')

if [ -z "$REPO_URL" ]; then
  echo ""
  echo "⚠️  Static Web App is NOT connected to GitHub"
  echo ""
  echo "📋 MANUAL STEP REQUIRED:"
  echo "   1. Go to: https://portal.azure.com"
  echo "   2. Navigate to: Static Web App → $SWA_NAME"
  echo "   3. Click 'Deployment' in left menu"
  echo "   4. Click 'Add deployment source' or 'Edit'"
  echo "   5. Select:"
  echo "      - Source: GitHub"
  echo "      - Organization: zimaxnet"
  echo "      - Repository: secai-radar"
  echo "      - Branch: main"
  echo "      - Build Presets: Custom"
  echo "   6. Configure:"
  echo "      - App location: /web"
  echo "      - Output location: dist"
  echo "      - API location: (leave empty - API is separate)"
  echo "   7. Click 'Save'"
  echo ""
  echo "   This will trigger the first deployment automatically!"
  echo ""
else
  echo "✅ Static Web App is connected to GitHub: $REPO_URL"
fi

echo ""
echo "✅ Step 2: Getting deployment token..."
SWA_TOKEN=$(az staticwebapp secrets list \
  --name "$SWA_NAME" \
  --resource-group "$RG" \
  --query properties.apiKey \
  --output tsv)

if [ -n "$SWA_TOKEN" ]; then
  echo "✅ Deployment token retrieved"
  echo ""
  echo "📋 ADD TO GITHUB SECRETS:"
  echo "   1. Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions"
  echo "   2. If not exists, add secret:"
  echo "      - Name: AZURE_STATIC_WEB_APPS_API_TOKEN"
  echo "      - Value: $SWA_TOKEN"
  echo ""
else
  echo "⚠️  Could not retrieve deployment token"
fi

echo ""
echo "✅ Step 3: Checking Function App publish profile..."
if [ -f "function-app-publish-profile.xml" ]; then
  echo "✅ Publish profile file exists"
  PUBLISH_PROFILE=$(cat function-app-publish-profile.xml)
  echo ""
  echo "📋 ADD TO GITHUB SECRETS:"
  echo "   1. Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions"
  echo "   2. Add secret:"
  echo "      - Name: AZURE_FUNCTIONAPP_PUBLISH_PROFILE"
  echo "      - Value: (Copy entire content of function-app-publish-profile.xml)"
  echo ""
  echo "   To view the file:"
  echo "   cat function-app-publish-profile.xml"
  echo ""
else
  echo "⚠️  Publish profile file not found"
  echo "   Generating..."
  az functionapp deployment list-publishing-profiles \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RG" \
    --xml > function-app-publish-profile.xml
  echo "✅ Publish profile saved to: function-app-publish-profile.xml"
fi

echo ""
echo "✅ Step 4: Getting Function App URL..."
FUNCTION_URL=$(az functionapp show \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --query defaultHostName \
  --output tsv)

if [ -n "$FUNCTION_URL" ]; then
  API_BASE_URL="https://$FUNCTION_URL/api"
  echo "✅ Function App URL: https://$FUNCTION_URL"
  echo "✅ API Base URL: $API_BASE_URL"
  echo ""
  echo "📋 ADD TO GITHUB SECRETS (Optional but Recommended):"
  echo "   1. Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions"
  echo "   2. Add secret:"
  echo "      - Name: VITE_API_BASE"
  echo "      - Value: $API_BASE_URL"
  echo ""
  echo "   OR set in Azure Static Web App settings:"
  echo "   Azure Portal → Static Web App → $SWA_NAME → Configuration"
  echo "   Add: VITE_API_BASE = $API_BASE_URL"
  echo ""
else
  echo "⚠️  Could not retrieve Function App URL"
fi

echo ""
echo "✅ Step 5: Checking deployment status..."
echo ""
echo "📊 CURRENT STATUS:"
echo "   Static Web App: https://$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RG" --query defaultHostname -o tsv)"
echo "   Function App: https://$FUNCTION_URL"
echo ""

echo "🧪 TEST COMMANDS:"
echo "   # Test Static Web App"
echo "   curl https://$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RG" --query defaultHostname -o tsv)"
echo ""
echo "   # Test Function App"
echo "   curl https://$FUNCTION_URL/api/domains"
echo ""

echo "📋 NEXT STEPS:"
echo "   1. ✅ Connect Static Web App to GitHub (see Step 1 above)"
echo "   2. ✅ Add GitHub Secrets (see Steps 2-4 above)"
echo "   3. ✅ Deploy Function App:"
echo "      - Go to: https://github.com/zimaxnet/secai-radar/actions"
echo "      - Select 'Deploy Azure Functions' workflow"
echo "      - Click 'Run workflow'"
echo "   4. ✅ Wait for Static Web App deployment (auto-triggers after Step 1)"
echo "   5. ✅ Test both apps"
echo ""

echo "🔐 AUTHENTICATION SETUP (After deployment works):"
echo "   1. Azure Portal → Static Web App → $SWA_NAME → Authentication"
echo "   2. Click 'Add identity provider'"
echo "   3. Select 'Microsoft (Azure AD / Entra ID)'"
echo "   4. Create new app registration or use existing"
echo "   5. Configure redirect URL for your domain"
echo ""

echo "🌐 DNS SETUP (After deployment works):"
echo "   1. Add CNAME record: secai-radar.zimax.net → $(az staticwebapp show --name "$SWA_NAME" --resource-group "$RG" --query defaultHostname -o tsv)"
echo "   2. Azure Portal → Static Web App → $SWA_NAME → Custom domains"
echo "   3. Add custom domain: secai-radar.zimax.net"
echo "   4. Verify DNS and wait for SSL certificate"
echo ""

echo "✅ Setup script complete!"
echo ""

