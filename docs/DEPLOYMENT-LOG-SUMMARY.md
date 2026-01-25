# secairadar.cloud Deployment Log Summary

## Latest run (2026-01-25) — Failed

**Workflow:** Build and Deploy SecAI Radar (SWA)  
**Run ID:** 21323732661  
**Commit:** fc52d9e — "Update SWA configuration and complete local builds"  
**Result:** Failure (after successful build and upload)

### What succeeded

- Checkout, Node.js 22, npm cache
- **Install & Build:** `npm ci` and `npm run build` in `apps/public-web` completed (✓ built in 6.09s)
- **Deploy step:** App location `apps/public-web` found, build skipped (Oryx), app artifacts zipped and uploaded
- **Azure:** Upload finished; deployment ID `2b3797a2-b042-462d-97d8-a0c61bf00421`

### What failed

- **Azure reported:** `Status: Failed` → **Deployment Failure Reason: Deployment Canceled**
- Failure happened during Azure’s “Polling on deployment” (~30s after upload), not in the GitHub job itself.

### Likely causes

1. **Concurrent deployment** — Another deployment (same branch or overlapping trigger) may have caused Azure to cancel this one.
2. **Transient Azure condition** — Short-lived platform or regional issue.
3. **Artifact path** — With `skip_app_build: true`, the deploy action uses `app_location` + `output_location` (`apps/public-web` + `dist`), which is where the build writes output. No workflow change was required for this.

### What to do next

1. **Re-run the workflow**  
   - Actions → “Build and Deploy SecAI Radar (SWA)” → “Re-run failed jobs” or “Re-run all jobs”.
2. **Inspect Azure**  
   - Azure Portal → Static Web App **secai-radar** → Deployment history / logs to see why the deployment was canceled.
3. **Avoid duplicate runs**  
   - Ensure only one workflow deploys SWA on each push (no duplicate triggers for the same branch).

### Useful links

- [GitHub Actions – secai-radar](https://github.com/zimaxnet/secai-radar/actions)
- [Azure Static Web Apps – Build configuration](https://learn.microsoft.com/en-us/azure/static-web-apps/build-configuration)
- [Troubleshooting deployment and runtime errors](https://learn.microsoft.com/en-us/azure/static-web-apps/troubleshooting)
