---
layout: default
title: Local Development & Deploy
---

# Local Development & Deploy

To rapidly iterate on features, you can spin up the full SecAI Radar stack locally.

## Prerequisite Services

- NPM & Node v20
- Python 3.11+ (with venv/pip)
- Database credentials to the target Postgres DB (e.g. from Azure Key Vault)

## Running the API locally

```bash
cd apps/public-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:pass@host/db"
uvicorn main:app --reload --port 8000
```

## Running the Frontend locally

```bash
cd apps/public-web
npm install
npm run dev
```

The frontend will run on `http://localhost:5173` and inherently proxy API queries (via Vite config) to the running API on `8000`.

## GitHub Actions Deployments

Changes pushed to the `main` branch inherently trigger continuous integration pipelines that:

1. Build the frontend and push to Azure Static Web Apps.
2. Build the API container image and push to Azure Container Instances.
3. Automatically configure Custom Domain endpoints transparently.
