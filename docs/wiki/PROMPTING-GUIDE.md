# SecAI Radar Advanced Prompting Guide

> **Purpose:** This guide defines the prompting principles and templates we use for SecAI Radar development to ensure the highest quality, accuracy, and explainability—especially critical for security assessments and compliance scoring.

---

## 1. Purpose & Scope

This guide primes AI assistance for SecAI Radar development with:

1. **Multi-step, self-correcting generations** over single-pass answers
2. **Exposed reasoning structures** for inspection and validation
3. **Self-prompt redesign capability** when needed
4. **Edge case consideration** for security, compliance, and scoring accuracy
5. **Multi-perspective analysis** for consultant, customer, and developer viewpoints

**Critical Application Areas:**
- Scoring engine logic and validation
- Security architecture and compliance mapping
- Data validation and schema enforcement
- Evidence handling and retention
- API design and tenant isolation
- Frontend UX for explainability
- Wiki documentation clarity

---

## 2. Core Principles Applied to SecAI Radar

### 2.1 Self-Correction Systems

**Goal:** Force critique and revision of outputs, especially for scoring logic and security decisions.

#### Chain of Verification Template (for Scoring Logic)
> You will perform this in 3 phases.  
> **Phase 1 — Draft:** Implement the scoring calculation for control coverage based on capability requirements, tenant tools, and tool capabilities.  
> **Phase 2 — Verification:** List at least 3 ways your draft may be incomplete or incorrect:
> - Edge cases (e.g., zero weights, missing tools, capability not in catalog)
> - Mathematical errors (normalization, rounding, boundary conditions)
> - Logic errors (hard vs soft gap classification, best tool selection)
> - Security concerns (tenant data isolation, input validation)
> For each, cite the specific code section or say "missing from input."  
> **Phase 3 — Revision:** Rewrite the implementation to fix all issues found in Phase 2. Include unit tests for edge cases. Output only the revised version.

#### Adversarial Prompting Template (for Architecture Reviews)
> Attack the previous design/implementation. Identify 5 specific weaknesses:
> 1. **Security vulnerability** (tenant isolation, data leakage, auth bypass)
> 2. **Scoring accuracy** (edge case failure, mathematical error, explainability gap)
> 3. **Compliance risk** (evidence handling, audit trail, data retention)
> 4. **Operational concern** (scalability, cost, maintainability)
> 5. **User experience** (explainability, consultant workflow, customer presentation)
> 
> For each: describe the weakness, give likelihood (high/medium/low), give impact (critical/high/medium/low), and propose mitigation. Then show the improved version.

**Use for:**
- Security architecture reviews (ADR creation/updates)
- Scoring algorithm changes
- API endpoint design
- Data model changes
- Evidence handling policies
- Tenant isolation mechanisms

---

### 2.2 Strategic Edge-Case Learning

**Goal:** Teach the model gray areas to reduce false negatives in validation, scoring, and security checks.

#### Template for Validation Logic
> I will show 3 examples that should be **rejected** and 1 that should **pass**. Learn these patterns, especially the subtle failure. Then evaluate the new sample and tell me which pattern it matches and why.
> 
> **Example 1 (Reject):** ControlID `SEC-NET-0001` with Domain `NET`, weight sum = 1.2 (should be ≤ 1.0)
> **Example 2 (Reject):** ControlID `SEC-LOG-0001` with capability requirement `{capabilityId: "siem", weight: 0.8, minStrength: 0.7}` but capability `siem` not in catalog
> **Example 3 (Reject):** Tenant tool `wiz-cspm` with ConfigScore = 1.5 (should be 0.0-1.0)
> **Example 4 (Pass):** ControlID `SEC-NET-0001` with Domain `NET`, weight sum = 1.0, all capabilities exist, ConfigScore = 0.8
> 
> Now evaluate: [new sample]

#### Template for Scoring Edge Cases
> Learn these scoring edge cases:
> 1. **Zero coverage:** Control requires capability `ns-firewall`, but tenant has no tools with this capability → CoverageScore = 0, Hard Gap
> 2. **Partial coverage:** Control requires `{siem: 0.6, log-retention: 0.4}`, tenant has `google-secops` (siem: 0.9, log-retention: 0.3), ConfigScore = 0.8 → Coverage = 0.6*(0.9*0.8) + 0.4*(0.3*0.8) = 0.432 + 0.096 = 0.528 (52.8%)
> 3. **Soft gap:** Coverage = 0.5, minStrength = 0.7 → Soft Gap
> 4. **Overlapping tools:** Tenant has both `wiz-cspm` (cspm: 0.85) and `azure-defender` (cspm: 0.6), both enabled → Use best (0.85)
> 
> Now evaluate: [new scenario]

