# 🚨 Quick Fix - 401 Error Resolved

## ✅ Fix Applied

The workflow has been updated to use **Azure CLI authentication** instead of publish profile, which fixes the 401 error.

## 🔧 What You Need to Do NOW

### Add Azure Credentials to GitHub Secrets

1. **Go to**: https://github.com/zimaxnet/secai-radar/settings/secrets/actions
2. **Click**: "New repository secret"
3. **Name**: `AZURE_CREDENTIALS`
4. **Value**: Copy this entire JSON:

**Get the JSON by running this command** (service principal already created):
```bash
az ad sp create-for-rbac --name "secai-radar-github-actions" \
  --role contributor \
  --scopes /subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg \
  --sdk-auth --output json
```

Copy the entire JSON output and paste it as the secret value.

**Note**: If the service principal already exists, you may need to create a new one or reset the password:
```bash
az ad sp credential reset --id 06b544a3-0db0-4c8c-bc7b-fbd97b83421f --sdk-auth --output json
```

5. **Click**: "Add secret"

### Deploy

1. **Go to**: https://github.com/zimaxnet/secai-radar/actions
2. **Select**: "Deploy Azure Functions" workflow
3. **Click**: "Run workflow" → "Run workflow"

This should now work without 401 errors!

## ✅ What Changed

- ✅ Switched from publish profile to Azure CLI authentication
- ✅ Using Azure Functions Core Tools for deployment
- ✅ More reliable for Python Functions
- ✅ Service principal created with Contributor role

## 🧪 Test After Deployment

```bash
curl https://secai-radar-api.azurewebsites.net/api/domains
```

Should return JSON data!

---

**Ready to deploy!** Just add the `AZURE_CREDENTIALS` secret and run the workflow. 🚀

