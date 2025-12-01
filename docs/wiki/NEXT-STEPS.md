# 🎯 Next Steps - Complete the Setup

## ✅ What's Done

1. ✅ Function App created: `secai-radar-api`
2. ✅ App settings configured
3. ✅ CORS configured for Static Web App
4. ✅ Managed identity enabled
5. ✅ Publish profile saved to `function-app-publish-profile.xml`
6. ✅ GitHub workflows configured
7. ✅ Function App URL: `https://secai-radar-api.azurewebsites.net/api`

## 🔧 What You Need to Do Now

### Step 1: Add GitHub Secrets (Required)

#### Add Function App Publish Profile

1. Open `function-app-publish-profile.xml` in the project root
2. Copy the **entire XML content** (all lines)
3. Go to GitHub: `https://github.com/zimaxnet/secai-radar`
4. Navigate to: **Settings** → **Secrets and variables** → **Actions**
5. Click **New repository secret**
6. **Name**: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
7. **Value**: Paste the entire XML content
8. Click **Add secret**

#### Add API Base URL (Recommended)

1. In GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name**: `VITE_API_BASE`
4. **Value**: `https://secai-radar-api.azurewebsites.net/api`
5. Click **Add secret**

**Alternative**: Instead of GitHub Secret, you can set this in Azure Static Web App:
- Azure Portal → Static Web App → `secai-radar` → **Configuration**
- Add application setting: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

### Step 2: Deploy Function App

Once GitHub Secrets are configured:

1. **Option A**: Push any change to `api/` directory
   ```bash
   git add api/
   git commit -m "Trigger Function App deployment"
   git push origin main
   ```

2. **Option B**: Manually trigger workflow
   - Go to GitHub Actions tab
   - Select "Deploy Azure Functions" workflow
   - Click "Run workflow"

### Step 3: Deploy Static Web App

1. **Option A**: Push any change to `web/` directory
   ```bash
   git add web/
   git commit -m "Trigger Static Web App deployment"
   git push origin main
   ```

2. **Option B**: Manually trigger workflow
   - Go to GitHub Actions tab
   - Select "Build and Deploy SecAI Radar (SWA)" workflow
   - Click "Run workflow"

### Step 4: Verify Deployment

#### Test Function App Directly

```bash
# Test domains endpoint
curl https://secai-radar-api.azurewebsites.net/api/domains

# Test tools endpoint
curl https://secai-radar-api.azurewebsites.net/api/tools
```

#### Test from Static Web App

1. Open your Static Web App in browser
2. Open browser DevTools (F12) → Network tab
3. Navigate through the app
4. Check that API calls are going to `https://secai-radar-api.azurewebsites.net/api`
5. Verify no CORS errors appear

#### Check Deployment Logs

- **GitHub Actions**: Go to Actions tab → View workflow runs
- **Function App Logs**:
  ```bash
  az functionapp log tail --name secai-radar-api --resource-group secai-radar-rg
  ```

## 📋 Quick Checklist

- [ ] Added `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` to GitHub Secrets
- [ ] Added `VITE_API_BASE` to GitHub Secrets (or Static Web App settings)
- [ ] Deployed Function App (via push or manual trigger)
- [ ] Deployed Static Web App (via push or manual trigger)
- [ ] Tested Function App endpoints directly
- [ ] Tested Static Web App with API calls
- [ ] Verified no CORS errors in browser DevTools

## 🆘 Troubleshooting

### Function App Deployment Fails

1. Check GitHub Actions logs for errors
2. Verify publish profile is correct (no extra whitespace)
3. Verify Function App exists:
   ```bash
   az functionapp show --name secai-radar-api --resource-group secai-radar-rg
   ```

### CORS Errors in Browser

1. Check CORS configuration:
   ```bash
   az functionapp cors show --name secai-radar-api --resource-group secai-radar-rg
   ```

2. Add your domain if missing:
   ```bash
   az functionapp cors add \
     --name secai-radar-api \
     --resource-group secai-radar-rg \
     --allowed-origins "https://your-domain.com"
   ```

### API Not Responding

1. Check Function App status in Azure Portal
2. View logs:
   ```bash
   az functionapp log tail --name secai-radar-api --resource-group secai-radar-rg
   ```
3. Test function directly:
   ```bash
   curl https://secai-radar-api.azurewebsites.net/api/domains
   ```

## 📚 Documentation

- [Setup Complete](docs/wiki/SETUP-COMPLETE.md) - Detailed setup summary
- [Quick Start](docs/wiki/QUICK-START.md) - Quick reference guide
- [Deployment Guide](docs/wiki/deployment-new-approach.md) - Full deployment guide
- [Migration Guide](docs/wiki/MIGRATION-GUIDE.md) - Migration details

## 🎉 Success Criteria

You'll know everything is working when:

1. ✅ Function App deploys successfully via GitHub Actions
2. ✅ Static Web App deploys successfully via GitHub Actions
3. ✅ API endpoints respond correctly (test with curl)
4. ✅ Static Web App can call API (no CORS errors)
5. ✅ Application works end-to-end in browser

---

**Ready to deploy!** Follow the steps above to complete the setup. 🚀

