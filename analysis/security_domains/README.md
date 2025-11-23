## Security Domain Data Pipeline

This folder bridges the sanitized assessment artifacts (workbook + Word report) with the SecAI Radar data model. It gives consultants a four-stage, repeatable workflow:

0. **Stage sanitized inputs** for demo or live runs.
1. **Generate normalized control CSVs** per security domain with doc-linked metadata.
2. **Collect Azure evidence automatically** and push the resulting artifacts back into those CSVs before importing them into Radar.
3. **Produce questionnaires and reports** from the normalized data for stakeholder delivery.

### 0. Stage sanitized assessment inputs

Place sanitized artifacts under `analysis/security_domains/sanitized/`:

- `analysis/security_domains/sanitized/Azure_Framework_2025_template_sanitized.xlsx`
- `analysis/security_domains/sanitized/Cloud_Security_Assessment_Report_sanitized.docx`
- Demo walkthrough exports (for example `demo/contoso_Questionaire.txt`, `demo/sp_contoso_Report.txt`) live under `sanitized/demo/`.

> Only sanitized or sample data should be committed. Keep live customer exports out of this repo.

---

### 1. Build the per-domain control CSVs

With sanitized sources in place, run:

```bash
python analysis/security_domains/build_domain_csvs.py
```

Outputs:

- `analysis/security_domains/csv/NET_network-security.csv` … one file per domain (12 total)
- `analysis/security_domains/csv/ALL_CONTROLS.csv` – aggregate convenience file
- `analysis/security_domains/control_mappings.json` – quick lookup (SEC ↔ Excel ↔ doc IDs)

Each CSV already contains the headers expected by `/api/tenant/{tenantId}/import`, plus useful extras (doc compliance status, observations, mappings, evidence checklist placeholders). Re-run this script whenever the sanitized workbook or report changes.

> ⚠️ Rebuilding CSVs resets evidence counters/artifacts. Run the evidence collector *after* the converter when both are needed.

---

### 2. Capture Azure evidence and update the CSVs

Configure the Azure CLI commands that prove control coverage in `analysis/security_domains/evidence_commands.yaml`. Example snippet:

```yaml
tenant: NICO
context:
  subscription: env:AZ_SUBSCRIPTION_ID
  resource_group: Contoso-SecOps-RG
controls:
  SEC-NET-0001:
    evidence:
      - name: vnet_inventory
        command: az network vnet list --subscription {subscription} --output json
        output: json
      - name: nsg_rules
        command: az network nsg list --subscription {subscription} --output json
        output: json
```

- `context` entries can reference environment variables via `env:VAR_NAME`.
- Add as many `controls` and `evidence` steps as required. Each step can inject ad-hoc `{vars}` overrides.

Run the collector:

```bash
# Dry-run (no Azure CLI calls; writes placeholders for smoke tests)
python analysis/security_domains/collect_azure_evidence.py --dry-run --control SEC-NET-0001

# Real execution against every control defined in the YAML
python analysis/security_domains/collect_azure_evidence.py
```

What it does:

- Executes each Azure CLI command, storing the raw output under `analysis/security_domains/evidence_artifacts/{CONTROL_ID}/`.
- Updates the corresponding domain CSV + `ALL_CONTROLS.csv` with:
  - `EvidenceArtifacts` (JSON metadata + file paths)
  - `AvailableEvidenceCount`
  - `EvidenceLastCollected`

Use `--control CONTROL_ID` to scope runs, `--csv-dir` / `--evidence-dir` to override locations, and `--skip-csv` if you only want the raw artifacts.

---

### 3. Import into SecAI Radar

1. Upload each per-domain CSV to Blob Storage under `assessments/{TenantId}/domains/` (one file per domain).
2. Call `POST /api/tenant/{tenantId}/import` with either the aggregate CSV or domain-level CSVs.
3. The API upserts into `Controls` table using the normalized IDs (`SEC-{DOMAINCODE}-{####}`), preserving the evidence metadata added by the collector.

Keep `control_mappings.json` alongside the CSVs; it drives any future automation (e.g., mapping back to the report or selecting controls for evidence runs).

---

### 4. Generate questionnaires & final reports

- `analysis/security_domains/questionnaire/` – scaffold for `generate_questionnaire.py` (to be implemented) that emits stakeholder questionnaires from the normalized CSVs.
- `analysis/security_domains/output/` – staging area for generated Word/PDF reports (`output/report/`) and any supporting evidence artifacts.

Integrate these outputs back into the sanitized demo artifacts so the walkthrough reflects what the SecAI Radar app produces end-to-end.
