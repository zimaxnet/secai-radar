# SecAI Radar – AI Stack Blueprint

> Goal: an open-source, cloud-security assessment app that (1) collects configuration/evidence from cloud resources, (2) normalizes it, (3) lets an AI model explain posture and gaps, and (4) emits a final assessment report (Markdown/HTML/DOCX) that a consulting team can hand to a customer.  
> Scope: generic, no customer names, no tool/vendor names.

---

## 1. Objectives

1. **Ingest** cloud/security evidence from one or more tenants/subscriptions.
2. **Normalize** evidence into a common "controls/domains" data model.
3. **Index/Retrieve** normalized evidence for AI (RAG/search).
4. **Orchestrate** multi-step AI tasks (plan → call tools → summarize → review).
5. **Generate** a human-readable report with findings, recommendations, and roadmap.
6. **Expose** it all in a small web app for browsing runs and downloading reports.
7. **Keep it hygienic**: no hardcoded customers, vendors, or consulting firms.

---

## 2. High-Level Architecture (5 Layers)

1. **Infrastructure Layer**
   - Containerized API + worker (can run on any cloud).
   - Background jobs for long-running "assessment runs."
   - Secure config/secrets via environment variables.

2. **Model Layer**
   - Define model *roles*, not brands:
     - `reasoning_model` (multi-step security analysis)
     - `classification_model` (map evidence → control/domain)
     - `generation_model` (write reports)
   - Configurable in `config/models.yaml`.

3. **Data Layer**
   - **Bronze**: raw JSON from discovery/collectors (timestamped).
   - **Silver**: normalized records with resource, domain, control, status.
   - **Gold/RAG**: text chunks of silver, embedded and searchable.

4. **Orchestration Layer**
   - Takes a high-level task (`run_cloud_security_assessment`) and:
     1. plans which tools to call,
     2. calls collectors,
     3. normalizes to silver,
     4. asks the model to summarize per domain,
     5. assembles report sections.
   - Should support iterative "self-review" of AI outputs.

5. **Application Layer**
   - Web UI to:
     - list assessment runs
     - view findings by domain/control
     - show AI narrative with evidence links
     - download final report

---

## 3. Repository Structure (Proposed)

```text
secai-radar/
  README.md
  docs/
    blueprint.md          <-- this file
    data-model.md         <-- defines bronze/silver schemas
    report-template.md    <-- generic assessment template
  config/
    models.yaml
    frameworks.yaml       <-- list of controls/domains (CIS-like, but generic)
  src/
    api/                  <-- REST endpoints: run assessment, get results
    orchestrator/         <-- multi-step AI workflows
    collectors/           <-- cloud discovery (generic names)
    normalizers/          <-- bronze -> silver
    rag/                  <-- embeddings, search
    report/               <-- assemble markdown/html/docx
  ui/
    webapp/               <-- front-end app
  examples/
    sample-assessment-run/
    sample-report-output/
```

**Important**: do **not** name real customers or tools in `examples/`. Use `tenant-alpha`, `subscription-001`, `rg-app-prod`.

---

## 4. Data Model

### 4.1 Bronze (raw)

* Source: direct API calls, exports, questionnaires.
* Keep as-is, just store with metadata:

  ```json
  {
    "source": "cloud_api",
    "collected_at": "2025-11-05T16:00:00Z",
    "scope": {
      "tenant": "tenant-alpha",
      "subscription": "subscription-001"
    },
    "payload": { "..." : "raw provider response" }
  }
  ```

### 4.2 Silver (normalized)

* Purpose: let AI and UI query in a uniform way.
* Example:

  ```json
  {
    "resource_id": "/subscriptions/subscription-001/resourceGroups/rg-app-prod/providers/Microsoft.Storage/storageAccounts/appfiles001",
    "resource_type": "storage_account",
    "tenant": "tenant-alpha",
    "subscription": "subscription-001",
    "domain": "Logging & Monitoring",
    "control_id": "GEN-LM-001",
    "status": "non_compliant",
    "evidence_ref": "bronze/2025-11-05/cloud_api/storage.json",
    "detected_at": "2025-11-05T16:05:00Z",
    "notes": "Diagnostic logging is not enabled."
  }
  ```

### 4.3 Frameworks

