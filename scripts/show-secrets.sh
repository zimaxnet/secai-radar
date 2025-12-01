#!/bin/bash

# Script to display secrets for easy copying to GitHub

echo "📋 GITHUB SECRETS TO ADD"
echo "========================"
echo ""

echo "1️⃣ AZURE_STATIC_WEB_APPS_API_TOKEN"
echo "-----------------------------------"
echo ""
az staticwebapp secrets list \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --query properties.apiKey \
  --output tsv
echo ""
echo ""

echo "2️⃣ AZURE_FUNCTIONAPP_PUBLISH_PROFILE"
echo "--------------------------------------"
echo "(Full XML content - copy everything below)"
echo ""
cat function-app-publish-profile.xml
echo ""
echo ""

echo "3️⃣ VITE_API_BASE (Optional but Recommended)"
echo "----------------------------------------------"
echo "https://secai-radar-api.azurewebsites.net/api"
echo ""
echo ""

echo "📝 INSTRUCTIONS:"
echo "1. Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Copy each value above for the corresponding secret name"
echo ""

