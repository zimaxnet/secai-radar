# Static Web App – "No site at secairadar.cloud" troubleshooting

**SWA name:** `secai-radar`  
**Resource group:** `secai-radar-rg`  
**Default hostname:** `purple-moss-0942f9e10.3.azurestaticapps.net`  
**Custom domain:** `secairadar.cloud` (Azure status: **Ready**)

## 1. Test the default hostname first

If the app is deployed at all, it will show up on the default hostname:

**https://purple-moss-0942f9e10.3.azurestaticapps.net**

- If this **loads** → deployment and SWA are fine; the problem is almost certainly **custom domain / DNS** (see §3).
- If this shows **nothing / 404 / error** → the problem is **deployment or token** (see §2).

## 2. Deployment and token

Deploys come from the **"Deploy to Staging"** workflow (on push to `main` or manual run). It:

1. Builds `apps/public-web` → `apps/public-web/dist`
2. Runs **Deploy to Azure Static Web Apps** with `app_location: "apps/public-web"`, `output_location: "dist"`, `skip_app_build: true`.

**Check:**

- [ ] **Actions** → **Deploy to Staging** → latest run on `main` is **green**.
- [ ] The step **"Deploy to Azure Static Web Apps"** **succeeded** (no red X).
- [ ] **AZURE_STATIC_WEB_APPS_API_TOKEN** in repo Secrets is the token for **this** SWA:  
  Azure Portal → **secai-radar** (Static Web App) → **Manage deployment token** → copy and update the secret.

If the token is for another SWA or is wrong, uploads can fail or go to the wrong app. After fixing the token, trigger **Deploy to Staging** again.

## 3. Custom domain and DNS (secairadar.cloud)

Azure shows **secairadar.cloud** as **Ready**. For the domain to serve the same app:

- DNS for **secairadar.cloud** must point at the Static Web App.

**Current DNS (summary):**

| Host | Type | Result |
|------|------|--------|
| `secairadar.cloud` | A | `20.109.133.32` (example; run `dig +short secairadar.cloud A` to confirm) |
| `purple-moss-0942f9e10.3.azurestaticapps.net` | CNAME → … → A | `20.84.233.119` (SWA front-end) |

If the A for **secairadar.cloud** is different from where **purple-moss-0942f9e10.3.azurestaticapps.net** resolves, traffic for **secairadar.cloud** is not hitting this SWA.

**What to do:**

1. In **Azure Portal**:  
   **secai-radar** → **Custom domains** → **secairadar.cloud**  
   Note the exact **CNAME target** (or any “point your domain here”) value Azure shows.

2. At your **DNS provider** for **secairadar.cloud**:
   - **Apex (secairadar.cloud):**  
     - If the provider supports **ALIAS/ANAME**, set it to  
       `purple-moss-0942f9e10.3.azurestaticapps.net`  
       (or the hostname Azure gives in the custom-domain blade).
     - If you must use **A**, use only the IP(s) Azure lists for this custom domain. Do not use an arbitrary IP.
   - **www (www.secairadar.cloud):**  
     Set **CNAME** to `purple-moss-0942f9e10.3.azurestaticapps.net`, then add **www.secairadar.cloud** as a custom domain in the SWA if you want to use it.

3. Run the domain check script:
   ```bash
   ./scripts/check-swa-domain-status.sh
   ```
   Ensure TXT (if required) and hostname/IP match what Azure and your DNS.

**Quick check:** Open **https://purple-moss-0942f9e10.3.azurestaticapps.net** in a browser. If that shows the app but **https://secairadar.cloud** does not, fix DNS for **secairadar.cloud** as above.

## 4. Useful commands

```bash
# SWA resource and default hostname
az staticwebapp show --name secai-radar --resource-group secai-radar-rg \
  --query "{defaultHostname:defaultHostname, customDomains:customDomains, sku:sku.name}" -o table

# Custom domain status
az staticwebapp hostname list --name secai-radar --resource-group secai-radar-rg -o table

# DNS (your machine)
dig +short secairadar.cloud A
dig +short purple-moss-0942f9e10.3.azurestaticapps.net A
```

## 5. Reference

- Custom domain setup: [docs/SWA-CUSTOM-DOMAIN-SETUP.md](./SWA-CUSTOM-DOMAIN-SETUP.md)
- Domain status script: [../scripts/check-swa-domain-status.sh](../scripts/check-swa-domain-status.sh)
- Deploy workflow: [.github/workflows/deploy-staging.yml](../.github/workflows/deploy-staging.yml)
