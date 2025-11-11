---
layout: default
title: Getting Started
permalink: /Getting-Started/
---

# Getting Started with SecAI Radar

This guide will help you get started with SecAI Radar quickly.

---

## Prerequisites

Before you begin, ensure you have:

- Access to a cloud environment (Azure, AWS, or GCP)
- API credentials for your cloud provider
- (Optional) Azure OpenAI API access for AI features
- Modern web browser (Chrome, Firefox, Safari, or Edge)

---

## Quick Start

### 1. Access the Application

Navigate to the SecAI Radar application URL. If you're setting up locally, see the [Installation](/wiki/Installation) guide.

### 2. Select Your Tenant

When you first access the application, you'll need to select or enter a tenant identifier. The tenant ID is used to scope all assessments and data.

### 3. Navigate to Dashboard

Once logged in, you'll see the main dashboard showing:
- Overall security posture
- Control counts by status
- Domain-based metrics
- Compliance overview

---

## Your First Assessment

### Step 1: Configure Security Tools

Before running an assessment, configure your security tools:

1. Navigate to **Tools** page
2. Click **Add Tool Configuration**
3. Enter:
   - **Vendor Tool ID**: e.g., `wiz-cspm`, `crowdstrike-falcon`
   - **Enabled**: Check if tool is active
   - **Configuration Score**: 0.0 - 1.0 (quality of tool configuration)
4. Click **Save Tool Configuration**

See [Tools Guide](/wiki/Tools-Guide) for detailed information.

### Step 2: Import Controls

Import security controls for assessment:

1. Navigate to **Controls** page
2. Click **Import CSV**
3. Prepare CSV with required headers:
   ```
   ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,
   Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
   ```
4. Paste CSV content and click **Import Controls**

See [Controls Guide](/wiki/Controls-Guide) for CSV format details.

### Step 3: View Dashboard

Navigate to **Dashboard** to see:
- Overall compliance metrics
- Domain breakdown
- Control status summary
- Radar chart visualization

### Step 4: Analyze Gaps

Navigate to **Gaps** page to:
- View capability coverage analysis
- Identify hard gaps (missing capabilities)
- Review soft gaps (configuration issues)
- Get remediation recommendations

---

## Common Tasks

### Viewing Controls

1. Go to **Controls** page
2. Use filters to find specific controls:
   - **Domain**: Filter by security domain (e.g., NET, IDM, LOG)
   - **Status**: Filter by status (Complete, InProgress, NotStarted)
   - **Search**: Search by control ID or title

### Updating Tool Configuration

1. Go to **Tools** page
2. Enter tool ID and configuration score
3. Adjust configuration score slider (0.0 - 1.0)
4. Click **Save Tool Configuration**

### Understanding Gaps

1. Go to **Gaps** page
2. Review coverage percentage for each control
3. Check **Hard Gaps** for missing capabilities
4. Review **Soft Gaps** for configuration improvements
5. Prioritize tuning existing tools before adding new ones

---

## Next Steps

- Read the [User Guide](/wiki/User-Guide) for detailed usage instructions
- Explore the [Dashboard Guide](/wiki/Dashboard-Guide) to understand metrics
- Check the [FAQ](/wiki/FAQ) for common questions
- Review [Architecture](/wiki/Architecture) for system overview

---

## Tips for Success

1. **Start Small**: Begin with a single domain or a few controls
2. **Configure Tools First**: Set up your security tools before importing controls
3. **Review Regularly**: Check gaps regularly and update configuration scores
4. **Prioritize Tuning**: Often better to improve existing tool configurations than add new tools
5. **Use Filters**: Use filters to focus on specific domains or statuses

---

**Need Help?** Check the [FAQ](/wiki/FAQ) or [Troubleshooting](/wiki/Troubleshooting) guides.