**Use for:**
- CSV import validation (`validate_seeds.py`, schema validation)
- Scoring engine unit tests (`test_scoring.py`)
- Control requirement validation
- Tool capability mapping validation
- Tenant tool inventory validation
- Gap classification logic

---

### 2.3 Meta-Prompting

**Goal:** Let the model design optimal prompts for complex SecAI Radar tasks.

#### Reverse Prompting Template (for Feature Design)
> You are an expert prompt designer for security assessment tools.  
> Task: "Design an API endpoint and UI component for consultants to upload evidence files (PDFs, screenshots, CSVs) for a specific control, with proper tenant isolation, blob storage, signed URLs, and audit logging."  
> 1. Design the single most effective prompt to implement this feature. Include:
>    - Role (Azure Functions developer, React developer)
>    - Input format (API contract, UI mockup, data flow)
>    - Output schema (function.json, TypeScript interface, React component structure)
>    - Verification step (how to test tenant isolation, file size limits, security)
> 2. Show me the designed prompt.
> 3. Then execute that prompt on the SecAI Radar codebase.

#### Recursive Prompt Optimization Template (for Complex Refactoring)
> You are a recursive prompt optimizer for SecAI Radar. Here is my current prompt: ```[existing prompt]```  
> Produce 3 improved versions:
> - **v1:** Add missing constraints (tenant isolation, scoring explainability, evidence retention policy)
> - **v2:** Resolve ambiguities (explicit inputs/outputs, error handling, edge cases)
> - **v3:** Increase reasoning depth and add self-check (verify scoring math, test tenant isolation, validate against ADRs)
> Then recommend which version to use for this refactoring task.

**Use for:**
- Complex feature implementation (evidence upload, catalog editor)
- Large refactorings (scoring engine, data model changes)
- API design (multi-tenant endpoints, batch operations)
- Frontend component design (radar charts, control detail views)

---

### 2.4 Reasoning Scaffolds

**Goal:** Prevent collapsing reasoning too early for complex SecAI Radar problems.

#### Over-Instruction Template (for Documentation)
> Do NOT summarize. Expand each point with:
> - **Implementation detail:** code examples, API contracts, data flow diagrams
> - **Edge cases:** validation failures, scoring edge cases, tenant isolation scenarios
> - **Failure modes:** what breaks, how to detect, how to recover
> - **Historical/contextual notes:** why this decision was made, related ADRs, alternatives considered
> - **Compliance/security notes:** evidence handling, audit requirements, data retention
> Prioritize completeness over brevity.

#### Zero-to-Chain-of-Thought Template (for Troubleshooting)
> Fill in each section for this SecAI Radar issue:
> 1. **Problem statement:** [e.g., "Scoring shows 0% coverage for control SEC-NET-0001, but tenant has Palo Alto FW enabled"]
> 2. **Relevant components/data/scope:**
>    - Scoring engine (`api/shared/scoring.py`)
>    - Control requirements (seed data, Table Storage)
>    - Tenant tools (Table Storage `TenantTools`)
>    - Tool capabilities (seed data, catalog)
> 3. **Likely causes or solution paths (3):**
>    - Cause A: Tool capability mapping missing (Palo Alto not mapped to `ns-firewall` capability)
>    - Cause B: Tenant tool not enabled (Palo Alto in catalog but `Enabled=false` in tenant inventory)
>    - Cause C: ConfigScore = 0 or capability strength = 0
> 4. **Evidence required to confirm/deny:**
>    - Check `ToolCapabilities` seed for `palo-alto-fw` → `ns-firewall` mapping
>    - Check `TenantTools` table for `Enabled=true` and `ConfigScore > 0`
>    - Check control requirements for `SEC-NET-0001` → `ns-firewall` capability
> 5. **Final recommendation:**
>    - Fix [specific issue]
>    - Add validation to prevent recurrence
>    - Update tests to cover this scenario
> 6. **Validation / next steps:**
>    - Run scoring unit tests
>    - Verify in UI with test tenant
>    - Update documentation if needed

**Use for:**
- Troubleshooting scoring issues
- Debugging API endpoint failures
- Investigating tenant isolation problems
- Documenting complex features (ADRs, wiki pages)
- Explaining scoring logic to stakeholders

---

### 2.5 Perspective Engineering & Temperature Simulation

**Goal:** Surface blind spots by forcing conflicting viewpoints for SecAI Radar decisions.

#### Multi-Persona Template (for Feature Planning)
> Simulate 3 experts with conflicting priorities for this SecAI Radar feature:
> 1. **Security Consultant (User):** Needs explainability, vendor-neutral scoring, actionable recommendations, fast workflow
> 2. **Customer Security Leader (Stakeholder):** Needs compliance alignment, evidence retention, audit trails, clear gap prioritization
> 3. **Azure Architect (Developer):** Needs cost efficiency, scalability, maintainability, simple deployment
> 
> Each must critique the others' requirements. After the debate, synthesize a plan that addresses all concerns and note tradeoffs.

