# 🎯 Next Actions - Get API Working

## ✅ Current Status

**Static Web App is WORKING!** 🎉

- ✅ Homepage showing: "SecAI Radar - Azure security assessment platform"
- ✅ Static Web App deployed successfully
- ✅ API URL configured: `VITE_API_BASE=https://secai-radar-api.azurewebsites.net/api`
- ⏳ Function App needs to be deployed (API not responding yet)

## 🚀 Immediate Next Steps

### Step 1: Deploy Function App

**Option A: Via GitHub Actions (Recommended)**

1. **Go to**: https://github.com/zimaxnet/secai-radar/actions
2. **Select**: "Deploy Azure Functions" workflow
3. **Click**: "Run workflow" → "Run workflow"
4. **Wait**: For deployment to complete (2-5 minutes)

**Option B: Via Azure CLI (Quick Test)**

```bash
cd api
npm install -g azure-functions-core-tools@4
func azure functionapp publish secai-radar-api
```

### Step 2: Verify Function App Deployment

After deployment, test:

```bash
# Test Function App endpoints
curl https://secai-radar-api.azurewebsites.net/api/domains
curl https://secai-radar-api.azurewebsites.net/api/tools
```

Should return JSON data (not empty).

### Step 3: Test from Web App

1. **Open**: https://purple-moss-0942f9e10.3.azurestaticapps.net
2. **Open DevTools** (F12) → **Network** tab
3. **Click**: "Go to Dashboard"
4. **Check**: Network tab for API calls
5. **Verify**: API calls are going to `https://secai-radar-api.azurewebsites.net/api`
6. **Check**: For CORS errors (should be none)

### Step 4: Redeploy Static Web App (If Needed)

After setting `VITE_API_BASE`, you may need to redeploy the Static Web App to pick up the new environment variable:

1. **Option A**: Push a new commit
   ```bash
   git commit --allow-empty -m "Trigger redeploy with API URL"
   git push origin main
   ```

2. **Option B**: Trigger manually in GitHub Actions
   - Go to Actions tab
   - Select "Build and Deploy SecAI Radar (SWA)"
   - Click "Run workflow"

## 🔐 After API Works: Configure Authentication

1. **Azure Portal**: Static Web App → `secai-radar` → **Authentication**
2. **Click**: "Add identity provider"
3. **Select**: "Microsoft (Azure AD / Entra ID)"
4. **Create** new app registration or use existing
5. **Save**

## 🌐 After Everything Works: Set Up Custom Domain

1. **Add DNS CNAME**: `secai-radar.zimax.net` → `purple-moss-0942f9e10.3.azurestaticapps.net`
2. **Azure Portal**: Static Web App → `secai-radar` → **Custom domains**
3. **Add**: `secai-radar.zimax.net`
4. **Verify** DNS and wait for SSL

## 🧪 Testing Commands

```bash
# Test Static Web App
curl https://purple-moss-0942f9e10.3.azurestaticapps.net

# Test Function App (after deployment)
curl https://secai-radar-api.azurewebsites.net/api/domains

# Check Function App logs
az functionapp log tail \
  --name secai-radar-api \
  --resource-group secai-radar-rg

# Check Static Web App settings
az staticwebapp appsettings list \
  --name secai-radar \
  --resource-group secai-radar-rg
```

## 📋 Checklist

- [x] Static Web App deployed and working
- [x] API URL configured (`VITE_API_BASE`)
- [ ] Function App deployed
- [ ] Function App endpoints responding
- [ ] Web app can call Function App API
- [ ] No CORS errors
- [ ] Authentication configured
- [ ] Custom domain configured

---

**Next**: Deploy Function App via GitHub Actions! 🚀