* Define a generic control list in `config/frameworks.yaml`:

  ```yaml
  - id: GEN-IAM-001
    domain: "Identity & Access Management"
    title: "Centralize identity and authentication"
    severity: high
  - id: GEN-LM-001
    domain: "Logging & Monitoring"
    title: "Enable audit and diagnostic logging"
    severity: high
  - id: GEN-NET-001
    domain: "Network Security"
    title: "Restrict public exposure of services"
    severity: medium
  ```

Cursor can then auto-complete switch/case logic in code based on `domain` and `control_id`.

---

## 5. Orchestration Flows

### 5.1 Run an Assessment (happy path)

1. **Create run**

   * Input:

     ```json
     {
       "name": "baseline-assessment",
       "scope": {
         "tenant": "tenant-alpha",
         "subscriptions": ["subscription-001", "subscription-002"]
       }
     }
     ```

2. **Plan**

   * Orchestrator decides which collectors to call:

     * `collectInventory`
     * `collectPolicyState`
     * `collectSecurityFindings`
     * `collectLoggingConfig`

3. **Collect**

   * Each collector writes **bronze** records to storage.

4. **Normalize**

   * Normalizers read bronze → write **silver**.

5. **AI Analysis**

   * For each domain:

     * fetch relevant silver items
     * feed to `reasoning_model`
     * get "observations + impact + recommendation"

6. **Report Assembly**

   * Generate markdown sections:

     * `01-executive-summary.md`
     * `02-overall-findings.md`
     * `03-domain-details.md`
     * `04-remediation-roadmap.md`

7. **Expose**

   * Store structured results in DB / JSON for UI.
   * Offer "Download report" endpoint.

---

## 6. Report Template (Generic)

Create `docs/report-template.md` with the following skeleton:

```markdown
# Cloud Security Assessment Report

## 1. Executive Summary
(Generated: date/time)

- Purpose of assessment
- Scope (tenant, subscriptions)
- Overall posture summary
- Top 5 issues

## 2. Assessment Approach
- Automated collection of configuration and security evidence
- Normalization into common control model
- AI-assisted analysis and summarization
- Manual review (optional)

## 3. Findings by Domain

For each domain:
- Domain name
- Summary of status (compliant / partial / non-compliant)
- Key observations
- Recommendations

## 4. Detailed Findings

(1) Resource/Control
- Evidence
- Impact
- Recommendation

## 5. Remediation Roadmap
- Short-term (0–30 days)
- Mid-term (30–90 days)
- Long-term (90+ days)
```

This matches the shape of typical cloud security reports but stays neutral.

---

## 7. UI Requirements

1. **Assessment Runs list**

   * id, name, date, scope, status

2. **Run detail view**

   * summary
   * findings by domain
   * AI narrative (with links to evidence_ref)

3. **Download**

   * markdown → html → docx (server-side library, or user exports)

4. **No hardcoded names**

   * render metadata from the run, not from the codebase

---

## 8. Sanitization Rules

* Do **not** check in sample data that contains real organizations.
* Do **not** reference specific commercial security products in code.
* Use neutral identifiers: `tenant-alpha`, `tenant-beta`, `subscription-001`.
* Keep prompts generic: "You are assisting with a cloud security assessment for an organization."
* Document in `README` that downstream users can add provider-specific collectors in `src/collectors/`.

---

## 9. Tasks for Cursor (Example Prompts)

* **Create collectors interface**

  > Generate a TypeScript interface `Collector` with a `run(scope)` method that writes JSON bronze files to storage. Add two example collectors: `collectInventory` and `collectPolicyState`.

* **Create normalizer**

  > Generate a normalizer function that reads bronze inventory records and maps them to the silver schema defined in `docs/blueprint.md`. Use domain = "Inventory" and status = "observed".

* **Create report builder**

  > Generate a Node.js script that reads assessment JSON output and composes `docs/report-template.md` sections into a single markdown file.

* **Create API routes**

  > Generate Express routes for: `POST /assessments` (start run), `GET /assessments` (list), `GET /assessments/:id` (details), `GET /assessments/:id/report` (download markdown).

---

## 10. Notes

* This blueprint assumes **cloud-first** but the model/data/orchestration layers must remain provider-agnostic.
* All dates and times should be stored in UTC.
* All evidence items should retain a pointer to the original bronze file for auditability.