#### Temperature Simulation Template (for Implementation Decisions)
> For this SecAI Radar implementation decision:
> 1. Give a **cautious, over-explained version** (junior developer): extensive validation, detailed error messages, defensive coding, comprehensive tests
> 2. Give a **concise, confident version** (senior developer): lean implementation, assumes good inputs, trusts existing validation, minimal tests
> 3. Reconcile the two and tell me where caution vs confidence is appropriate:
>    - **Caution needed:** Scoring logic (must be accurate and explainable), tenant isolation (security critical), input validation (CSV imports)
>    - **Confidence OK:** UI polish (can iterate), documentation clarity (can refine), non-critical features (can add later)

**Use for:**
- Feature prioritization (backlog decisions)
- Architecture trade-offs (ADR creation)
- Scoring policy decisions (thresholds, weights, evidence factors)
- UI/UX design (explainability vs simplicity)
- API design (flexibility vs simplicity)

---

## 3. Project-Specific Application

### Domain: Azure Security Assessment & Compliance Scoring

**Preferred Output Format:**
- **Code:** Python (Azure Functions), TypeScript/React (Web UI)
- **Documentation:** Markdown (ADRs, wiki, developer docs)
- **Data:** JSON (seeds, API responses), CSV (imports/exports)
- **Schema:** JSON Schema + Zod validation

**Verification Sources:**
- **Documentation:** `docs/SEC_AI_Radar_Brief.md`, `docs/adr/`, `docs/backlog.md`
- **Code:** `api/shared/scoring.py`, `api/shared/validate_seeds.py`, `api/tests/`
- **Seeds:** `seeds/` directory (JSON files with schemas)
- **ADRs:** `docs/adr/` for architectural decisions

**Security/Compliance Context:**
- **Frameworks:** CIS, NIST (referenced in controls, capability mapping)
- **Standards:** Evidence retention (ADR 0005), audit trails, tenant isolation
- **Tools in Scope:** Vendor-neutral (Wiz, Palo Alto, Google SecOps, CrowdStrike, Azure Defender, etc.)

**Quality Gates:**
- **Schema validation:** JSON Schema + Zod on all imports
- **Unit tests:** Scoring engine (`test_scoring.py`), validation logic
- **CI/CD:** Run validations + tests on PR; block if seed/catalog changes break scoring
- **Explainability:** Every score must be reproducible and explainable

---

## 4. SecAI Radar-Specific Prompting Patterns

### Pattern 1: Scoring Algorithm Development
**When to use:** Implementing or modifying scoring logic, adding new capability types, adjusting thresholds.

**Template:**
> Apply Chain of Verification (Phase 1-3) to implement scoring for [specific scenario].
> 
> **Context:** 
> - Scoring function: `compute_control_coverage()` in `api/shared/scoring.py`
> - Current implementation: [reference existing code]
> - Requirements: [capability weights, minStrength, evidence factor]
> 
> **Edge Cases to Consider:**
> - Zero weights or sum != 1.0
> - Missing capabilities in catalog
> - No tenant tools for required capability
> - ConfigScore = 0 or capability strength = 0
> - Multiple tools covering same capability (use best)
> - Hard vs soft gap classification
> 
> **Verification:**
> - Unit tests must cover all edge cases
> - Verify explainability (can trace score back to inputs)
> - Check against ADR 0004 (scoring policy)

### Pattern 2: Security Architecture Review
**When to use:** Adding new API endpoints, changing data models, implementing tenant isolation, evidence handling.

**Template:**
> Apply Adversarial Prompting to review this design:
> 
> **Design:** [describe API endpoint, data model, or feature]
> 
> **Attack from 5 perspectives:**
> 1. **Security vulnerability:** Can tenant A access tenant B's data? Can unauthorized users bypass auth?
> 2. **Scoring accuracy:** Will this change affect scoring explainability or correctness?
> 3. **Compliance risk:** Does this handle evidence properly? Is audit trail maintained?
> 4. **Operational concern:** Will this scale? What's the cost impact?
> 5. **User experience:** Will consultants understand this? Can customers trust the results?
> 
> **Mitigations:** For each weakness, propose specific fixes.
> 
> **Improved Version:** Show the hardened design.

### Pattern 3: Validation Logic Development
**When to use:** Adding CSV import validation, schema validation, seed data validation.

**Template:**
> Apply Strategic Edge-Case Learning to implement validation for [entity type].
> 
> **Examples to Learn:**
> - [3 examples that should be rejected with subtle failures]
> - [1 example that should pass]
> 
> **Validation Rules:**
> - Schema compliance (JSON Schema reference)
> - Business rules (weight sums, numeric ranges, required fields)
> - Referential integrity (capabilities exist, tools exist)
> 
> **Implementation:**
> - Use `validate_seeds.py` pattern
> - Return clear error messages pointing to specific fields
> - Include line numbers for CSV imports

