# Fix GitHub Pages 404 Error

## Problem

GitHub Pages is enabled with GitHub Actions as the source, but you're getting a 404 error.

## Possible Causes

1. **Workflow hasn't run yet** - The workflow needs to be triggered
2. **Workflow failed** - Check the Actions tab for errors
3. **Output path issue** - The workflow builds to `_site/wiki` but GitHub Pages might expect root
4. **Missing index file** - No `index.html` or `index.md` in the deployed location
5. **Custom domain not verified** - DNS might not be resolving correctly

## Quick Checks

### 1. Check if Workflow Has Run

Go to: https://github.com/zimaxnet/secai-radar/actions
- Look for "Deploy Wiki to GitHub Pages" workflow
- Check if it has run and if it succeeded
- If it hasn't run, trigger it manually or push to the `wiki` branch

### 2. Check Workflow Output

If the workflow ran, check:
- Did it complete successfully?
- What path did it deploy to?
- Are there any error messages?

### 3. Check GitHub Pages Settings

Go to: https://github.com/zimaxnet/secai-radar/settings/pages
- Verify "GitHub Actions" is selected as the source
- Check the "Visit site" button to see the URL

## Solutions

### Solution 1: Fix the Workflow Output Path

The current workflow builds to `_site/wiki`, but GitHub Pages with Actions might expect the root. Update the workflow to build to the root:

```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: '_site/wiki'  # Change from '_site' to '_site/wiki'
```

### Solution 2: Trigger the Workflow

If the workflow hasn't run:
1. Go to: https://github.com/zimaxnet/secai-radar/actions
2. Find "Deploy Wiki to GitHub Pages"
3. Click "Run workflow" → Select `wiki` branch → Run

### Solution 3: Use Static Files (Simpler)

If Jekyll is causing issues, use the fallback static files approach:

1. Make sure `docs/wiki/index.md` or `docs/wiki/Home.md` exists
2. The workflow already has a fallback that copies static files
3. Ensure the workflow is set to upload from the correct path

### Solution 4: Check the Deployed URL

The site might be deployed but at a different path:
- Try: `https://zimaxnet.github.io/secai-radar/wiki/`
- Check the workflow output for the actual deployment URL

## Recommended Fix

Update the workflow to deploy from the correct path. The workflow should upload `_site/wiki` instead of `_site`, or change the build destination to `_site` root.

## Next Steps

1. Check the Actions tab to see if the workflow has run
2. If it hasn't run, trigger it manually
3. If it failed, check the error logs
4. If it succeeded but still 404, check the deployment path

## Verification

After fixing:
1. Wait for the workflow to complete
2. Check the Actions tab for the deployment URL
3. Try accessing the site
4. Check GitHub Pages settings for the live URL

