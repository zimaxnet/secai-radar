# Fix 401 Unauthorized Error - Function App Deployment

## Problem

GitHub Actions workflow failing with:
```
Error: Failed to fetch Kudu App Settings.
Unauthorized (CODE: 401)
```

## Root Cause

The `Azure/functions-action@v1` with publish profile is having authentication issues. This can happen due to:
1. Publish profile credentials expiring
2. Access restrictions blocking GitHub Actions
3. Compatibility issues with the action version

## Solution: Use Azure CLI Authentication

We've switched to using Azure CLI authentication instead of publish profile.

### Step 1: Add Azure Credentials to GitHub Secrets

1. **Service Principal Created**: ✅
   - Service Principal Name: `secai-radar-github-actions`
   - Role: Contributor
   - Scope: Resource Group `secai-radar-rg`

2. **Add to GitHub Secrets**:
   - Go to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions
   - Click: **New repository secret**
   - Name: `AZURE_CREDENTIALS`
   - Value: Get the JSON by running this command:
   ```bash
   az ad sp create-for-rbac --name "secai-radar-github-actions" \
     --role contributor \
     --scopes /subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg \
     --sdk-auth --output json
   ```
   Copy the entire JSON output and paste it as the secret value.
   - Click: **Add secret**

### Step 2: Deploy

The workflow has been updated to use:
- Azure login with service principal
- Azure Functions Core Tools for deployment
- Direct `func azure functionapp publish` command

**Trigger deployment**:
1. Go to: https://github.com/zimaxnet/secai-radar/actions
2. Select: "Deploy Azure Functions" workflow
3. Click: "Run workflow" → "Run workflow"

## Alternative: Fix Access Restrictions

If you prefer to keep using publish profile, you may need to configure access restrictions:

1. **Azure Portal**: Function App → `secai-radar-api` → **Networking**
2. **Access Restrictions**: 
   - Click "Access Restrictions"
   - Verify SCM (Kudu) restrictions allow GitHub Actions IPs
   - Add rule if needed: Service Tag → `AzureCloud` → Allow

## Updated Workflow

The workflow now:
- Uses Azure CLI authentication (service principal)
- Installs Azure Functions Core Tools
- Deploys using `func azure functionapp publish`
- More reliable for Python Functions

## Test After Deployment

```bash
curl https://secai-radar-api.azurewebsites.net/api/domains
curl https://secai-radar-api.azurewebsites.net/api/tools/catalog
```

Should return JSON data, not 404.

---

**Status**: Workflow updated. Add `AZURE_CREDENTIALS` secret and redeploy! 🚀

