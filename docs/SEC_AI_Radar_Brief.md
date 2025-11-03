# SecAI Radar — Build Brief (Context Doc)

> **Goal:** Create a consultant-friendly web app to **conduct Azure security assessments** in a customer environment, quantify control coverage, and produce **explainable gap analysis** and actionable recommendations based on the **SecAI Framework**—independent of any single vendor (e.g., Sentinel).

---

## 1) Who this is for

- **Primary user:** a security consultant/architect working inside a customer’s tenant.
- **Stakeholders:** customer security leadership, control owners, practitioners.
- **Outcomes:** a repeatable, tool-agnostic assessment with traceable evidence and clear remediation plans.

---

## 2) Core problem & approach

Customers use **different security tool stacks** (Google SecOps, Palo Alto, Wiz, CrowdStrike, Proofpoint, etc.). Traditional assessments over-index on specific vendor tools (e.g., Sentinel). **SecAI Radar** maps controls to **capability requirements**, then measures how well the **customer’s actual tools** cover those capabilities (with configuration quality considered). The result is an **objective coverage score** and **transparent gap list** per control.

---

## 3) Product pillars

1. **Data Collection**
   - Per-domain **CSV**s (or forms) for controls (title, description, status, evidence, score).
   - Customer **tool inventory** (what’s deployed + config quality).
   - Evidence links/files stored per control.

2. **Normalization & Consolidation**
   - Validate inputs → **normalized “bronze” model** (cheap, queryable).
   - Deterministic `ControlID`s and consistent schema.

3. **Scoring & Gaps**
   - Each control maps to one or more **capabilities** with **weights** and a **minStrength** threshold.
   - For each capability, pick the **best customer tool** (strength × configScore).
   - Compute coverage, classify hard/soft gaps, generate recommendations.

4. **Explainability**
   - Every score is reproducible and explainable: which capabilities mattered, which tool covered, and where gaps remain.

5. **Export & Presentation**
   - Web dashboards (tiles + radar).
   - Download CSV snapshots.
   - (Optional) Emit a consolidated workbook or `summary.json` for Excel spider charts.

---

## 4) Architecture (cost-first, Azure-native)

- **Frontend:** Vite + React (TypeScript), Tailwind + shadcn/ui, Recharts
- **Auth/Hosting:** **Azure Static Web Apps (SWA)** with **Entra ID (Azure AD)** auth
- **API:** **Azure Functions (Python)** — HTTP triggers (and optional Timer/Queue)
- **Storage:**
  - **Azure Blob Storage:** source CSVs, evidence uploads, export artifacts
  - **Azure Table Storage:** normalized data (Controls, TenantTools); seed catalogs can start as JSON
  - (Optional later) Cosmos DB serverless for richer querying

**Why:** minimal cost & friction, easy local dev with **Azurite**, and simple scale-up path.

---

## 5) Data model (Tables & Blobs)

> **Tenant ID example:** `NICO` (adjust per customer)

### 5.1 Controls (normalized)
- **Table:** `Controls`  
- **PartitionKey:** `{TenantId}|{DomainCode}` (e.g., `NICO|NET`)  
- **RowKey:** `ControlID` (e.g., `SEC-NET-0007`)  
- **Fields:** `ControlTitle`, `ControlDescription`, `Question`, `RequiredEvidence`,  
  `Status` (`NotStarted|InProgress|Complete|NotApplicable`), `Owner`, `Frequency`,  
  `ScoreNumeric` (0..100), `Weight` (0..1), `Notes`, `SourceRef`, `Tags`, `UpdatedAt`

**CSV headers (import):**
```
ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,
Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
```

### 5.2 Vendor Tools (catalog)
- **Table or JSON seed:** `VendorTools`  
- `id`, `name`, `vendor`, `capabilities[]`, `notes`, `links`

### 5.3 Capability Taxonomy
- **Table or JSON seed:** `Capabilities`  
- `capabilityId`, `name`, `description`

### 5.4 Tool→Capability Strengths (catalog)
- **Table or JSON seed:** `ToolCapabilities`  
- Key: `{vendorToolId, capabilityId}` → `strength` (0..1), `maturity` (0..1), `notes`

