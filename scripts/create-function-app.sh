#!/bin/bash

# Script to create Azure Function App for SecAI Radar API
# This separates the API from the Static Web App for better reliability

set -e

# Configuration
RG="secai-radar-rg"
LOC="centralus"
FUNCTION_APP_NAME="secai-radar-api"
STORAGE_ACCOUNT="secairadar587d35"
PYTHON_VERSION="3.12"

echo "Creating Azure Function App resources..."

# Get storage account connection string
STORAGE_CONN=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RG" \
  --query connectionString \
  --output tsv)

if [ -z "$STORAGE_CONN" ]; then
  echo "Error: Could not retrieve storage account connection string"
  exit 1
fi

# Create Function App on Consumption plan (serverless)
# For Consumption plan, we don't create a separate App Service Plan
echo "Creating Function App on Consumption plan..."
az functionapp create \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --storage-account "$STORAGE_ACCOUNT" \
  --consumption-plan-location "$LOC" \
  --runtime python \
  --runtime-version "$PYTHON_VERSION" \
  --functions-version 4 \
  --os-type Linux || echo "Function App may already exist"

# Configure app settings
echo "Configuring application settings..."
az functionapp config appsettings set \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --settings \
    "AzureWebJobsStorage=$STORAGE_CONN" \
    "TABLES_CONN=$STORAGE_CONN" \
    "BLOBS_CONN=$STORAGE_CONN" \
    "BLOB_CONTAINER=assessments" \
    "TENANT_ID=NICO" \
    "FUNCTIONS_EXTENSION_VERSION=~4" \
    "FUNCTIONS_WORKER_RUNTIME=python" \
    "PYTHON_VERSION=$PYTHON_VERSION"

# Configure CORS to allow Static Web App
echo "Configuring CORS..."
az functionapp cors add \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --allowed-origins \
    "https://secai-radar.zimax.net" \
    "https://purple-moss-0942f9e10.3.azurestaticapps.net" \
    "http://localhost:5173" \
    "http://localhost:3000"

# Enable managed identity (optional, for future use)
echo "Enabling system-assigned managed identity..."
az functionapp identity assign \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" || echo "Identity may already be assigned"

# Get Function App URL
FUNCTION_URL=$(az functionapp show \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RG" \
  --query defaultHostName \
  --output tsv)

echo ""
echo "✅ Function App created successfully!"
echo "Function App URL: https://$FUNCTION_URL"
echo ""
echo "Next steps:"
echo "1. Get the publish profile for deployment:"
echo "   az functionapp deployment list-publishing-profiles --name $FUNCTION_APP_NAME --resource-group $RG"
echo ""
echo "2. Add the publish profile to GitHub Secrets as AZURE_FUNCTIONAPP_PUBLISH_PROFILE"
echo ""
echo "3. Update web/src/api.ts to use: VITE_API_BASE=https://$FUNCTION_URL/api"
echo ""

