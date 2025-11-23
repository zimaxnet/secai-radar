# SecAI Radar Infrastructure as Code

This folder provides the baseline Bicep templates for provisioning the SecAI Radar stack in a cost-conscious, reproducible way.

## Structure
- `main.bicep` – core deployment (storage, function plan/app, application insights, queue).
- `modules/` – reusable building blocks (e.g., Static Web App, budgets, Key Vault secrets) – coming soon.
- `parameters/` – environment-specific parameter files (`dev`, `preprod`, `prod`).

## Prerequisites
- Azure CLI 2.58+
- Bicep CLI 0.25+ (`az bicep install`)
- Contributor rights on the target subscription
- Access to Azure OpenAI resource (for deployment validation)

## Usage
```bash
# Validate changes
az deployment sub what-if \
  --name secai-radar-dev \
  --location eastus2 \
  --template-file main.bicep \
  --parameters @parameters/dev.bicepparam

# Deploy
az deployment sub create \
  --name secai-radar-dev \
  --location eastus2 \
  --template-file main.bicep \
  --parameters @parameters/dev.bicepparam
```

## Cost Guidance
- Default plan uses **Elastic Premium EP1** with `preWarmedInstanceCount` set to `0` to minimize idle spend.
- Storage queues and tables incur pennies per month; lifecycle rules move stale evidence to Cool tier automatically.
- Application Insights is configured with sampling (5%) and a `$1/day` cap.
- Azure OpenAI settings are parameterized so lower-cost deployments (e.g., GPT‑3.5) can be selected per environment.

## Next Work Items
- Add `modules/staticWebApp.bicep` for reproducible SWA deployment.
- Add `modules/budget.bicep` to enforce cost alerts.
- Integrate with GitHub Actions OIDC workflow for automated rollouts.
