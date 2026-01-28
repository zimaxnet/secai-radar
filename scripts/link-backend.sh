#!/bin/bash
set -e

# Link the Container App backend to the Static Web App
# This ensures /api/* requests are routed to the Container App

BACKEND_ID="/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.App/containerapps/secai-radar-public-api"

echo "Linking secai-radar-public-api to secai-radar SWA..."

az staticwebapp backends link \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --backend-resource-id "$BACKEND_ID" \
  --backend-region centralus

echo "✅ Backend linked successfully!"
