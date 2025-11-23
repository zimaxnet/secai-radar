# SecAI Radar - Complete User Journey

> **Purpose:** Complete end-to-end user journey for conducting a SecAI Framework assessment from start to finish

---

## Journey Overview

The SecAI Radar application guides users through a complete security assessment using the SecAI Framework. The journey is designed to be:

- **Guided:** Clear next steps at every stage
- **Professional:** Production-ready, polished UI
- **Complete:** From first visit to final report
- **Resumable:** Can pause and continue at any time
- **Framework-Focused:** SecAI Framework prominently explained and referenced

---

## Complete User Flow

### Phase 1: Landing & Introduction

**Route:** `/`

**Purpose:** Welcome users and explain SecAI Framework

**Content:**
- Hero section introducing SecAI Radar
- Explanation of SecAI Framework (vendor-neutral, capability-driven)
- Key benefits and features
- How it works (5-step process)
- 12 security domains overview
- Clear call-to-action buttons

**User Actions:**
- Click "Start New Assessment" → Navigate to Assessments page
- Click "Continue Assessment" → Navigate to Assessments page

---

### Phase 2: Assessment Selection

**Route:** `/assessments`

**Purpose:** Select existing assessment or create new one

**Content:**
- List of existing assessments with:
  - Tenant/customer name
  - Progress percentage
  - Status (Not Started, In Progress, Complete)
  - Last updated date
  - Controls completed
- "Start New Assessment" button
- Create new assessment form

**User Actions:**
- Click existing assessment → Navigate to Assessment Overview
- Click "Start New Assessment" → Show creation form
- Fill form and create → Navigate to Assessment Setup

---

### Phase 3: Assessment Setup (Onboarding)

**Route:** `/tenant/{tenantId}/setup`

**Purpose:** Configure assessment before starting

**Wizard Steps:**

1. **Welcome**
   - Introduction to setup process
   - Overview of what will be configured
   - SecAI Framework explanation

2. **Tool Inventory**
   - Explanation of tool inventory
   - Link to tools management (can be done later)
   - Guidance on tool configuration

3. **Scope Selection**
   - Select which security domains to assess
   - All 12 domains shown with descriptions
   - Pre-select all (recommended)
   - Custom selection allowed

4. **Review & Start**
   - Summary of configuration
   - Tools: X selected
   - Domains: X selected
   - "Start Assessment" button

**User Actions:**
- Complete setup → Navigate to Assessment Overview
- Can skip steps and configure later

---

### Phase 4: Assessment Overview (Central Hub)

**Route:** `/tenant/{tenantId}/assessment`

**Purpose:** Central hub showing overall assessment progress

**Content:**
- **Assessment Header:**
  - Tenant name
  - Assessment status badge
  - Overall progress bar
  - Last updated

- **Quick Stats:**
  - Controls: X/Y complete
  - Domains: X/Y complete
  - Gaps: X identified
  - Status indicator

- **Recommended Next Action:**
  - Prominent call-to-action
  - "Continue Assessment" or "Import Controls" or "Review Gaps"
  - Direct link to next step

- **Domain Progress Cards:**
  - All 12 security domains
  - Progress bars
  - Status indicators
  - Click to navigate to domain

- **Quick Actions:**
  - Controls, Gaps, Tools, Report links

**User Actions:**
- Click domain card → Navigate to Domain Assessment
- Click "Continue Assessment" → Resume at last active point
- Click quick actions → Navigate to respective pages

---

### Phase 5: Domain Assessment

**Route:** `/tenant/{tenantId}/domain/{domainCode}`

**Purpose:** Work through all controls in a security domain

**Content:**
- **Domain Header:**
  - Domain name and code
  - **Prominent domain description** (explains what this domain covers)
  - Framework mappings (CIS, NIST, Azure Security Benchmark)
  - Domain progress bar

- **Domain Context:**
  - What this domain covers
  - Key capabilities assessed
  - Common tools used

- **Controls List:**
  - All controls for this domain
  - Status badges (Not Started, In Progress, Complete)
  - Coverage scores with color coding
  - Gap indicators
  - Clickable to navigate to control detail

- **Domain Actions:**
  - Status filter
  - Export domain report
  - View domain gaps

**User Actions:**
- Click control → Navigate to Control Detail
- Work through controls sequentially (recommended)
- Filter by status
- Return to Assessment Overview

---

### Phase 6: Control Assessment

**Route:** `/tenant/{tenantId}/control/{controlId}`

**Purpose:** Complete assessment for a single control

**Content (in order):**

1. **Control Header:**
   - Control ID and title
   - Breadcrumb navigation
   - Coverage score (if calculated)

2. **Control Description (Prominent):**
   - Full control description
   - Question to answer
   - Required evidence types
   - Framework reference links

3. **Gap Analysis:**
   - Hard gaps (missing capabilities)
   - Soft gaps (configuration issues)
   - Coverage calculation explanation

