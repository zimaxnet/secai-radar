# Azure Credentials for GitHub Secrets

## Service Principal Created

A service principal has been created for GitHub Actions deployment:

**Name**: `secai-radar-github-actions`  
**Role**: Contributor  
**Scope**: Resource Group `secai-radar-rg`

## Add to GitHub Secrets

### Step 1: Go to GitHub Secrets

Navigate to: https://github.com/zimaxnet/secai-radar/settings/secrets/actions

### Step 2: Add Secret

1. Click **New repository secret**
2. **Name**: `AZURE_CREDENTIALS`
3. **Value**: Copy the entire JSON below:

**Get the JSON from Azure CLI** (run this command):
```bash
az ad sp create-for-rbac --name "secai-radar-github-actions" \
  --role contributor \
  --scopes /subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg \
  --sdk-auth --output json
```

Copy the entire JSON output and paste it as the secret value.

4. Click **Add secret**

## After Adding Secret

1. Go to: https://github.com/zimaxnet/secai-radar/actions
2. Select: "Deploy Azure Functions" workflow
3. Click: "Run workflow" → "Run workflow"

The deployment should now work without 401 errors!

---

**Important**: Keep this secret secure. Do not commit it to the repository.

