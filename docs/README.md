# SecAI Radar Docs

This folder contains the essential documentation for the SecAI Radar MVP.

## Essential MVP Documentation

### Primary Architecture Reference

- **`blueprint.md`** — **Primary architecture blueprint** (AI Stack Blueprint). This is the authoritative source for architectural guidance. Defines the 5-layer architecture, objectives, and repository structure.

### Core Documentation

- `data-model.md` — Defines Bronze/Silver schemas and data layer patterns.
- `report-template.md` — Generic assessment report template.
- `model-integration.md` — Model Layer integration guide (GPT-5-chat configuration and usage).
- **`implementation-plan.md`** — **Comprehensive implementation plan** for all 5 layers of the AI stack.

### Infrastructure & Security

- **`DNS-SECURITY-GUIDE.md`** — **Complete DNS security guide** covering DNSSEC, CAA records, monitoring, and best practices for secai-radar.zimax.net.
- **`DNS-QUICK-REFERENCE.md`** — Quick reference for DNS security commands, troubleshooting, and common tasks.
- **`DNS-AZURE-COMPLETED.md`** — **Implementation summary** of completed DNS security improvements in Azure.
- **`DNS-IMPROVEMENTS-SUMMARY.md`** — Prioritized list of DNS security improvements with cost estimates.
- `COST-ESTIMATION.md` — Monthly infrastructure cost breakdown for Azure resources.

### User Documentation (Wiki)

- **`wiki/`** — **Complete wiki documentation** for users, administrators, and developers.
  - `wiki/Home.md` — Wiki homepage and navigation
  - `wiki/Getting-Started.md` — Quick start guide
  - `wiki/User-Guide.md` — Complete user documentation
  - `wiki/Dashboard-Guide.md` — Dashboard usage guide
  - `wiki/Controls-Guide.md` — Controls management guide
  - `wiki/Tools-Guide.md` — Tools configuration guide
  - `wiki/Gaps-Guide.md` — Gap analysis guide
  - `wiki/FAQ.md` — Frequently asked questions
  - `wiki/API-Reference.md` — API documentation
  - `wiki/Architecture.md` — Architecture overview
  - `wiki/Installation.md` — Installation guide
  - `wiki/Configuration.md` — Configuration guide
  - `wiki/Troubleshooting.md` — Troubleshooting guide
  - `wiki/Glossary.md` — Terms and definitions
  - `wiki/Contributing.md` — Contributing guide
  
  See `wiki/README.md` for instructions on publishing to GitHub Wiki or GitHub Pages.

### Navigation

- `README.md` — This file (documentation index).

## Architecture Overview

SecAI Radar follows a **5-layer architecture** (see `blueprint.md` for details):

1. **Infrastructure Layer** — Containerized API + worker, background jobs
2. **Model Layer** — Model roles (reasoning, classification, generation)
3. **Data Layer** — Bronze (raw), Silver (normalized), Gold/RAG (embedded)
4. **Orchestration Layer** — Multi-step AI workflows
5. **Application Layer** — Web UI for browsing runs and reports

## Key Principles

- **Vendor-agnostic**: No hardcoded customer names, vendor names, or consulting firm names
- **Role-based models**: Models defined by role (reasoning, classification, generation), not brand
- **Data layer separation**: Clear Bronze/Silver/Gold separation with lineage
- **Configurable**: Model selection and frameworks via `config/models.yaml` and `config/frameworks.yaml`

## Archived Documentation

Legacy documentation from previous implementation phases has been archived to `archive/`. See `archive/README.md` for details.

**For current development, always reference `blueprint.md` as the authoritative source.**