### Pattern 4: Feature Implementation (Multi-Step)
**When to use:** Implementing complex features (evidence upload, catalog editor, control detail page).

**Template:**
> Use Meta-Prompting to design and implement [feature].
> 
> **Step 1:** Design the optimal prompt for this feature (include role, input format, output schema, verification)
> 
> **Step 2:** Execute the prompt with SecAI Radar context:
> - Architecture: Azure Static Web Apps + Functions + Table/Blob Storage
> - Auth: Entra ID (SWA)
> - Tenant isolation: Required for all tenant-scoped endpoints
> - Explainability: Required for all scoring-related features
> 
> **Step 3:** Apply Chain of Verification to review the implementation
> 
> **Step 4:** Apply Multi-Persona review (consultant, customer, developer perspectives)

### Pattern 5: Documentation (ADRs, Wiki)
**When to use:** Writing ADRs, updating wiki documentation, creating developer guides.

**Template:**
> Apply Over-Instruction Template to document [topic].
> 
> **Do NOT summarize.** Include:
> - Implementation details with code examples
> - Edge cases and failure modes
> - Historical context (why this decision, related ADRs)
> - Compliance/security considerations
> - Troubleshooting guide
> 
> **For ADRs:** Follow template in `docs/adr/0000-template.md`
> - Context, Decision, Options Considered, Consequences, Follow-ups
> 
> **For Wiki:** Write for security consultants (non-developers)
> - Use clear language, avoid jargon
> - Include screenshots/mockups where helpful
> - Focus on "how to use" not "how it works"

---

## 5. High-Risk Task Defaults

For high-risk tasks (security, compliance, scoring accuracy), **default to:**

1. **Self-correction (Chain of Verification)** - Especially for scoring logic
2. **Adversarial review** - Especially for security architecture
3. **Reasoning scaffold** - Especially for troubleshooting
4. **Edge-case learning** - Especially for validation logic
5. **Multi-perspective** - Especially for feature prioritization

**High-Risk Tasks:**
- Scoring algorithm changes
- Tenant isolation mechanisms
- Evidence handling and retention
- Authentication/authorization
- Data validation (CSV imports, seed data)
- API endpoint design (security, tenant scoping)
- Compliance mapping (control requirements, capability taxonomy)

---

## 6. Starter Commands for Cursor

### For Scoring Logic
```
You have the SecAI Radar prompting policy defined in docs/PROMPTING-GUIDE.md. 
Apply Chain of Verification (3 phases) to [scoring task]. 
Ensure edge cases are covered and unit tests are included.
```

### For Security Review
```
You have the SecAI Radar prompting policy. 
Apply Adversarial Prompting to review this [design/implementation]. 
Attack from security, scoring accuracy, compliance, operational, and UX perspectives.
```

### For Feature Implementation
```
You have the SecAI Radar prompting policy. 
Use Meta-Prompting to design and implement [feature]. 
Then apply Chain of Verification and Multi-Persona review.
```

### For Troubleshooting
```
You have the SecAI Radar prompting policy. 
Apply Zero-to-Chain-of-Thought to troubleshoot this issue: [problem description].
Include relevant components, likely causes, evidence needed, and validation steps.
```

### For Documentation
```
You have the SecAI Radar prompting policy. 
Apply Over-Instruction Template to document [topic]. 
Do NOT summarize. Include implementation details, edge cases, failure modes, and historical context.
```

---

## 7. Quality Checklist

Before considering any implementation complete, verify:

- [ ] **Scoring accuracy:** Math verified, edge cases tested, explainable
- [ ] **Security:** Tenant isolation verified, auth enforced, input validated
- [ ] **Compliance:** Evidence handling correct, audit trail maintained
- [ ] **Validation:** Schema validation, business rules, error messages clear
- [ ] **Documentation:** ADRs updated if architecture changed, wiki updated if user-facing
- [ ] **Tests:** Unit tests for scoring/validation, integration tests for API
- [ ] **Explainability:** Can trace score back to inputs, recommendations are actionable

---

## 8. Reminders

- **Explainability is non-negotiable:** Every score must be reproducible and explainable
- **Tenant isolation is critical:** All tenant-scoped endpoints must enforce isolation
- **Vendor-neutral by design:** Don't assume specific tools; use capability mapping
- **Cost-first architecture:** Prefer Azure-native, low-cost solutions (Tables/Blobs over Cosmos)
- **Consultant-friendly UX:** Prioritize explainability and workflow efficiency
- **Evidence matters:** Proper handling and retention per ADR 0005

---

**Version:** 1.0  
**Date:** 2025-01-XX  
**Related:** `docs/SEC_AI_Radar_Brief.md`, `docs/adr/`, `docs/backlog.md`

