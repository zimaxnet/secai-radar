#!/bin/bash
# Script to configure authentication for Azure Static Web App
# This uses the Azure REST API since CLI doesn't support auth configuration

SWA_NAME="secai-radar"
RG="secai-radar-rg"
SUBSCRIPTION_ID="23f4e2c5-0667-4514-8e2e-f02ca7880c95"
TENANT_ID="8838531d-55dd-4018-8341-77705f4845f4"
APP_ID="1cd314e6-933a-4bf9-b889-ffe04a815b98"

echo "Getting access token..."
ACCESS_TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

ENDPOINT="https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RG}/providers/Microsoft.Web/staticSites/${SWA_NAME}/config/authsettingsV2?api-version=2022-03-01"

echo "Configuring authentication..."
curl -X PUT "$ENDPOINT" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "globalValidation": {
        "requireAuthentication": false,
        "unauthenticatedClientAction": "RedirectToLoginPage"
      },
      "identityProviders": {
        "azureActiveDirectory": {
          "enabled": true,
          "registration": {
            "openIdIssuer": "https://login.microsoftonline.com/'${TENANT_ID}'/v2.0",
            "clientIdSettingName": "MICROSOFT_PROVIDER_AUTHENTICATION_SECRET",
            "clientSecretSettingName": "MICROSOFT_PROVIDER_AUTHENTICATION_SECRET"
          },
          "validation": {
            "jwtClaimChecks": {},
            "allowedAudiences": []
          }
        }
      },
      "login": {
        "routes": {
          "logoutEndpoint": "/.auth/logout"
        }
      }
    }
  }'

echo -e "\nAuthentication configuration sent. Check Azure Portal for status."

