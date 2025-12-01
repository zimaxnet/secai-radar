# Quick Start - New Deployment Approach

## 🚀 Quick Setup (5 Steps)

### 1. Create Function App

```bash
cd scripts
./create-function-app.sh
```

### 2. Get Publish Profile

```bash
az functionapp deployment list-publishing-profiles \
  --name "secai-radar-api" \
  --resource-group "secai-radar-rg" \
  --xml
```

Copy the entire XML output.

### 3. Add GitHub Secret

1. GitHub → `zimaxnet/secai-radar` → Settings → Secrets → Actions
2. New repository secret
3. Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
4. Value: Paste XML from Step 2

### 4. Get Function App URL

```bash
az functionapp show \
  --name "secai-radar-api" \
  --resource-group "secai-radar-rg" \
  --query defaultHostName \
  --output tsv
```

You'll get: `secai-radar-api.azurewebsites.net`

### 5. Configure Web App

**Option A: GitHub Secret (Recommended)**
1. GitHub → Settings → Secrets → Actions
2. New secret: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

**Option B: Static Web App Settings**
1. Azure Portal → Static Web App → `secai-radar` → Configuration
2. Add: `VITE_API_BASE` = `https://secai-radar-api.azurewebsites.net/api`

## ✅ Deploy

Push to `main` branch or trigger workflows manually.

## 🧪 Test

```bash
# Test Function App
curl https://secai-radar-api.azurewebsites.net/api/domains

# Test from browser
# Open Static Web App and check DevTools Network tab
```

## 📚 More Info

- Full guide: [deployment-new-approach.md](./deployment-new-approach.md)
- Migration: [MIGRATION-GUIDE.md](./MIGRATION-GUIDE.md)

