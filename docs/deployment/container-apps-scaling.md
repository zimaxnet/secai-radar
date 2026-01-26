# SecAI Radar: Container Apps Scaling

## Current behavior

Both **public-api** and **registry-api** Container Apps are deployed with **min-replicas 1** so they stay on for demos. Turn them off manually when not needed (scale to 0 in Azure Portal or via `az containerapp update --min-replicas 0`).

- **min-replicas: 1** – At least one replica is always running.
- **max-replicas: 10** – Can scale up under load via the HTTP scale rule.
- **HTTP scale rule** – `scale-rule-type http`, `scale-rule-http-concurrency 10` – used for scale-up only.

## Turning containers off and on

**Scale to 0 (turn off):**
```bash
az containerapp update -g secai-radar-rg -n secai-radar-public-api --min-replicas 0 --max-replicas 0
az containerapp update -g secai-radar-rg -n secai-radar-registry-api --min-replicas 0 --max-replicas 0
```

**Scale back to 1 (turn on for demo):**
```bash
az containerapp update -g secai-radar-rg -n secai-radar-public-api --min-replicas 1 --max-replicas 10
az containerapp update -g secai-radar-rg -n secai-radar-registry-api --min-replicas 1 --max-replicas 10
```

Or use Azure Portal: Container App → Scale (under Application) → set Min replicas to 0 or 1.

## Where it’s configured

- **Deploy workflow** – [`.github/workflows/deploy-staging.yml`](../../.github/workflows/deploy-staging.yml) sets `--min-replicas 1 --max-replicas 10` for both apps on create and update.