### 5.5 Control→Capability Requirements (framework brain)
- **Table or JSON seed:** `ControlRequirements`  
- Key: `{controlId, capabilityId}` → `weight` (0..1), `minStrength` (0..1), `notes`

### 5.6 Customer Tool Inventory
- **Table:** `TenantTools`  
- **PartitionKey:** `{TenantId}`  
- **RowKey:** `{vendorToolId}`  
- Fields: `Enabled` (bool), `ConfigScore` (0..1), `Owner`, `Notes`

### 5.7 Evidence
- **Blob:** `assessments/{TenantId}/evidence/{ControlID}/...`  
- (Optional **Table:** `Evidence` with pointers & review status)

---

## 6) Scoring model (transparent)

For each **ControlID**:
1. **Required capabilities**: from `ControlRequirements[controlId]` → list `{cap_i, weight w_i, minStrength_i}`.  
2. **Best tool per capability** (customer inventory):
   - For each active tool `t`: `candidate = Strength(t, cap_i) × ConfigScore(t)`
   - `coverage_i = max(candidate across active tools)`
3. **CoverageScore** = Σ `w_i × coverage_i`  (weights typically sum to 1)
4. **Normalize** (if needed) and scale to 0..100 for display
5. **Gap classification**:
   - **Hard Gap:** `coverage_i == 0` and `w_i` high (e.g., ≥ 0.25)  
   - **Soft Gap:** `0 < coverage_i < minStrength_i`  
6. **Recommendations:**
   - First, **tune** tools with low `ConfigScore` to raise coverage  
   - Then consider adding a tool strong in the missing capability

> **Example**  
> `SEC-NET-0001`: needs `ns-firewall (0.6, min 0.6)` + `url-filtering (0.4, min 0.6)`  
> Customer has Palo Alto FW (`ns-firewall`, `url-filtering`) and ConfigScore=0.8.  
> If strengths are 0.9 and 0.85, coverage = `0.6*(0.9*0.8) + 0.4*(0.85*0.8)` = `0.432 + 0.272` = **0.704 (70.4%)** → **OK**.

---

## 7) API surface (Functions HTTP)

```
GET   /api/domains
GET   /api/tools/catalog

GET   /api/tenant/{tenantId}/controls?domain=NET&status=Complete&q=edr
POST  /api/tenant/{tenantId}/import           # CSV or JSON array upsert

GET   /api/tenant/{tenantId}/tools
POST  /api/tenant/{tenantId}/tools            # {vendorToolId, Enabled, ConfigScore, ...}

GET   /api/tenant/{tenantId}/summary          # tiles for dashboard/radar
GET   /api/tenant/{tenantId}/gaps             # coverage %, hard/soft gaps + reasons

# (Later)
POST  /api/tenant/{tenantId}/score/recalc     # force rebuild
GET   /api/tenant/{tenantId}/evidence/{controlId}
POST  /api/tenant/{tenantId}/evidence/{controlId}
```

**Bindings**  
- Tables: `Controls`, `TenantTools` (+ optional catalog tables)  
- Blob: `assessments/{tenantId}/domains/controls_*.csv`, `.../evidence/...`

---

## 8) Frontend UX (Vite + React)

- **Auth:** Entra ID via Static Web Apps; per-route authorization.
- **Tenant & Domain Picker:** set working context.
- **Controls Grid:** filter by domain/status/text; inline edit; CSV import/export.
- **Control Detail:** capability breakdown, strongest covering tool, gaps, evidence panel.
- **Tools Inventory:** toggle enabled tools, set ConfigScore, owner, notes.
- **Gaps View:** hard/soft gaps with **why** and **suggested actions** (tune vs add).
- **Dashboard:** tiles and radar/spider charts per domain and overall.
- **Auditability:** show last updated, who changed what (later).

---

## 9) Naming & ID conventions

- **Control IDs:** `SEC-{DOMAINCODE}-{0000}` e.g., `SEC-NET-0001`  
  - Deterministic generation; maintain a **mapping** to avoid re-keying.
