# Function App Deployment - Troubleshooting

## Current Issue

Function App is deployed but returning HTTP 404 for API endpoints.

## Status

- ✅ Function App created: `secai-radar-api`
- ✅ Function App is running
- ✅ CORS configured
- ✅ App settings configured
- ❌ API endpoints returning 404
- ❌ Functions may not be deployed yet

## Possible Causes

1. **Functions not deployed yet**
   - GitHub Actions workflow may not have run
   - Functions may not have been uploaded

2. **Deployment incomplete**
   - Functions may be partially deployed
   - Dependencies may not be installed

3. **Route configuration issue**
   - Routes may not match expected paths
   - `host.json` routePrefix may be incorrect

## Solution Steps

### Step 1: Verify Deployment

Check if functions are actually deployed:

```bash
# Check deployment status
az functionapp deployment list \
  --name secai-radar-api \
  --resource-group secai-radar-rg

# Check if GitHub Actions ran
# Go to: https://github.com/zimaxnet/secai-radar/actions
# Look for "Deploy Azure Functions" workflow
```

### Step 2: Deploy Functions

If functions aren't deployed, deploy them:

**Option A: Via GitHub Actions (Recommended)**

1. Go to: https://github.com/zimaxnet/secai-radar/actions
2. Select "Deploy Azure Functions" workflow
3. Click "Run workflow" → "Run workflow"
4. Wait for deployment to complete

**Option B: Via CLI (Quick Test)**

```bash
cd api
npm install -g azure-functions-core-tools@4

# Deploy
func azure functionapp publish secai-radar-api
```

### Step 3: Verify Functions Are Active

After deployment, test:

```bash
# Test domains endpoint
curl https://secai-radar-api.azurewebsites.net/api/domains

# Should return JSON data, not 404
```

### Step 4: Check Function App Logs

If still not working, check logs:

```bash
# View logs
az webapp log tail \
  --name secai-radar-api \
  --resource-group secai-radar-rg

# Or in Azure Portal:
# Function App → secai-radar-api → Log stream
```

## Expected Function Routes

Based on `host.json` and `function.json` files:

- `/api/domains` - GET
- `/api/tools` - GET (from tools function, route is `tools/catalog`)
- `/api/tenant/{tenantId}/controls` - GET
- `/api/tenant/{tenantId}/summary` - GET
- `/api/tenant/{tenantId}/tools` - GET, POST
- `/api/tenant/{tenantId}/gaps` - GET
- `/api/tenant/{tenantId}/import` - POST

## Verification

After deployment, these should work:

```bash
# Test domains
curl https://secai-radar-api.azurewebsites.net/api/domains

# Test tools (note: route is tools/catalog, not just tools)
curl https://secai-radar-api.azurewebsites.net/api/tools/catalog

# Test tenant tools
curl https://secai-radar-api.azurewebsites.net/api/tenant/NICO/tools
```

## Next Steps

1. ✅ Verify GitHub Actions workflow ran
2. ✅ Deploy functions if not deployed
3. ✅ Test endpoints
4. ✅ Check logs if still failing
5. ✅ Verify routes match expected paths

---

**Current Status**: Functions need to be deployed via GitHub Actions or CLI.

