# SecAI Radar Infrastructure Blueprint

## Objectives
- Support AI-first workloads with **scale-to-zero** economics.
- Keep footprint serverless-first, relying on Azure consumption tiers wherever possible.
- Enable simple rollout of background AI batch jobs without introducing heavyweight orchestrators.
- Provide an IaC baseline so the environment is reproducible across dev, preprod, and prod.

## Target Environment

| Layer | Service | Purpose | Cost Controls |
|-------|---------|---------|---------------|
| Application | Azure Static Web App (`secai-radar`) | Host SPA frontend | Free tier (100 GB/month); upgrade only if bandwidth is exceeded |
| API | Azure Functions (Elastic Premium Plan) | Containerized API endpoints + HTTP triggers | `EP1` plan with `preWarmedInstanceCount=0`, autoscale 0→10; consumption fallback for dev |
| Worker | Azure Functions Queue Trigger (same app) | Asynchronous AI jobs (evidence classification, report batches) | Queue-driven, reuses plan capacity |
| Messaging | Azure Storage Queue | Work backlog for AI tasks | Pay-per-operation; negligible cost |
| State | Azure Storage (Blob + Table) | Evidence, catalog metadata, workflow state | Lifecycle policy moves cold data to Cool tier |
| Secrets | Azure Key Vault | API keys + configuration | Standard tier ($<1/month), shared across envs |
| AI | Azure OpenAI | GPT‑4o for reasoning/classification | Per-token cost; throttle via per-request budget guardrails |
| Monitoring | Azure Application Insights | Telemetry + cost monitoring | Sampling (5%), daily cap = $1 |

## Logical Architecture
```
Static Web App ──→ Function API (HTTP)
                          │
                          ├─→ Azure OpenAI (via ai_service)
                          ├─→ Storage Tables (controls, tools)
                          └─→ Queue Output (ai-jobs)

Queue Trigger Function ──→ Azure OpenAI (batch)
                        └─→ Blob Storage (evidence enrichment)
```

## Deployment Topology
- **Resource Groups**
  - `secai-radar-rg` (core app + storage + monitoring)
  - `secai-radar-network` (optional VNet integration if Premium plan with VNet is required)
- **Regions**: `East US 2` primary; keep AI resource co-located to minimize egress charges.
- **Naming Convention**: `${appName}-${env}-${resource}` (e.g., `secai-radar-prod-func`).

## IaC Structure (new `infra/` folder)
- `infra/main.bicep`: core deployment (storage, plan, function app, queue, insights).
- `infra/modules/staticwebapp.bicep`: optional module for Static Web App (future).
- `infra/parameters/<env>.bicepparam`: per-environment overrides (SKU, naming, OpenAI deployment ID).
- GitHub Actions workflow (`.github/workflows/infra-deploy.yml`) to deploy via `az deployment sub create`.

## Cost Levers & Defaults
- **Functions Plan**: Start with Elastic Premium `EP1` (1x vCPU, 3.5 GB) for predictable cold starts on containers; set `preWarmedInstanceCount=0` to allow scale-to-zero. For dev, permit `workflowMode="Consumption"`.
- **Queues vs. Durable Activity**: Use Storage Queues to avoid Durable Functions billing overhead until orchestration layer is required.
- **OpenAI**: Default to GPT‑4o; enforce `maxTokens=1_024` and `temperature=0.2` in `ai_service.py`. Add usage caps at API layer.
- **Monitoring**: Enable Application Insights with sampling and log retention of 30 days; disable expensive analytics tables unless needed.
- **Networking**: Defer VNet injection until compliance requires it; Premium plan supports VNet but introduces fixed compute cost.

## Deployment Workflow
1. **Parameterize**: Use `.bicepparam` files per environment (`dev`, `preprod`, `prod`).
2. **Validate**: `az deployment sub what-if` to preview changes.
3. **Deploy**: GitHub Action with OIDC (`azure/login`) running `az deployment sub create`.
4. **Configure**: Post-deploy script seeds Key Vault secrets and Storage queues.
5. **Verify**: Health checks for Function endpoints, queue trigger, and AI token limits.

## Next Steps
- Finalize IaC modules listed above.
- Add budget alerts via `CostManagement/budgets` resource in Bicep.
- Document rollback and disaster recovery strategy (to be covered in `docs/finops.md`).
