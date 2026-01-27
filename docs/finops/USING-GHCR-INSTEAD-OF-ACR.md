# Using GitHub Container Registry (ghcr.io) Instead of ACR

You **do not need Azure Container Registry** for SecAI. GitHub provides **GitHub Container Registry (ghcr.io)**, and Azure Container Apps can pull images from it. Using ghcr.io saves **~\$5/month** (ACR Basic) and one Azure resource.

## How it works

1. **Build & push in GitHub Actions**  
   The workflow builds the images and pushes them to `ghcr.io/<org>/secai-radar-public-api:latest` and `ghcr.io/<org>/secai-radar-registry-api:latest` using `GITHUB_TOKEN` (no extra token needed for push).

2. **Container Apps pull from ghcr.io**  
   When creating or updating the Container Apps, the workflow registers ghcr.io as the image source and uses a **GitHub PAT with `read:packages`** so Azure can pull the images. That token is stored as a repo secret (e.g. `GHCR_PAT`) and passed only to the Azure CLI steps.

## Required setup

- **One repo secret:** `GHCR_PAT` — a GitHub Personal Access Token with **`read:packages`** so Container Apps can pull from ghcr.io.
  - **Quick (use current gh token):** from the repo root run  
    `./scripts/setup-ghcr-and-remove-acr.sh`  
    This sets `GHCR_PAT` from `gh auth token` and deletes the SecAI ACR in `secai-radar-rg`.
  - **Dedicated token:** run  
    `./scripts/setup-ghcr-and-remove-acr.sh --new-token`  
    to open the token-creation page (read:packages), then paste the new token when prompted.

- **No ACR:**  
  The same script deletes ACR in the resource group. For new Bicep deployments, use `deployContainerRegistry: false` so the template does not create an ACR.

## Cost impact

| Before (ACR) | After (ghcr.io) |
|--------------|------------------|
| ACR Basic ~\$5/month | \$0 (ghcr.io is free for public images; for private, included in GitHub plan) |

See [SECAI-INFRA-COST-IMPLICATIONS.md](./SECAI-INFRA-COST-IMPLICATIONS.md) for updated totals when ACR is dropped.
