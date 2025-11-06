# Complete User Journey

> **Complete end-to-end user journey for conducting a SecAI Framework assessment from start to finish**

---

## Journey Overview

The SecAI Radar assessment journey is designed to guide users through a complete security assessment using the SecAI Framework. The journey is structured in clear phases with progress tracking and clear next steps.

---

## Phase 1: Welcome & Introduction

### Landing Page (`/`)
**Purpose:** Introduce SecAI Radar and the SecAI Framework

**Content:**
- **Hero Section:**
  - "SecAI Radar - Azure Security Assessment Platform"
  - "Vendor-neutral, capability-driven security assessments"
  - "Based on the SecAI Framework"
  
- **What is SecAI Framework:**
  - Brief explanation of capability-based assessment
  - Framework benefits (vendor-neutral, explainable, actionable)
  - Key features (12 security domains, control mapping, gap analysis)

- **Call to Action:**
  - "Start New Assessment" button
  - "Continue Existing Assessment" button
  - "Learn More" link

**User Actions:**
- New user: Click "Start New Assessment"
- Returning user: Click "Continue Existing Assessment"

---

## Phase 2: Tenant Selection & Setup

### Tenant Selection Page (`/assessments`)
**Purpose:** Select or create a customer/tenant for assessment

**Content:**
- **Existing Assessments:**
  - List of existing tenants/assessments
  - Show: Tenant name, last updated, progress, status
  - "Continue Assessment" button for each

- **New Assessment:**
  - "Start New Assessment" button
  - Opens tenant creation form

**Tenant Creation Form:**
- Customer/Organization name
- Tenant ID (auto-generated or custom)
- Assessment type (Initial, Follow-up, Audit)
- Start date
- Target completion date (optional)

**User Actions:**
- Select existing tenant → Continue to Assessment Overview
- Create new tenant → Continue to Assessment Setup

---

## Phase 3: Assessment Setup (Onboarding)

### Assessment Setup Wizard (`/tenant/{tenantId}/setup`)
**Purpose:** Configure the assessment before starting

**Steps:**

1. **Welcome Step:**
   - "Welcome to SecAI Assessment Setup"
   - Overview of what will be configured
   - Estimated time: 5-10 minutes

2. **Tool Inventory Step:**
   - "What security tools does this customer use?"
   - Show catalog of available tools
   - Enable/disable tools
   - Set initial configuration scores
   - "We'll refine these as we go"

3. **Scope Selection Step:**
   - "Which security domains should we assess?"
   - Show all 12 domains with descriptions
   - Pre-select all (recommended)
   - Allow customization
   - Show estimated controls per domain

4. **Review & Start Step:**
   - Summary of configuration
   - Tools selected: X tools
   - Domains selected: X domains
   - Estimated controls: X controls
   - "Start Assessment" button

**User Actions:**
- Complete setup → Navigate to Assessment Overview
- Save & continue later → Save progress, return to tenant selection

---

## Phase 4: Assessment Overview

### Assessment Dashboard (`/tenant/{tenantId}/assessment`)
**Purpose:** Central hub showing overall assessment progress

**Content:**
- **Assessment Header:**
  - Tenant name
  - Assessment status (Not Started, In Progress, Review, Complete)
  - Overall progress: X% complete
  - Last updated: [date]

- **Progress Overview:**
  - Visual progress bar
  - Controls: X/Y complete
  - Domains: X/Y complete
  - Evidence: X items uploaded
  - Gaps: X identified

- **Domain Progress Cards:**
  - All 12 security domains
  - Progress indicator per domain
  - Status: Not Started, In Progress, Complete
  - "Start" or "Continue" button

- **Quick Actions:**
  - "Continue Assessment" (resume where left off)
  - "View All Gaps"
  - "Generate Report" (when ready)
  - "Export Data"

- **Assessment Timeline:**
  - Key milestones
  - Next recommended action

**User Actions:**
- Click domain card → Navigate to Domain Assessment
- Click "Continue Assessment" → Resume at last active domain/control
- Click "View All Gaps" → Navigate to Gaps page

---

## Phase 5: Domain-by-Domain Assessment

### Domain Assessment Page (`/tenant/{tenantId}/domain/{domainCode}`)
**Purpose:** Work through all controls in a security domain

**Content:**
- **Domain Header:**
  - Domain name and code (e.g., "NET: Network Security")
  - **Prominent domain description**
  - Framework mappings (CIS, NIST, Azure Security Benchmark)
  - Domain progress: X/Y controls complete

- **Domain Context:**
  - "What this domain covers"
  - Key capabilities assessed
  - Common tools used

- **Controls List:**
  - All controls for this domain
  - Status indicators (Not Started, In Progress, Complete)
  - Coverage scores
  - Gap indicators
  - "Start" or "Continue" button per control

- **Domain Actions:**
  - "Mark Domain Complete" (when all controls done)
  - "Export Domain Report"
  - "View Domain Gaps"

**User Actions:**
- Click control → Navigate to Control Detail
- Work through controls in order (recommended)
- Or jump to specific controls

---

## Phase 6: Control Assessment

### Control Detail Page (`/tenant/{tenantId}/control/{controlId}`)
**Purpose:** Complete assessment for a single control

**Content:**
- **Control Header:**
  - Control ID and title
  - **Prominent control description**
  - Framework reference links
  - Coverage score (if calculated)

