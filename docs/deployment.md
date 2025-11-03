# Deployment Guide

## Azure Static Web Apps Setup

### Prerequisites
- Azure CLI installed and authenticated
- GitHub repository: `zimaxnet/secai-radar`
- Custom domain: `zimax.net/secai-radar`

### Step 1: Create Azure Resources

```bash
# Set variables
RG=secai-radar-rg
LOC=centralus
SA=secairadar$RANDOM

# Create resource group
az group create -n "$RG" -l "$LOC"

# Create storage account
az storage account create -n "$SA" -g "$RG" -l "$LOC" --sku Standard_LRS

# Get connection strings
az storage account show-connection-string -n "$SA" -g "$RG" --query connectionString -o tsv
```

### Step 2: Create Static Web App

In Azure Portal:
1. Go to **Static Web Apps**
2. Click **Create**
3. Fill in:
   - **Subscription**: Your subscription
   - **Resource Group**: `secai-radar-rg`
   - **Name**: `secai-radar` (or your preferred name)
   - **Plan type**: Free or Standard
   - **Region**: Central US
   - **Source**: GitHub
   - **Organization**: `zimaxnet`
   - **Repository**: `secai-radar`
   - **Branch**: `main`
   - **Build Presets**: Custom
   - **App location**: `/web`
   - **API location**: `/api`
   - **Output location**: `dist`

### Step 3: Configure Authentication

1. In the Static Web App, go to **Authentication**
2. Click **Add** under Identity providers
3. Select **Microsoft (Azure AD / Entra ID)**
4. Configure:
   - **App registration name**: `secai-radar-auth`
   - **App registration type**: Create new app registration
   - Save and wait for provisioning

### Step 4: Configure Application Settings

Go to **Configuration** → **Application settings** and add:

```
AzureWebJobsStorage=<connection_string_from_step_1>
TABLES_CONN=<connection_string_from_step_1>
BLOBS_CONN=<connection_string_from_step_1>
BLOB_CONTAINER=assessments
TENANT_ID=NICO
```

### Step 5: Configure Custom Domain

1. Go to **Custom domains** in the Static Web App
2. Click **Add**
3. Enter: `secai-radar.zimax.net` (or your preferred subdomain)
4. Follow DNS configuration instructions
5. Wait for SSL certificate provisioning

### Step 6: Configure GitHub Actions Secret

1. In the Static Web App, go to **Deployment token**
2. Copy the deployment token
3. In GitHub repository `zimaxnet/secai-radar`:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: Paste the deployment token

### Step 7: Verify Deployment

1. Push to `main` branch (workflow will trigger automatically)
2. Check GitHub Actions tab for workflow status
3. Once deployed, visit: `https://secai-radar.zimax.net` (or your custom domain)

## CI/CD Workflow

The `.github/workflows/azure-static-web-apps.yml` workflow will:
- Setup Python 3.12 and install API dependencies
- Build the React web app (Vite) with Node.js 22
- Deploy to Azure Static Web Apps on push to `main`
- Preview deployments on pull requests

## Troubleshooting

### Build Failures
- Check GitHub Actions logs
- Verify Node.js version (22) in workflow
- Verify Python version (3.12) in workflow

### Authentication Issues
- Verify Entra ID provider is configured
- Check `staticwebapp.config.json` routes with `allowedRoles`

### API Errors
- Verify application settings are set correctly
- Check storage account connection strings
- Ensure tables/blobs are accessible

