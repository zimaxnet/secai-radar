# Branch Structure: `main` vs `gh-pages`

## Overview

The repository intentionally maintains two long-lived branches with **different responsibilities**:

- `main` — builds and runs the SecAI Radar product (Azure Functions API + React app) and ships production infrastructure.
- `gh-pages` — publishes the public blueprint/wiki on GitHub Pages and carries any static assets required for that site.

Understanding the split keeps deployments predictable and ensures we do not lose critical APIs when working from the documentation branch.

---

## Branch Profiles

### `main`
- **Purpose**: Product development and production deployments.
- **Deployments**:
  - Azure Static Web Apps (`secai-radar.zimax.net`).
  - Azure Functions (AI recommendations, evidence ingestion, report writer, etc.).
- **Code included**:
  - `api/`, `web/`, shared services, seeds, infrastructure scripts.
  - Developer/engineering documentation in `docs/`.
- **CI/CD**:
  - `.github/workflows/azure-static-web-apps.yml` (web).
  - `.github/workflows/azure-functions-deploy.yml` (API) with failure notifications.
- **When to use**:
  - Any backend or frontend feature work.
  - Updating infrastructure-as-code or shared services.
  - Authoring developer-focused documentation.

### `gh-pages`
- **Purpose**: Public-facing blueprint, wiki, and hosted static site.
- **Deployments**:
  - GitHub Pages at `https://zimaxnet.github.io/secai-radar/`.
  - No Azure deployments (APIs and Azure infra are **not** present).
- **Code included**:
  - `docs/wiki/` plus supporting assets.
  - GitHub Pages workflow (`.github/workflows/pages.yml`).
  - Optional static build of the SPA for documentation/demo purposes.
- **When to use**:
  - Editing public blueprint or wiki content.
  - Maintaining the Pages workflow or static assets served by GitHub.

---

## Relationship & Sync Strategy

| Area | `main` | `gh-pages` | Notes |
|------|--------|------------|-------|
| Azure Functions APIs | ✅ | ❌ | Only `main` contains AI recommendations, evidence ingestion, reports, etc. |
| React app source (`web/src`) | ✅ | ✅ (may include compiled assets) | Keep `gh-pages` dist artifacts aligned with `main` or document how to rebuild. |
| Documentation | Developer/engineering docs (`docs/`) | Public blueprint/wiki (`docs/wiki/`) | Cross-link so contributors know where the source of truth lives. |
| Workflows | Azure web/API deploy | GitHub Pages deploy | Failure notifications live on `main`; mirror as needed on `gh-pages`. |
| DNS / CNAME | `secai-radar.zimax.net` → Azure Static Web App | Uses default `zimaxnet.github.io/secai-radar/` | Custom wiki domain retired; no `CNAME` file in `gh-pages`. |

Because the branches diverge, **do not merge `gh-pages` back into `main`**. Instead, cherry-pick or copy specific documentation changes if they are relevant to developers.

---

## Working Guidelines

1. **Feature or infrastructure work** → Branch from `main` and open PRs back into `main`.
2. **Wiki/blueprint updates** → Branch from `gh-pages` and open PRs back into `gh-pages`.
3. **Do not delete APIs from `main`** based on the trimmed `gh-pages` view—the documentation branch intentionally omits backend services.
4. **Keep secrets out of `gh-pages`**. Use placeholders in public scripts/configs and store real identifiers in Azure Key Vault or GitHub Secrets.
5. **Regenerate static assets intentionally**. If `gh-pages` keeps committed `web/dist` artifacts, document the build command (`npm install && npm run build`) so output stays in sync with `main`.

---

## Syncing Content

- To reuse documentation written on `main`, copy or cherry-pick the relevant markdown into `gh-pages` (do not merge branches wholesale).
- If the wiki references code changes from `main`, link to the relevant files/commits instead of duplicating logic.
- When architecture changes in `main`, add a task to update the public blueprint so both audiences stay aligned.

---

## Frequently Asked Questions

**Q: Where do I add new AI endpoints?**  
Always on `main`. The `gh-pages` branch is documentation-only.

**Q: Can I deploy `gh-pages` to Azure Functions?**  
No. It does not contain the required code or workflows.

**Q: How do I link between the wiki and developer docs?**  
Use absolute URLs when pointing to GitHub Pages (`https://zimaxnet.github.io/secai-radar/...`) and relative links for files that live in `main`.

**Q: What happened to the old `wiki` branch?**  
It has been retired. All public documentation now lives on `gh-pages`.

---

## Summary

- `main` = production code and Azure deployments.  
- `gh-pages` = public blueprint + wiki hosted by GitHub Pages.  
- Treat them as complementary, not interchangeable, and document changes accordingly.
