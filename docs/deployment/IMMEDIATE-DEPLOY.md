# 🚨 Immediate Deployment - Get Site Working Now

## Current Problem
- Static Web App shows default/empty page
- Function App not deployed
- Nothing has been deployed yet

## Solution: Connect to GitHub and Deploy

### Step 1: Commit Changes (If Needed)

You have uncommitted changes. Commit them:

```bash
cd /Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar
git add .
git commit -m "Add standalone Function App deployment setup"
git push origin main
```

### Step 2: Connect Static Web App to GitHub

**Option A: Via Azure Portal (Easiest)**

1. Go to: https://portal.azure.com
2. Navigate to: Static Web App → `secai-radar`
3. Click **Deployment** in left menu
4. Click **Add deployment source** or **Edit**
5. Select:
   - **Source**: GitHub
   - **Organization**: `zimaxnet`
   - **Repository**: `secai-radar`
   - **Branch**: `main`
   - **Build Presets**: Custom
6. Configure:
   - **App location**: `/web`
   - **Output location**: `dist`
   - **API location**: (leave empty - API is separate)
7. Click **Save**
8. Authorize GitHub if prompted

**Option B: Via Azure CLI**

```bash
# This requires GitHub token - portal is easier
az staticwebapp link \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --repo-url https://github.com/zimaxnet/secai-radar \
  --branch main \
  --app-location web \
  --output-location dist
```

### Step 3: Deploy Function App

**Via GitHub Actions (Recommended)**

1. Go to GitHub: https://github.com/zimaxnet/secai-radar
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Add `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`:
   - Open `function-app-publish-profile.xml`
   - Copy entire XML content
   - Paste as secret value
4. Go to **Actions** tab
5. Select "Deploy Azure Functions" workflow
6. Click **Run workflow** → **Run workflow**

**Or via CLI (Quick Test)**

```bash
cd api
npm install -g azure-functions-core-tools@4
func azure functionapp publish secai-radar-api
```

### Step 4: Verify Deployment

```bash
# Test Static Web App (should show your app, not default page)
curl https://purple-moss-0942f9e10.3.azurestaticapps.net

# Test Function App
curl https://secai-radar-api.azurewebsites.net/api/domains
```

## After Deployment Works

1. ✅ **Configure Authentication** (Entra ID)
   - Azure Portal → Static Web App → Authentication
   - Add Microsoft (Entra ID) provider

2. ✅ **Set up Custom Domain DNS**
   - Add CNAME: `secai-radar.zimax.net` → `purple-moss-0942f9e10.3.azurestaticapps.net`
   - Verify in Azure Portal

3. ✅ **Configure API URL in Web App**
   - Add `VITE_API_BASE` secret to GitHub or Static Web App settings
   - Value: `https://secai-radar-api.azurewebsites.net/api`

---

**Quickest Path**: Connect Static Web App to GitHub via Portal → Push code → Deploy Function App via GitHub Actions