- **Domain codes:**  
  `NET, ID, PA, DATA, ASSET, LOG, IR, POST, END, BAK, DEV, GOV`
- **Partition keys:**  
  Controls → `{TenantId}|{DomainCode}`  
  TenantTools → `{TenantId}`

---

## 10) Security, privacy, and roles

- **Auth:** Entra ID (SWA) with role claims; restrict tenants by group or app roles.
- **Least privilege** storage keys (SAS / managed identity).
- **Evidence classification**: mark sensitive uploads; apply retention policy.
- **Audit log** (future): track changes to controls, tools, and config scores.

---

## 11) KPIs / success metrics

- **Coverage lift**: % of controls improving to ≥ target threshold over time.
- **Gap reduction**: number of hard gaps closed per month.
- **Evidence completeness**: fraction of controls with required evidence types.
- **Time to assessment**: start → export report duration.
- **Explainability**: % of scores with complete rationale available.

---

## 12) Roadmap (phased)

**Phase 1 — Foundation (done/near)**  
- Seeds (capabilities, tools, strengths)  
- Import → Controls (Table)  
- Tenant tools inventory endpoints  
- Summary tiles & gaps endpoint  
- Basic web shell + auth

**Phase 2 — UX & Explainability**  
- Control detail with capability coverage graph  
- Tools inventory UI with ConfigScore sliders  
- CSV import UI (Papaparse + Zod) & export snapshots  
- Radar chart per domain

**Phase 3 — Evidence & Excel Bridge**  
- Evidence uploads (Blob) + link attach  
- Build `summary.json` or `consolidated.xlsx` for Excel spider  
- Signed URLs for data pulls

**Phase 4 — Governance & Scaling**  
- RBAC per tenant; audit log  
- Catalog editor (tune strengths, add tools/capabilities)  
- Optional: move to Cosmos DB serverless for richer queries

---

## 13) Contribution & quality gates

- **Schema contract**: single source of truth (JSON Schema + Zod).  
- **Validation on import**: required fields, vocab, numeric bounds, no unknown columns, dedupe `ControlID`.  
- **Tests**: scoring engine unit tests (coverage math, gap thresholds).  
- **CI**: run validations + tests on PR; block if seed/catalog changes break scoring.

---

## 14) Example seed snippets

**Tool capability strength (catalog)**
```json
{ "vendorToolId": "wiz-cspm", "capabilityId": "cspm", "strength": 0.85, "maturity": 0.8 }
```

**Control capability requirement (framework)**
```json
{ "controlId": "SEC-LOG-0001", "capabilityId": "siem", "weight": 1.0, "minStrength": 0.7 }
```

**Tenant tool inventory (customer-specific)**
```json
{ "PartitionKey": "NICO", "RowKey": "google-secops", "Enabled": true, "ConfigScore": 0.8 }
```

---

## 15) Definition of Done (MVP)

- Can **import** per-domain CSVs for a tenant and view them in the grid.
- Can **declare customer tools** + config scores.
- **Summary tiles** and **gaps** populate and are explainable.
- **Radar chart** renders per domain from API.
- **Auth** via Entra ID working; tenant scoping respected.

---

## 16) Open questions / decisions

- Final **capability taxonomy** scope (keep lean vs exhaustive).
- Standard **minStrength** defaults per capability? (framework default vs per-control overrides)
- Weighting policy for **ScoreNumeric** vs capability-derived coverage (are both shown or unify them?).
- Evidence policy: required types per control & how they affect scoring (multiplier vs gate).

---

## 17) Project layout (suggested)

```
secai-radar/
  api/                    # Azure Functions (Python)
    shared/
    domains/
    tools/
    controls/
    import_controls/
    tenant_tools/
    summary/
    gaps/
    seeds_*               # seeded JSON for runtime
  web/                    # Vite + React app
  seeds/                  # canonical seeds (editable source)
  docs/                   # this brief + ADRs + runbooks
```

---

**Bottom line:** SecAI Radar gives consultants a **vendor-neutral, capability-driven** way to measure control coverage in any Azure environment—**explainable**, **auditable**, and **actionable**.
