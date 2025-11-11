---
layout: default
title: User Guide
permalink: /User-Guide/
---

# SecAI Radar User Guide

Complete guide to using SecAI Radar for cloud security assessments.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Complete User Journey](#complete-user-journey)
4. [Navigation](#navigation)
5. [Dashboard](#dashboard)
6. [Controls](#controls)
7. [Tools](#tools)
8. [Gaps](#gaps)
9. [Report Generation](#report-generation)
10. [Best Practices](#best-practices)

---

## Overview

SecAI Radar provides a web-based interface for managing cloud security assessments using the SecAI Framework. The application guides users through a complete assessment journey from initial setup to final report generation.

### Key Features

- **Vendor-Neutral Assessment**: Capability-driven approach that works with any security tool stack
- **Complete Journey**: From landing page to assessment completion
- **Domain-Based Workflow**: Work through 12 security domains systematically
- **AI-Powered Insights**: Get recommendations and gap analysis
- **Evidence Management**: Upload and classify evidence for each control
- **Progress Tracking**: Visual progress indicators at all levels

---

## Getting Started

### First Time Users

1. **Visit the Landing Page**: Learn about SecAI Framework and the assessment process
2. **Start New Assessment**: Create a new tenant/assessment
3. **Complete Setup Wizard**: Configure tools and select domains
4. **Begin Assessment**: Work through domains and controls

### Returning Users

1. **Continue Assessment**: Select existing assessment from the assessments page
2. **Resume Work**: Continue where you left off
3. **Review Progress**: Check overall progress and next actions

For a complete walkthrough, see the [User Journey](User-Journey) guide.

---

## Complete User Journey

The SecAI Radar assessment follows a structured journey:

1. **Landing & Introduction** - Learn about SecAI Framework
2. **Assessment Selection** - Choose or create an assessment
3. **Assessment Setup** - Configure tools and scope
4. **Assessment Overview** - Central hub with progress tracking
5. **Domain Assessment** - Work through security domains
6. **Control Assessment** - Complete individual controls
7. **Gap Review** - Review and address identified gaps
8. **Report Generation** - Generate final assessment report

See the [User Journey](User-Journey) page for detailed information about each phase.

---

## Navigation

### Header Navigation

The header displays:
- **Application Name**: "SecAI Radar"
- **Tenant ID**: Current tenant identifier
- **Navigation Links**: Dashboard, Controls, Tools, Gaps

### Active Page Indicator

The current page is highlighted in the navigation bar with a dark background.

### Breadcrumbs

Pages show their location in the application hierarchy.

---

## Dashboard

The Dashboard provides a comprehensive overview of your security posture.

### Overall Statistics

Four key metrics cards:
- **Total Controls**: Total number of controls assessed
- **Complete**: Number of controls marked as complete
- **In Progress**: Number of controls currently in progress
- **Not Started**: Number of controls not yet started

### Domain Breakdown

Each security domain shows:
- Domain name
- Total controls
- Complete, In Progress, Not Started counts
- Compliance percentage
- Progress bar

### Compliance Overview

Radar chart showing:
- Compliance status across domains
- Visual comparison of Complete, In Progress, Not Started
- Domain-specific metrics

### Using the Dashboard

1. **View Overall Metrics**: Check the top cards for quick status
2. **Review Domain Status**: Scroll through domain cards for detailed breakdown
3. **Analyze Trends**: Use radar chart to identify domains needing attention
4. **Navigate to Details**: Click on domains or use filters to drill down

See [Dashboard Guide](/wiki/Dashboard-Guide) for detailed information.

---

## Controls

The Controls page manages security control assessments.

### Control List

Table showing:
- **Control ID**: Unique identifier
- **Domain**: Security domain
- **Title**: Control title
- **Status**: Current status (Complete, InProgress, NotStarted)
- **Owner**: Control owner

### Filters

Use filters to find specific controls:
- **Domain**: Filter by security domain (e.g., NET, IDM, LOG)
- **Status**: Filter by status
- **Search**: Search by control ID or title

### Importing Controls

1. Click **Import CSV** button
2. Prepare CSV with required headers:
   ```
   ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,
   Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
   ```
3. Paste CSV content into text area
4. Click **Import Controls**
5. Review success/error messages

### CSV Format

Required columns:
- `ControlID`: Unique control identifier (e.g., SEC-NET-0001)
- `Domain`: Security domain code (e.g., NET, IDM)
- `ControlTitle`: Human-readable control title
- `ControlDescription`: Detailed description
- `Status`: Complete, InProgress, NotStarted, NotApplicable
- Additional fields as needed

See [Controls Guide](/wiki/Controls-Guide) for detailed CSV format.

---

## Tools

The Tools page manages security tool configurations.

### Adding a Tool

1. Enter **Vendor Tool ID**:
   - Use standard tool identifiers (e.g., `wiz-cspm`, `crowdstrike-falcon`)
   - Check available tools in the catalog
2. **Enable/Disable**: Toggle tool activation
3. **Configuration Score**: Set quality score (0.0 - 1.0)
   - Use slider or enter value directly
   - Higher scores indicate better configuration
4. Click **Save Tool Configuration**

### Configuration Score Guide

- **0.9 - 1.0**: Excellent configuration, fully optimized
- **0.7 - 0.89**: Good configuration, minor improvements possible
- **0.5 - 0.69**: Fair configuration, significant improvements needed
- **0.0 - 0.49**: Poor configuration, major improvements required

### Tool Tips

- **Prioritize Tuning**: Improve existing tool configurations before adding new tools
- **Regular Updates**: Update configuration scores as tools are tuned
- **Accurate Scoring**: Use realistic scores based on actual configuration quality

See [Tools Guide](/wiki/Tools-Guide) for detailed information.

---

## Gaps

The Gaps page analyzes capability coverage and identifies security gaps.

### Gap Analysis

For each control, you'll see:
- **Control ID**: Control identifier
- **Coverage Percentage**: Overall capability coverage (0-100%)
- **Status Badge**: Good/Fair/Poor based on coverage
- **Hard Gaps**: Missing capabilities (no tool coverage)
- **Soft Gaps**: Configuration issues (tool exists but misconfigured)

### Hard Gaps

Hard gaps indicate:
- Missing capabilities
- No tool provides the required capability
- May require adding new tools

### Soft Gaps

Soft gaps indicate:
- Capabilities exist but are misconfigured
- Configuration scores too low
- Can often be fixed by improving tool configuration

### Understanding Coverage

Coverage calculation:
- Each control has required capabilities with weights
- Best tool for each capability is selected (strength × configScore)
- Coverage = weighted sum of best tool coverage

### Remediation Priority

1. **Tune Existing Tools**: Improve configuration scores first
2. **Review Soft Gaps**: Address configuration issues
3. **Add New Tools**: Only for hard gaps where no tool exists

See [Gaps Guide](/wiki/Gaps-Guide) for detailed analysis.

---

## Best Practices

### 1. Start with Configuration

Before importing controls:
- Configure all active security tools
- Set realistic configuration scores
- Enable/disable tools appropriately

### 2. Import Controls Systematically

- Start with one domain
- Use consistent ControlID format
- Ensure all required fields are populated
- Validate CSV format before importing

### 3. Regular Updates

- Update control status as assessments progress
- Adjust tool configuration scores regularly
- Review gaps periodically
- Track progress over time

### 4. Prioritize Remediation

- Focus on high-severity controls first
- Tune existing tools before adding new ones
- Address soft gaps (configuration) before hard gaps (missing tools)
- Document remediation steps

### 5. Use Filters Effectively

- Filter by domain for focused analysis
- Use status filters to track progress
- Search for specific controls quickly
- Export filtered results for reporting

---

## Keyboard Shortcuts

- **`/`**: Focus search field
- **`Esc`**: Clear filters
- **`Tab`**: Navigate between form fields

---

## Tips & Tricks

1. **Bulk Import**: Prepare CSV files in Excel or similar tools
2. **Status Tracking**: Use consistent status values (Complete, InProgress, NotStarted)
3. **Domain Organization**: Group related controls by domain
4. **Configuration Scores**: Be honest—accurate scores lead to better analysis
5. **Regular Reviews**: Schedule weekly/monthly reviews of gaps and controls

---

**Need Help?** See [FAQ](/wiki/FAQ) or [Troubleshooting](/wiki/Troubleshooting) for assistance.

