#!/usr/bin/env bash
# Create GHCR_PAT from gh and delete ACR (use ghcr.io, save ~$5/mo).
# Run from repo root or scripts/.
#
# Usage:
#   ./scripts/setup-ghcr-and-remove-acr.sh              # Use current gh token as GHCR_PAT, delete ACR
#   ./scripts/setup-ghcr-and-remove-acr.sh --new-token  # Open browser to create a new PAT, then set GHCR_PAT
#   ./scripts/setup-ghcr-and-remove-acr.sh --skip-acr   # Only set GHCR_PAT (do not delete ACR)

set -e

SKIP_ACR=
NEW_TOKEN=
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-acr)   SKIP_ACR=1; shift ;;
    --new-token)  NEW_TOKEN=1; shift ;;
    *) echo "Usage: $0 [--new-token] [--skip-acr]"; exit 1 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- 1) Set GHCR_PAT ---
if [[ -n "$NEW_TOKEN" ]]; then
  echo "Opening GitHub token creation (scope: read:packages). Create a token, then paste it below."
  if command -v open &>/dev/null; then
    open "https://github.com/settings/tokens/new?description=GHCR-SecAI-pull&scopes=read:packages"
  else
    echo "Open: https://github.com/settings/tokens/new?description=GHCR-SecAI-pull&scopes=read:packages"
  fi
  read -rs TOKEN
  echo
  if [[ -z "$TOKEN" ]]; then echo "No token entered."; exit 1; fi
  echo "$TOKEN" | gh secret set GHCR_PAT
  echo "GHCR_PAT set from new token."
else
  TOKEN=$(gh auth token)
  if [[ -z "$TOKEN" ]]; then echo "Run: gh auth login"; exit 1; fi
  echo "$TOKEN" | gh secret set GHCR_PAT
  echo "GHCR_PAT set from current gh token (ensure it has read:packages or write:packages)."
fi

# --- 2) Delete ACR ---
if [[ -n "$SKIP_ACR" ]]; then
  echo "Skipping ACR deletion (--skip-acr)."
  exit 0
fi

RG="${AZURE_RESOURCE_GROUP:-secai-radar-rg}"
if ! command -v az &>/dev/null; then
  echo "az not found; skipping ACR delete. Delete manually: az acr delete -g $RG -n <acr-name> --yes"
  exit 0
fi

ACRS=$(az acr list --resource-group "$RG" -o tsv --query "[].name" 2>/dev/null || true)
if [[ -z "$ACRS" ]]; then
  echo "No ACRs found in $RG."
  exit 0
fi

for name in $ACRS; do
  echo "Deleting ACR: $name"
  az acr delete --name "$name" --resource-group "$RG" --yes
done
echo "Done. GHCR_PAT is set; ACR(s) removed. Redeploy with the Deploy-to-Staging workflow (images from ghcr.io)."