- **Assessment Sections (in order):**

  1. **Understanding the Control:**
     - Description
     - Question to answer
     - Required evidence types
     - Framework references

  2. **Evidence Collection:**
     - Upload evidence files
     - Link to external evidence
     - Evidence list with classifications
     - "Evidence complete" checkbox

  3. **Observations & Findings:**
     - Text area for observations
     - Findings and notes
     - Status selection (Not Started, In Progress, Complete, Not Applicable)
     - Owner assignment

  4. **Gap Analysis:**
     - Capability requirements
     - Hard gaps (missing capabilities)
     - Soft gaps (configuration issues)
     - Coverage calculation explanation

  5. **AI Recommendations:**
     - Generate AI recommendations (on-demand)
     - Actionable remediation steps
     - Tool tuning suggestions

  6. **Control Status:**
   - Mark as Complete
   - Save & Continue
   - Next Control button

**User Actions:**
- Upload evidence
- Enter observations
- Review gaps
- Get AI recommendations
- Mark control complete
- Navigate to next control

---

## Phase 7: Gap Review & Remediation

### Gaps Overview Page (`/tenant/{tenantId}/gaps`)
**Purpose:** Review all identified gaps across the assessment

**Content:**
- **Gaps Summary:**
  - Total gaps: X
  - Hard gaps: X (critical)
  - Soft gaps: X (configuration)
  - By domain breakdown

- **Gaps List:**
  - All controls with gaps
  - Gap type (hard/soft)
  - Capability missing
  - Recommended actions
  - AI recommendations (if enabled)

- **Actions:**
  - Filter by domain, gap type, severity
  - Export gaps report
  - Generate remediation plan

**User Actions:**
- Review gaps
- Get AI recommendations
- Export gaps report
- Navigate to controls to address gaps

---

## Phase 8: Assessment Completion

### Assessment Review Page (`/tenant/{tenantId}/review`)
**Purpose:** Review assessment before finalizing

**Content:**
- **Completion Checklist:**
  - All domains assessed
  - All controls reviewed
  - Evidence collected
  - Gaps documented
  - Observations entered

- **Assessment Summary:**
  - Overall coverage score
  - Domain breakdown
  - Gap summary
  - Evidence summary

- **Final Actions:**
  - "Mark Assessment Complete"
  - "Generate Final Report"
  - "Export Assessment Data"
  - "Create Follow-up Assessment"

---

## Phase 9: Report Generation

### Report Generation Page (`/tenant/{tenantId}/report`)
**Purpose:** Generate final assessment report

**Content:**
- **Report Options:**
  - Executive Summary (AI-generated)
  - Full Assessment Report
  - Gaps Report
  - Evidence Index
  - Excel Export

- **Report Preview:**
  - Preview generated report
  - Download options
  - Share options

**User Actions:**
- Generate report
- Download report
- Share report

---

## Navigation Structure

### Main Navigation (Always Visible)
```
SecAI Radar
├── Assessments (tenant selection)
├── Current Assessment
│   ├── Overview
│   ├── Domains
│   ├── Controls
│   ├── Gaps
│   ├── Tools
│   └── Report
└── Help & Documentation
```

### Breadcrumbs (Context Navigation)
```
Home > Assessments > [Tenant Name] > Assessment Overview > Domain: NET > Control: SEC-NET-0001
```

---

## Progress Tracking

### Assessment Progress Indicators
- **Overall Progress:** X% complete
- **Domain Progress:** X/Y domains complete
- **Control Progress:** X/Y controls complete
- **Evidence Progress:** X/Y controls have evidence
- **Gap Progress:** X/Y gaps addressed

### Visual Progress Indicators
- Progress bars at assessment, domain, and control levels
- Status badges (Not Started, In Progress, Complete)
- Completion checkmarks
- Next action indicators

---

## Key User Flows

### Flow 1: New Assessment (First Time)
1. Landing Page → Learn about SecAI
2. Start New Assessment → Tenant Creation
3. Assessment Setup → Configure tools and scope
4. Assessment Overview → See all domains
5. Start Domain → Begin with first domain
6. Work Through Controls → Complete controls in domain
7. Complete Domain → Move to next domain
8. Review Gaps → Address identified gaps
9. Complete Assessment → Finalize assessment
10. Generate Report → Create final report

### Flow 2: Continue Assessment (Returning User)
1. Landing Page → Continue Existing Assessment
2. Tenant Selection → Select tenant
3. Assessment Overview → See progress
4. Continue Assessment → Resume at last active point
5. Complete remaining work
6. Generate Report

### Flow 3: Domain-Focused Workflow
1. Assessment Overview → Select domain
2. Domain Assessment → See all controls in domain
3. Work through controls sequentially
4. Complete domain
5. Return to Overview → Select next domain

---

## Design Principles

1. **Guided Experience:** Always show what to do next
2. **Progress Visibility:** Always show where you are in the journey
3. **Context Preservation:** Remember where user left off
4. **Clear Hierarchy:** Domain → Control → Evidence → Gaps
5. **Professional Presentation:** Clean, modern, trustworthy UI
6. **Framework Prominence:** SecAI Framework clearly explained and referenced
7. **Completion Focus:** Clear path to assessment completion

---

## Success Criteria

An assessment is complete when:
1. ✅ All selected domains assessed
2. ✅ All controls reviewed
3. ✅ Evidence collected (where required)
4. ✅ Observations entered
5. ✅ Gaps documented
6. ✅ Report generated

---

**This journey ensures consultants and customers can successfully complete a SecAI Framework assessment from start to finish, with clear guidance, professional presentation, and complete functionality.**

