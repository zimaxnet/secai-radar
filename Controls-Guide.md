---
layout: default
title: Controls Guide
---

# Controls Guide

Complete guide to managing security controls in SecAI Radar.

---

## Overview

The Controls page allows you to manage security control assessments, import controls, and track their status.

---

## Control List

### Table Columns

The control table displays:
- **Control ID**: Unique identifier (e.g., SEC-NET-0001)
- **Domain**: Security domain code (e.g., NET, IDM, LOG)
- **Title**: Human-readable control title
- **Status**: Current assessment status
- **Owner**: Control owner or responsible party

### Status Values

- **Complete**: Control is fully implemented and compliant
- **InProgress** or **In Progress**: Control is being worked on
- **NotStarted** or **Not Started**: Control has not been started
- **NotApplicable**: Control does not apply to this environment

---

## Filters

### Domain Filter

Filter controls by security domain:
- Enter domain code (e.g., `NET`, `IDM`, `LOG`)
- Case-insensitive matching
- Partial matches supported

**Common Domains**:
- `NET` - Network Security
- `IDM` - Identity Management
- `LOG` - Logging and Monitoring
- `SEC` - Security Operations
- `POST` - Posture Management

### Status Filter

Filter by assessment status:
- `Complete` - Fully compliant controls
- `InProgress` - Active work items
- `NotStarted` - Not yet started
- `NotApplicable` - N/A controls

### Search Filter

Search across multiple fields:
- Control ID
- Control Title
- Domain
- Description

**Search Tips**:
- Use partial matches (e.g., "NET" finds all NET-* controls)
- Search is case-insensitive
- Search across all visible columns

---

## Importing Controls

### CSV Format

Required CSV headers (exact order):
```
ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,
Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
```

### Required Fields

- **ControlID**: Unique identifier (e.g., `SEC-NET-0001`)
- **Domain**: Security domain code (e.g., `NET`)
- **ControlTitle**: Human-readable title
- **ControlDescription**: Detailed description
- **Status**: Complete, InProgress, NotStarted, NotApplicable
- **UpdatedAt**: Timestamp (ISO 8601 format)

### Optional Fields

- **Question**: Assessment question
- **RequiredEvidence**: Required evidence types
- **Owner**: Control owner
- **Frequency**: Assessment frequency
- **ScoreNumeric**: Numeric score (0-100)
- **Weight**: Control weight (0-1)
- **Notes**: Additional notes
- **SourceRef**: Source reference
- **Tags**: Comma-separated tags

### CSV Import Steps

1. **Prepare CSV**: Create CSV file with required headers
2. **Click Import CSV**: Button on Controls page
3. **Paste Content**: Paste CSV content into text area
4. **Validate**: System validates header format
5. **Import**: Click "Import Controls" button
6. **Review**: Check success/error messages

### Import Validation

The system validates:
- **Header Format**: Exact header match required
- **Required Fields**: All required fields must be present
- **Data Types**: Numeric fields must be valid numbers
- **Status Values**: Status must be valid value

### Common Import Errors

**Invalid Header Format**
- Error: "CSV header must be: ControlID,Domain,..."
- Solution: Ensure exact header order and spelling

**Missing Required Fields**
- Error: "Required field missing"
- Solution: Include all required fields

**Invalid Status Value**
- Error: "Invalid status value"
- Solution: Use valid status: Complete, InProgress, NotStarted, NotApplicable

---

## CSV Format Example

```csv
ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
SEC-NET-0001,NET,Network Security Group Rules,Ensure NSG rules restrict access appropriately,Are NSG rules configured to restrict access?,nsg_rules,NotStarted,Network Team,Monthly,0,0.5,Initial assessment,Framework-v1,network,2025-01-15T10:00:00Z
SEC-IDM-0001,IDM,Multi-Factor Authentication,Enable MFA for all users,Is MFA enabled for all user accounts?,mfa_config,InProgress,Security Team,Quarterly,50,0.8,Partially implemented,Framework-v1,identity,2025-01-15T10:00:00Z
```

---

## Best Practices

### 1. Consistent Naming

- Use consistent ControlID format (e.g., `SEC-{DOMAIN}-{NUMBER}`)
- Keep domain codes consistent
- Use descriptive titles

### 2. Complete Information

- Fill in all required fields
- Include detailed descriptions
- Add notes for context

### 3. Regular Updates

- Update status as work progresses
- Update timestamps regularly
- Keep owner information current

### 4. Organization

- Group controls by domain
- Use consistent tags
- Maintain source references

### 5. Validation

- Validate CSV format before importing
- Check for duplicate ControlIDs
- Verify status values

---

## Tips & Tricks

1. **Bulk Import**: Prepare CSV files in Excel or similar tools
2. **Template**: Save a CSV template for future imports
3. **Backup**: Keep CSV files as backup
4. **Filtering**: Use filters to focus on specific domains or statuses
5. **Export**: Export filtered results for reporting (if available)

---

## Troubleshooting

### Controls Not Showing

- **Check Filters**: Clear filters to see all controls
- **Check Tenant**: Verify correct tenant ID
- **Check Import**: Verify controls were imported successfully

### Import Fails

- **Check Header**: Verify exact header format
- **Check Encoding**: Ensure UTF-8 encoding
- **Check Format**: Verify CSV format (commas, not semicolons)

### Status Not Updating

- **Check Format**: Verify status value spelling
- **Check Case**: Status matching is case-sensitive
- **Refresh**: Refresh page to see updates

---

**Related Guides**: [User Guide](/wiki/User-Guide) | [Dashboard Guide](/wiki/Dashboard-Guide)