4. **AI Recommendations:**
   - On-demand AI recommendations
   - Actionable remediation steps
   - Tool tuning suggestions

5. **Observations & Notes:**
   - Text area for findings
   - Status selection
   - Owner assignment

6. **Evidence Collection:**
   - Upload evidence files
   - Evidence list with classifications
   - Download evidence

7. **Control Actions:**
   - Mark as Complete
   - Save & Continue
   - Navigate to next control

**User Actions:**
- Upload evidence
- Enter observations
- Review gaps
- Get AI recommendations
- Mark control complete
- Navigate to next/previous control

---

### Phase 7: Gap Review

**Route:** `/tenant/{tenantId}/gaps`

**Purpose:** Review all identified gaps

**Content:**
- Gaps summary (total, hard, soft)
- List of all controls with gaps
- Gap details (type, capability, recommendations)
- AI recommendations toggle
- Filter by domain, gap type

**User Actions:**
- Review gaps
- Get AI recommendations
- Navigate to controls to address gaps
- Export gaps report

---

### Phase 8: Report Generation

**Route:** `/tenant/{tenantId}/report`

**Purpose:** Generate final assessment report

**Content:**
- Report generation options
- AI executive summary (optional)
- Assessment summary
- Domain breakdown
- Gaps summary
- Download options (TXT, JSON)

**User Actions:**
- Generate report
- Download report
- Share report

---

## Navigation Structure

### Main Routes

```
/ (Landing)
├── /assessments (Assessment Selection)
│   └── /tenant/{tenantId}/setup (Assessment Setup)
│       └── /tenant/{tenantId}/assessment (Assessment Overview)
│           ├── /tenant/{tenantId}/domain/{domainCode} (Domain Assessment)
│           │   └── /tenant/{tenantId}/control/{controlId} (Control Detail)
│           ├── /tenant/{tenantId}/controls (All Controls)
│           ├── /tenant/{tenantId}/tools (Tool Inventory)
│           ├── /tenant/{tenantId}/gaps (Gaps Review)
│           └── /tenant/{tenantId}/report (Report Generation)
```

### Breadcrumb Navigation

Every page shows context:
- Control Detail: `Assessment / Domain / Control`
- Domain: `Assessment / Domain`
- Assessment Overview: `Assessment`

---

## Progress Tracking

### Assessment-Level Progress
- Overall: X% complete
- Controls: X/Y complete
- Domains: X/Y complete
- Gaps: X identified

### Domain-Level Progress
- Domain: X/Y controls complete
- Progress bar
- Status indicators

### Control-Level Progress
- Control status (Not Started, In Progress, Complete)
- Coverage score
- Evidence status
- Observations status

---

## Key Features

### 1. Framework Prominence
- SecAI Framework explained on landing page
- Framework references on every domain page
- Framework mappings clearly displayed

### 2. Guided Workflow
- Clear next actions at every step
- Progress indicators throughout
- Recommended workflow paths

### 3. Professional Presentation
- Clean, modern UI
- Consistent design language
- Clear hierarchy and typography
- Professional color scheme

### 4. Complete Journey
- Start: Landing page
- Setup: Assessment configuration
- Work: Domain-by-domain assessment
- Review: Gap analysis
- Complete: Report generation

### 5. Resumable
- Can pause at any time
- Progress saved automatically
- "Continue Assessment" functionality
- Last active point remembered

---

## User Personas

### Consultant (Primary User)
- **Goal:** Complete assessment for customer
- **Journey:** Setup → Work through domains → Generate report
- **Needs:** Clear workflow, progress tracking, evidence management

### Customer (Stakeholder)
- **Goal:** Understand security posture
- **Journey:** Review assessment → See gaps → Understand recommendations
- **Needs:** Clear explanations, visual progress, actionable insights

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

## Next Steps for Production

1. **Tenant Management API:**
   - List all tenants
   - Create new tenant
   - Update tenant metadata

2. **Progress Persistence:**
   - Save last active domain/control
   - Track assessment state
   - Resume functionality

3. **Assessment Templates:**
   - Pre-configured assessment types
   - Industry-specific templates
   - Custom templates

4. **Collaboration:**
   - Multiple users per assessment
   - Assignment of controls
   - Comments and discussions

5. **Advanced Reporting:**
   - Excel export
   - PDF generation
   - Custom report templates
   - Scheduled reports

---

## Design Principles

1. **Framework-First:** SecAI Framework is always prominent
2. **Guided Experience:** Never leave users wondering what's next
3. **Progress Visibility:** Always show where you are
4. **Professional Polish:** Production-ready, not MVP
5. **Complete Journey:** Start to finish, no dead ends
6. **Resumable:** Can pause and continue seamlessly

---

**This journey ensures consultants and customers can successfully complete a SecAI Framework assessment from start to finish, with clear guidance, professional presentation, and complete functionality.**

