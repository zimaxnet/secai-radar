---
layout: default
title: Assessment Workflow
permalink: /assessment-workflow/
---

# Assessment Workflow

This guide captures the updated automation that drives SecAI Radar assessments—from sanitized source material through the deliverables the app consumes and produces.

## 0. Stage Sanitized Inputs

Store demo or customer-ready (sanitized) artifacts under `analysis/security_domains/sanitized/`:

- `Azure_Framework_2025_template_sanitized.xlsx`
- `Cloud_Security_Assessment_Report_sanitized.docx`
- Demo walkthrough exports (for example, `demo/contoso_Questionaire.txt`, `demo/sp_contoso_Report.txt`)

Only redacted or sample data should live in the repository.

## 1. Generate Per-Domain CSVs

```bash
python analysis/security_domains/build_domain_csvs.py
```

Outputs:

- `analysis/security_domains/csv/*.csv` – one normalized file per security domain plus `ALL_CONTROLS.csv`
- `analysis/security_domains/control_mappings.json` – crosswalk between Excel IDs, Word tables, and `SEC-` IDs

Run this whenever the sanitized workbook or Word report changes. Rebuilding resets evidence counters, so collect evidence afterwards.

## 2. Collect Azure Evidence

Configure `analysis/security_domains/evidence_commands.yaml` with the Azure CLI commands that prove each control. Then run:

```bash
# Optional dry run
python analysis/security_domains/collect_azure_evidence.py --dry-run

# Full execution
python analysis/security_domains/collect_azure_evidence.py
```

The collector:

- Executes each CLI command (dotenv-aware via `env:` placeholders)
- Stores raw outputs under `analysis/security_domains/evidence_artifacts/{CONTROL_ID}/`
- Updates per-domain CSVs and `ALL_CONTROLS.csv` with evidence metadata (`EvidenceArtifacts`, counts, timestamps)

## 3. Generate Questionnaire Walkthrough

```bash
python analysis/security_domains/questionnaire/generate_questionnaire.py
```

- Reads `ALL_CONTROLS.csv`
- Emits Markdown walkthroughs to `analysis/security_domains/questionnaire/output/` grouping controls by domain and listing suggested evidence

Use `--csv`, `--output-dir`, or `--filename` to customize inputs/outputs.

## 4. Produce Summary Report

```bash
python analysis/security_domains/output/render_report.py
```

- Reads `ALL_CONTROLS.csv`
- Writes a markdown summary with per-domain compliance counts to `analysis/security_domains/output/report/`

Replace or extend this script with DOCX/PDF templating when the production reporting pipeline is ready.

## 5. Import Into SecAI Radar

1. Upload each domain CSV (or `ALL_CONTROLS.csv`) to Blob Storage under `assessments/{TenantId}/domains/`.
2. Call `POST /api/tenant/{tenantId}/import`.
3. Verify the app shows updated control states, evidence references, and compliance scores.

Keep `control_mappings.json` alongside the CSVs so follow-on automations can trace Excel ↔ Word ↔ SecAI IDs.

---

### Demo Walkthrough Artifacts

The repository includes sanitized samples under:

- `analysis/security_domains/sanitized/demo/` – redacted questionnaire/report excerpts
- `analysis/security_domains/questionnaire/output/` – generated demo questionnaire
- `analysis/security_domains/output/report/` – generated demo summary

Refresh these artifacts after updating sanitized inputs so the demo mirrors the current automation.

