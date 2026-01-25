# Azure Static Web App Updated ✅

## Configuration Updated

The Azure Static Web App configuration has been updated to match the monorepo structure:

- **App Location:** `apps/public-web` (was likely `web` or empty)
- **Output Location:** `dist` (build output directory)
- **API Location:** (empty - no API in SWA)

## Verification

To verify the configuration:

```bash
az staticwebapp show \
  --name secai-radar \
  --resource-group secai-radar-rg \
  --query "{appLocation:appLocation,outputLocation:outputLocation,apiLocation:apiLocation}"
```

## Next Steps

1. **Push to main branch** - This will trigger automatic deployment
   ```bash
   git add .
   git commit -m "Update SWA config for monorepo structure"
   git push origin main
   ```

2. **Monitor deployment** - Check GitHub Actions or Azure Portal
   - GitHub: https://github.com/zimaxnet/secai-radar/actions
   - Azure Portal: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/staticsite

3. **Verify deployment** - Once deployed, check:
   - https://secairadar.cloud/mcp (or your custom domain)
   - Health endpoint: https://secairadar.cloud/health

## Build Configuration

The SWA will now:
1. Look for source code in `apps/public-web/`
2. Run `npm install` and `npm run build`
3. Deploy files from `apps/public-web/dist/` to Azure

## Troubleshooting

If deployment fails:

1. **Check build logs** in GitHub Actions
2. **Verify package.json** has correct build script:
   ```json
   "scripts": {
     "build": "tsc && vite build"
   }
   ```
3. **Check for build errors** locally:
   ```bash
   cd apps/public-web
   npm run build
   ```

## Current Status

✅ **Configuration Updated**
⏳ **Waiting for deployment** (triggered by push to main)
