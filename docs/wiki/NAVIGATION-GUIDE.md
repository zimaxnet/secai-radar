# SecAI Radar - Navigation Guide

> **Purpose:** Guide for navigating the SecAI Radar application and accessing all features

---

## Application Structure

SecAI Radar is organized around **Security Domains**, with each domain containing multiple **Controls**. The workflow is designed for consultants and customers to work through assessments systematically.

---

## Navigation Flow

### 1. **Dashboard** (`/tenant/{tenantId}/dashboard`)
**Entry Point:** Start here to see an overview of all security domains.

**Features:**
- Domain cards showing progress (complete/total controls)
- Visual progress bars for each domain
- Radar chart showing overall progress
- **Click any domain card** to navigate to that domain's assessment page

**Navigation:**
- Click domain cards → Domain Assessment Page
- Use top navigation → Controls, Tools, Gaps

---

### 2. **Domain Assessment Pages** (`/tenant/{tenantId}/domain/{domainCode}`)
**Access:** Click any domain card on the Dashboard, or click a domain link in the Controls table.

**Features:**
- **Prominent domain description** at the top
- **Framework mappings** (CIS, NIST, Azure Security Benchmark)
- **Progress tracking** with visual indicators
- **Domain-level gap summary**
- **Controls list** with:
  - Status filtering (Complete, In Progress, Not Started)
  - Coverage indicators
  - Gap indicators
  - Clickable links to individual controls

**Navigation:**
- Click any control → Control Detail Page
- Back to Dashboard link
- Use top navigation for other sections

**Example URLs:**
- `/tenant/NICO/domain/NET` - Network Security domain
- `/tenant/NICO/domain/ID` - Identity Management domain
- `/tenant/NICO/domain/PA` - Privileged Access domain

---

### 3. **Control Detail Page** (`/tenant/{tenantId}/control/{controlId}`)
**Access:** Click any control ID from:
- Domain Assessment Page
- Controls table
- Gaps page

**Features:**
- **Control description** prominently displayed
- **Framework reference** links
- **Capability breakdown** (hard/soft gaps)
- **Coverage score** with visual indicator
- **AI recommendations** (on-demand)
- **Observations/Notes** section
- **Evidence upload and display**
- **Control metadata** (status, owner, frequency)

**Navigation:**
- Back to Domain link
- Upload evidence button
- Generate AI recommendation button

**Example URLs:**
- `/tenant/NICO/control/SEC-NET-0001` - Network control
- `/tenant/NICO/control/SEC-LOG-0001` - Logging control

---

### 4. **Controls Page** (`/tenant/{tenantId}/controls`)
**Access:** Top navigation → Controls

**Features:**
- Table view of all controls
- Filter by domain, status, or search
- CSV import functionality
- **Clickable links:**
  - Control ID → Control Detail Page
  - Domain → Domain Assessment Page

**Use Cases:**
- Quick search for specific controls
- Bulk import of controls via CSV
- Overview of all controls across domains

---

### 5. **Gaps Page** (`/tenant/{tenantId}/gaps`)
**Access:** Top navigation → Gaps

**Features:**
- List of all controls with gaps
- Hard gaps (missing capabilities)
- Soft gaps (configuration issues)
- **AI Recommendations toggle**
- **On-demand AI recommendations** per control

**Navigation:**
- Enable AI toggle to see AI-powered recommendations
- Click "Get AI Recommendation" for specific controls

---

### 6. **Tools Page** (`/tenant/{tenantId}/tools`)
**Access:** Top navigation → Tools

**Features:**
- Tenant tool inventory
- Enable/disable tools
- Set configuration scores
- Tool owner and notes

---

## Quick Access Patterns

### Pattern 1: Domain-First Workflow (Recommended)
1. **Dashboard** → See all domains
2. **Click domain card** → Domain Assessment Page
3. **Review domain description and frameworks**
4. **Click control** → Control Detail Page
5. **Enter observations, upload evidence**
6. **View gaps and AI recommendations**
7. **Back to domain** → Continue with next control

### Pattern 2: Control-First Workflow
1. **Controls page** → Search/filter for specific control
2. **Click control ID** → Control Detail Page
3. **Work through control details**
4. **Click domain link** → See all controls in that domain

### Pattern 3: Gap-First Workflow
1. **Gaps page** → See all controls with gaps
2. **Enable AI recommendations** → Get AI insights
3. **Click control** → Control Detail Page (if linked)
4. **Address gaps** → Update observations, upload evidence

---

## URL Structure

All URLs follow this pattern:
```
/tenant/{tenantId}/{page}/{identifier}
```

**Examples:**
- `/tenant/NICO/dashboard` - Dashboard
- `/tenant/NICO/domain/NET` - Network Security domain
- `/tenant/NICO/control/SEC-NET-0001` - Specific control
- `/tenant/NICO/controls` - All controls
- `/tenant/NICO/gaps` - All gaps
- `/tenant/NICO/tools` - Tools inventory

---

## Visual Design Elements

### Domain Cards (Dashboard)
- **Gradient header** (blue) with domain name
- **Progress bar** showing completion percentage
- **Status counts** (Complete, In Progress, Not Started)
- **Hover effects** for interactivity

### Domain Assessment Pages
- **Prominent header** with domain description
- **Framework badges** showing mapped frameworks
- **Progress tracking** with visual indicators
- **Gap summary** alerts
- **Controls list** with status badges

### Control Detail Pages
- **Clear hierarchy** with control ID and title
- **Coverage score** prominently displayed
- **Color-coded gaps** (red for hard, orange for soft)
- **AI recommendations** in highlighted boxes
- **Evidence section** with upload capability

---

## Troubleshooting

### "Pages don't reflect changes"
1. **Hard refresh** the browser (Ctrl+Shift+R or Cmd+Shift+R)
2. **Clear browser cache**
3. **Check if deployment completed** - verify latest commit is deployed
4. **Check browser console** for JavaScript errors

### "Can't see domain pages"
1. **Ensure you're on the Dashboard** - domain cards should be visible
2. **Check if domains have data** - domains only show if controls exist
3. **Verify API is working** - check browser network tab
4. **Check tenant ID** - ensure you're using the correct tenant

### "Links not working"
1. **Check URL format** - should be `/tenant/{tenantId}/domain/{domainCode}`
2. **Verify routing** - check browser console for routing errors
3. **Check tenant ID** - must match your tenant identifier

---

## Best Practices

1. **Start at Dashboard** - Get overview before diving into details
2. **Work by Domain** - Complete all controls in a domain before moving to next
3. **Use Domain Pages** - Best way to see domain context and frameworks
4. **Enable AI when needed** - Use AI recommendations for complex gaps
5. **Upload evidence as you go** - Don't wait until the end
6. **Use observations** - Document findings in real-time

---

## Next Steps

If pages still don't reflect changes:
1. Verify the latest code is deployed
2. Check browser console for errors
3. Verify API endpoints are responding
4. Check that data exists (controls, domains, etc.)

For development:
- Run `npm run dev` locally to see changes immediately
- Check `web/dist` folder after build
- Verify routes in `App.tsx` are correct

