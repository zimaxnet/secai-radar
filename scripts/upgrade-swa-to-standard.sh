#!/bin/bash
# Upgrade Azure Static Web App to Standard tier (required before linking backends/containers)
# Run from repo root; requires 'az' and login.

set -e

RG="${SECAI_RG:-secai-radar-rg}"
SWA_NAME="${SECAI_SWA:-secai-radar}"

echo "Upgrading Static Web App to Standard..."
echo "  Resource Group: $RG"
echo "  Static Web App: $SWA_NAME"
echo ""

az staticwebapp update \
  --name "$SWA_NAME" \
  --resource-group "$RG" \
  --sku Standard

echo ""
echo "Done. Verify with:"
echo "  az staticwebapp show -n $SWA_NAME -g $RG --query sku -o tsv"
echo ""
echo "Standard enables: linked backends, staging environments, custom domains, more quota."
echo "Next: create/link Container Apps or other backends in the Azure Portal or via IaC."
