# 🚀 Deploy Now - Quick Deployment Guide

## Current Status

- ✅ Function App created: `secai-radar-api`
- ✅ Static Web App created: `secai-radar`
- ❌ **No deployments yet** - Both apps show default/empty pages
- ❌ Static Web App not connected to GitHub
- ❌ Function App not deployed

## Option 1: Deploy via GitHub Actions (Recommended)

### Prerequisites
1. Ensure GitHub Secrets are configured:
   - `AZURE_STATIC_WEB_APPS_API_TOKEN` (from Static Web App deployment token)
   - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` (from `function-app-publish-profile.xml`)

2. Connect Static Web App to GitHub:
   ```bash
   # Or do this via Azure Portal:
   # Azure Portal → Static Web App → secai-radar → Deployment → Add source
   ```

### Steps

1. **Push code to trigger deployment**:
   ```bash
   git add .
   git commit -m "Deploy web app and function app"
   git push origin main
   ```

2. **Or manually trigger workflows**:
   - Go to GitHub → Actions tab
   - Run "Build and Deploy SecAI Radar (SWA)" workflow
   - Run "Deploy Azure Functions" workflow

## Option 2: Manual Deployment (Quick Test)

### Deploy Static Web App Manually

1. **Build the web app locally**:
   ```bash
   cd web
   npm install
   npm run build
   ```

2. **Deploy using Azure CLI**:
   ```bash
   # Get deployment token
   az staticwebapp secrets list \
     --name secai-radar \
     --resource-group secai-radar-rg \
     --query properties.apiKey \
     --output tsv

   # Deploy (using swa CLI or Azure CLI)
   ```

3. **Or use SWA CLI** (if installed):
   ```bash
   npm install -g @azure/static-web-apps-cli
   swa deploy ./web/dist \
     --deployment-token <TOKEN> \
     --app-name secai-radar \
     --resource-group secai-radar-rg
   ```

### Deploy Function App Manually

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Deploy from api directory
cd api
func azure functionapp publish secai-radar-api
```

## Option 3: Connect Static Web App to GitHub (Best Long-term)

1. **Azure Portal**:
   - Go to Static Web App → `secai-radar`
   - Click **Deployment** → **Add deployment source**
   - Select **GitHub**
   - Authorize and select:
     - Organization: `zimaxnet`
     - Repository: `secai-radar`
     - Branch: `main`
     - Build Presets: **Custom**
     - App location: `/web`
     - Output location: `dist`
     - **API location: (leave empty)** - API is separate now

2. **Save** - This will trigger the first deployment

## Quick Check Commands

```bash
# Check Static Web App deployment status
az staticwebapp show \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --query "{deploymentCount:deploymentCount, repositoryUrl:repositoryUrl, branch:branch}"

# Check Function App deployment
az functionapp deployment source show \
  --name secai-radar-api \
  --resource-group secai-radar-rg

# Test Static Web App
curl https://purple-moss-0942f9e10.3.azurestaticapps.net

# Test Function App
curl https://secai-radar-api.azurewebsites.net/api/domains
```

## Next Steps After Deployment

1. ✅ Verify web app loads (not default page)
2. ✅ Verify Function App endpoints respond
3. ✅ Test API calls from web app
4. ✅ Configure authentication (Entra ID)
5. ✅ Set up custom domain DNS

---

**Recommended**: Connect Static Web App to GitHub and push code to trigger automatic deployments.

