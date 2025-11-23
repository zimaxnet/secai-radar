#!/bin/bash

# Script to get Azure credentials for GitHub Secrets
# This will output the JSON that should be added to GitHub Secrets as AZURE_CREDENTIALS

echo "Getting Azure credentials for GitHub Actions..."
echo ""

# Check if service principal exists
SP_ID=$(az ad sp list --display-name "secai-radar-github-actions" --query "[0].appId" --output tsv 2>/dev/null)

if [ -n "$SP_ID" ] && [ "$SP_ID" != "None" ]; then
  echo "Service principal exists (ID: $SP_ID)."
  echo "Creating new password and outputting credentials..."
  echo ""
  # Reset password and get new credentials
  NEW_PASSWORD=$(az ad sp credential reset --id "$SP_ID" --query password --output tsv)
  
  # Get service principal details
  SUB_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"
  TENANT_ID=$(az account show --query tenantId --output tsv)
  
  # Output in SDK auth format
  cat <<EOF
{
  "clientId": "$SP_ID",
  "clientSecret": "$NEW_PASSWORD",
  "subscriptionId": "$SUB_ID",
  "tenantId": "$TENANT_ID",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
EOF
else
  echo "Creating new service principal..."
  echo ""
  az ad sp create-for-rbac \
    --name "secai-radar-github-actions" \
    --role contributor \
    --scopes /subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg \
    --sdk-auth --output json
fi

echo ""
echo ""
echo "✅ Copy the JSON output above"
echo "   Add it to GitHub Secrets as: AZURE_CREDENTIALS"
echo ""

