## SecAI Radar Demo Deployment Guide

SecAI Radar delivers a vendor-neutral Azure security assessment that you can walk through with prospects in minutes. This repository bundles everything needed to showcase the full experience—data prep, API, web app, and sanitized demo artifacts—so you can deploy to a customer tenant or run locally without guesswork.

### What’s Inside

- `analysis/security_domains/` – scripts that convert sanitized workbook/report inputs into normalized CSVs, collect Azure evidence, and generate demo questionnaires/reports.
- `secai-radar/api/` – Azure Functions back end that provides assessment, control, tool, gap, and report endpoints.
- `secai-radar/web/` – React front end packaged for Azure Static Web Apps with an interactive demo journey.
- `docs/wiki/` – published documentation (see [Assessment Workflow](docs/wiki/Assessment-Workflow.md)) mapping the entire pipeline.

### One-Glance Demo Flow

1. **Prep sanitized data**  
   Place sanitized Excel/Word sources + demo excerpts in `analysis/security_domains/sanitized/`.
2. **Generate domain CSVs**  
   `python analysis/security_domains/build_domain_csvs.py`
3. **Collect (or stub) Azure evidence**  
   `python analysis/security_domains/collect_azure_evidence.py --dry-run` (replace with real commands when ready).
4. **Produce customer-facing assets**  
   - Questionnaire: `python analysis/security_domains/questionnaire/generate_questionnaire.py`  
   - Summary report: `python analysis/security_domains/output/render_report.py`
5. **Import into the app**  
   Upload CSVs to blob storage (`assessments/{TenantId}/domains/`) then call `POST /api/tenant/{TenantId}/import`.
6. **Launch the demo**  
   Deploy the API (Azure Functions) + web app (Static Web Apps or Vite preview) and browse to `/` to follow the guided experience.

### Deploying to a Customer Tenant

1. **Prerequisites**
   - Azure subscription with Static Web Apps + Functions permissions
   - `az` CLI 2.53+ (login with the target tenant)
   - Node 18+, Python 3.12+, and enough rights to create storage accounts / tables

2. **Provision infrastructure**
   - Use `secai-radar/scripts/create-function-app.sh` to deploy the Functions app (or follow `secai-radar/docs/DEPLOY-NOW.md` for portal-driven setup).
   - Configure required secrets (Storage connection, OpenAI/Azure AI keys) via `scripts/store-secrets.sh` and the guidance in `secai-radar/docs/KEY-VAULT-SETUP.md`.

3. **Seed assessment data**
   - Upload generated CSVs to Blob (`assessments/{TenantId}/domains/`).
   - Run the import endpoint once (`POST /api/tenant/{TenantId}/import`) with `ALL_CONTROLS.csv`.
   - Optionally seed tool inventory via `POST /api/tenant/{TenantId}/tools`.

4. **Deploy the web app**
   - `cd secai-radar/web`
   - `npm install`
   - `npm run build`
   - `az staticwebapp up --name <AppName> --location <region> --resource-group <rg> --source . --app-location . --output-location dist`

5. **Smoke-test the demo**
   - Navigate to the Static Web App URL.
   - Confirm the homepage “Explore Interactive Demo” CTA routes to `/tenant/<TenantId>/assessment`.
   - Step through the linked screens in the demo journey to show Assessment → Dashboard → Domain → Control detail → Tools → Gaps → Report.

### Local Development

- **API**: `cd secai-radar/api && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && func start`
- **Web**: `cd secai-radar/web && npm install && npm run dev`
- **Environment**: set `VITE_DEFAULT_TENANT=<TenantId>` and point Functions to local Azurite or real storage.

### Keeping the Demo Fresh

- Re-run the analysis scripts whenever you update sanitized inputs so the CSVs, questionnaire, and report align.
- Refresh blob data and re-trigger `/import` before major customer demos.
- Update `Landing.tsx` or documentation if you add new flows to the app so the guided tour stays accurate.

Need a deeper dive? Start with `docs/wiki/Assessment-Workflow.md`, then review `secai-radar/docs/DEPLOY-NOW.md` for detailed Azure deployment steps.

