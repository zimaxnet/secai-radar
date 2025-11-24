# ✅ Complete Setup Guide - Get Everything Working

## 🎯 Current Status

- ✅ Code committed and pushed to GitHub
- ✅ Function App created: `secai-radar-api`
- ✅ Static Web App created: `secai-radar`
- ⏳ Static Web App NOT connected to GitHub yet
- ⏳ GitHub Secrets need to be added
- ⏳ Deployments need to be triggered

## 📋 Step-by-Step Setup

### Step 1: Connect Static Web App to GitHub ⚠️ MANUAL REQUIRED

**This must be done via Azure Portal (cannot be automated via CLI)**

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Static Web App → `secai-radar`
3. **Click**: "Deployment" in the left menu
4. **Click**: "Add deployment source" or "Edit"
5. **Configure**:
   - **Source**: GitHub
   - **Organization**: `zimaxnet`
   - **Repository**: `secai-radar`
   - **Branch**: `main`
   - **Build Presets**: Custom
6. **Build Details**:
   - **App location**: `/web`
   - **Output location**: `dist`
   - **API location**: *(leave empty - API is separate)*
7. **Click**: "Save"
8. **Authorize GitHub** if prompted

✅ **This will automatically trigger the first deployment!**

---

### Step 2: Add GitHub Secrets

**Go to**: https://github.com/zimaxnet/secai-radar/settings/secrets/actions

#### Secret 1: `AZURE_STATIC_WEB_APPS_API_TOKEN`

**Value**: Run this command to get it:
```bash
cd /Users/derek/Library/CloudStorage/OneDrive-zimaxnet/code/SecAI/secai-radar
bash scripts/show-secrets.sh
```

Or get it directly:
```bash
az staticwebapp secrets list \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --query properties.apiKey \
  --output tsv
```

**Value**: `1865c4c671d57aa9512b7a22ee5b078c1923c8b145f7741fb09d1c7e2548d8aa03-c90d6ded-e185-49ae-a42d-09eedd9dc75d01009280942f9e10`

#### Secret 2: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`

**Value**: Copy the entire content of `function-app-publish-profile.xml`

```bash
cat function-app-publish-profile.xml
```

Copy the entire XML content (all lines).

#### Secret 3: `VITE_API_BASE` (Optional but Recommended)

**Value**: `https://secai-radar-api.azurewebsites.net/api`

**Alternative**: Instead of GitHub Secret, you can set this in Azure Static Web App settings:
- Azure Portal → Static Web App → `secai-radar` → **Configuration**
- Add application setting: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

---

### Step 3: Deploy Function App

1. **Go to**: https://github.com/zimaxnet/secai-radar/actions
2. **Select**: "Deploy Azure Functions" workflow
3. **Click**: "Run workflow" button
4. **Select**: Branch: `main`
5. **Click**: "Run workflow" (green button)

✅ **This will deploy the Function App**

---

### Step 4: Verify Deployments

#### Check Static Web App

After Step 1 (connecting to GitHub), the deployment should start automatically. Check:

1. **GitHub Actions**: https://github.com/zimaxnet/secai-radar/actions
   - Look for "Build and Deploy SecAI Radar (SWA)" workflow
   - Should run automatically after connecting to GitHub

2. **Test Static Web App**:
   ```bash
   curl https://purple-moss-0942f9e10.3.azurestaticapps.net
   ```
   Should show your app (not default page)

3. **Azure Portal**: 
   - Static Web App → `secai-radar` → **Deployment history**
   - Should show deployment status

#### Check Function App

1. **Test Function App**:
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```
   Should return JSON data

2. **Check Logs**:
   ```bash
   az functionapp log tail \
     --name secai-radar-api \
     --resource-group secai-radar-rg
   ```

---

### Step 5: Configure Authentication 🔐

**After both apps are working**, set up Entra ID authentication:

1. **Azure Portal**: Static Web App → `secai-radar` → **Authentication**
2. **Click**: "Add identity provider"
3. **Select**: "Microsoft (Azure AD / Entra ID)"
4. **Choose**: "Create new app registration" or use existing
5. **Configure**:
   - **Name**: `secai-radar-auth`
   - The app registration will be created automatically
6. **Save**

**Callback URLs** (configured automatically):
- `https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad/callback`
- `https://secai-radar.zimax.net/.auth/login/aad/callback` (after DNS setup)

---

### Step 6: Configure Custom Domain 🌐

**After deployment is working**:

1. **Add DNS CNAME Record**:
   - **Name**: `secai-radar.zimax.net`
   - **Value**: `purple-moss-0942f9e10.3.azurestaticapps.net`
   - **TTL**: 3600 (or default)

2. **Azure Portal**: Static Web App → `secai-radar` → **Custom domains**
3. **Click**: "Add"
4. **Enter**: `secai-radar.zimax.net`
5. **Follow**: DNS verification instructions
6. **Wait**: For SSL certificate provisioning (5-30 minutes)

---

## ✅ Verification Checklist

- [ ] Static Web App connected to GitHub
- [ ] `AZURE_STATIC_WEB_APPS_API_TOKEN` added to GitHub Secrets
- [ ] `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` added to GitHub Secrets
- [ ] `VITE_API_BASE` added to GitHub Secrets (or Static Web App settings)
- [ ] Function App deployed via GitHub Actions
- [ ] Static Web App deployment running/completed
- [ ] Static Web App shows your app (not default page)
- [ ] Function App endpoints respond correctly
- [ ] Authentication configured (Entra ID)
- [ ] Custom domain configured and verified

---

## 🧪 Quick Test Commands

```bash
# Test Static Web App
curl https://purple-moss-0942f9e10.3.azurestaticapps.net

# Test Function App
curl https://secai-radar-api.azurewebsites.net/api/domains
curl https://secai-radar-api.azurewebsites.net/api/tools

# Check deployment status
az staticwebapp show \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --query "{deploymentCount:deploymentCount, repositoryUrl:repositoryUrl}"

# View Function App logs
az functionapp log tail \
  --name secai-radar-api \
  --resource-group secai-radar-rg
```

---

## 🆘 Troubleshooting

### Static Web App Not Deploying

1. **Check GitHub connection**:
   - Azure Portal → Static Web App → Deployment
   - Verify repository is linked

2. **Check GitHub Actions**:
   - Go to Actions tab
   - Check for workflow errors

3. **Verify deployment token**:
   - GitHub Secrets → `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Should match the token from Azure

### Function App Not Deploying

1. **Check publish profile**:
   - Verify `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` secret is correct
   - Should be complete XML content

2. **Check GitHub Actions logs**:
   - Look for deployment errors

3. **Test Function App**:
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```

### CORS Errors

1. **Verify CORS configuration**:
   ```bash
   az functionapp cors show \
     --name secai-radar-api \
     --resource-group secai-radar-rg
   ```

2. **Add missing origin**:
   ```bash
   az functionapp cors add \
     --name secai-radar-api \
     --resource-group secai-radar-rg \
     --allowed-origins "https://your-domain.com"
   ```

---

## 📚 Quick Reference

- **Static Web App**: https://purple-moss-0942f9e10.3.azurestaticapps.net
- **Function App**: https://secai-radar-api.azurewebsites.net
- **API Base URL**: https://secai-radar-api.azurewebsites.net/api
- **GitHub Repo**: https://github.com/zimaxnet/secai-radar
- **Azure Portal**: https://portal.azure.com

---

**Ready to deploy!** Follow the steps above in order. 🚀

