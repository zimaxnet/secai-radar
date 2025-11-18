
# SecAI Radar Web (Vite + React)

The web app delivers the customer-facing demo experience. It ships with a guided landing page, tenant-aware routes, and sanitized sample data so prospects can walk through the full assessment flow.

## Quick Start

```bash
cd secai-radar/web
npm install
npm run dev
```

Set `VITE_DEFAULT_TENANT=<TenantId>` in `.env.local` (defaults to `NICO`) so the homepage demo CTA links into your preloaded assessment.

## Build & Deploy

```bash
npm run build
```

Deploy the `dist/` folder via Azure Static Web Apps or any static host. For AZ Static Web Apps:

```bash
az staticwebapp up \
  --name <AppName> \
  --resource-group <ResourceGroup> \
  --location <Region> \
  --source . \
  --app-location . \
  --output-location dist
```

## Key Routes

| Route | Purpose |
| --- | --- |
| `/` | Landing page + interactive demo journey |
| `/assessments` | Create/continue assessments (placeholder CTA) |
| `/tenant/:id/assessment` | Overview + readiness scores |
| `/tenant/:id/dashboard` | Domain coverage visualizations |
| `/tenant/:id/domain/:domainCode` | Domain controls listing |
| `/tenant/:id/control/:controlId` | Control detail with evidence |
| `/tenant/:id/tools` | Tool inventory |
| `/tenant/:id/gaps` | Hard/soft gap analysis |
| `/tenant/:id/report` | Executive summary |

## Demo Data Refresh

1. Regenerate sanitized artifacts via the scripts in `analysis/security_domains/`.
2. Upload the updated CSVs to Blob (`assessments/{TenantId}/domains/`).
3. Call `POST /api/tenant/{TenantId}/import` (see `secai-radar/api/README.md`).
4. Reload the web app to reflect the latest dataset.

## Authentication & Next Steps

- Static Web Apps authentication can be enabled later via `/signin` (future enhancement).
- Follow `secai-radar/docs/COMPLETE-SETUP.md` and `docs/wiki/Assessment-Workflow.md` for the full deployment story.
