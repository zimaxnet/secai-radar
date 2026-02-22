# Enable GitHub Pages for Wiki

## Current Status

The `wiki` branch exists on GitHub with all the content, but GitHub Pages needs to be **manually enabled** in the repository settings.

## Steps to Enable

1. **Go to GitHub Pages Settings**:
   - Visit: https://github.com/zimaxnet/secai-radar/settings/pages

2. **Configure Source**:
   - Under **"Source"**, select **"Deploy from a branch"**
   - **Branch**: Select `wiki`
   - **Folder**: Select `/ (root)` or `/docs/wiki` 
     - **Note**: The workflow (`pages.yml`) builds from `docs/wiki/` and outputs to `_site/wiki/`
     - If using the GitHub Actions workflow, you may need to select `/ (root)` and the workflow will handle the build
     - Alternatively, if you want to use the built files, check what folder the workflow outputs to

3. **Click "Save"**

4. **Wait for Build**:
   - GitHub will start building and deploying
   - This may take a few minutes
   - You'll see a status indicator on the Pages settings page

## Important Notes

### GitHub Actions Workflow vs Manual Deploy

The `wiki` branch has a GitHub Actions workflow (`.github/workflows/pages.yml`) that:
- Builds Jekyll site from `docs/wiki/` directory
- Outputs to `_site/wiki/` directory
- Uses GitHub Actions to deploy

**Option 1: Use GitHub Actions (Recommended)**
- In Pages settings, select **"GitHub Actions"** as the source (if available)
- The workflow will handle building and deploying automatically
- This is the modern approach

**Option 2: Use Branch Deploy**
- Select `wiki` branch
- Select `/ (root)` folder
- GitHub will serve the built files from `_site/wiki/` (if they exist)
- Or serve the raw markdown files from `docs/wiki/`

### Custom Domain

Once Pages is enabled:
- GitHub will verify the custom domain `wiki.secai-radar.zimax.net`
- The DNS CNAME record is already configured in Azure DNS
- SSL certificate will be automatically provisioned

## Troubleshooting

### "No branch configured" Message
- This means GitHub Pages hasn't been enabled yet
- Follow the steps above to enable it

### Branch Not Showing
- Make sure the `wiki` branch exists: https://github.com/zimaxnet/secai-radar/branches
- Refresh the Pages settings page
- Try selecting a different branch first, then switch back to `wiki`

### Build Fails
- Check the Actions tab for workflow runs: https://github.com/zimaxnet/secai-radar/actions
- Review the workflow logs for errors
- The `pages.yml` workflow may need adjustments

## Verification

After enabling:
1. Check the Pages settings page for "Your site is live at..."
2. Visit: `https://wiki.secai-radar.zimax.net` (after DNS propagation)
3. Visit: `https://zimaxnet.github.io/secai-radar` (default GitHub Pages URL)

## Next Steps

1. Enable GitHub Pages in settings
2. Wait for initial build/deploy
3. Verify custom domain is working
4. Test accessing the wiki

