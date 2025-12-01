---
layout: default
title: Evidence Collection
permalink: /evidence-collection/
---

# Evidence Collection Guide

## Overview

SecAI Radar provides comprehensive evidence collection and management capabilities, allowing you to upload, organize, and track evidence files for each security control.

---

## Evidence Collection Workflow

### 1. Navigate to Control Detail Page

1. Go to **Controls** page
2. Click on any control to view its detail page
3. Scroll to the **Evidence** section

### 2. Upload Evidence

**Upload Methods:**

1. **Click Upload Button**
   - Click the **"Upload Evidence"** button
   - Select file(s) from your computer
   - Files are uploaded immediately

2. **File Requirements**
   - Supported formats: All file types
   - File size limits: Check with administrator
   - Recommended: Descriptive filenames

### 3. Evidence Management

**View Evidence:**
- All uploaded evidence appears in the Evidence section
- Click **"View"** to open/download evidence files
- Evidence metadata shows:
  - Filename
  - File size
  - Upload date

**Evidence Organization:**
- Evidence is automatically organized by control
- Files are stored in Azure Blob Storage
- Folder structure: `{tenant}/{control_id}/{timestamp_filename}`

---

## Control Detail Page

### Accessing Control Details

**From Controls Page:**
1. Navigate to **Controls**
2. Click **"View Details"** on any control card
3. Control detail page opens

**From Dashboard:**
1. Navigate to **Dashboard**
2. Click on any domain card
3. View controls in that domain
4. Click on a control to see details

### Control Information Display

**Control Details Include:**
- **Control ID** - Unique identifier
- **Control Title** - Descriptive name
- **Domain** - Security domain classification
- **Description** - Full control description
- **Question** - Assessment question
- **Required Evidence** - Evidence requirements
- **Source Reference** - Framework reference
- **Status** - Current assessment status
- **Owner** - Assigned owner
- **Notes** - Additional notes

### Updating Control Information

**Status Management:**
1. Select status from dropdown:
   - **Not Started** - Not yet assessed
   - **In Progress** - Assessment in progress
   - **Complete** - Assessment completed

2. Click **"Save Changes"** to update

**Owner Assignment:**
1. Enter owner name or email in Owner field
2. Click **"Save Changes"**

**Notes:**
1. Add notes or comments in Notes field
2. Click **"Save Changes"**

---

## Evidence Upload Process

### Step-by-Step Upload

1. **Select File**
   - Click **"Upload Evidence"** button
   - Choose file from file picker
   - File upload begins immediately

2. **Upload Progress**
   - Progress indicator shows upload status
   - Success message appears on completion
   - Evidence appears in list automatically

3. **Evidence Display**
   - Evidence appears in Evidence section
   - Shows filename, size, and upload date
   - Direct link to view/download

### Evidence Types

**Recommended Evidence Types:**
- Screenshots of configurations
- Configuration file exports
- Policy documents
- Audit logs
- Assessment reports
- Compliance certificates

**Evidence Naming:**
- Use descriptive filenames
- Include dates if relevant
- Example: `firewall-rules-2025-01-15.json`

### Evidence Metadata

**Automatically Tracked:**
- Filename
- File size
- Upload timestamp
- File URL (for viewing)

**Optional:**
- Description (can be added during upload)
- Tags (future feature)
- Evidence type classification (future feature)

---

## Evidence Management

### Viewing Evidence

**From Control Detail Page:**
1. Scroll to **Evidence** section
2. Click **"View"** button on any evidence item
3. File opens in new tab/window

**Evidence List Display:**
- All evidence for the control
- Sorted by upload date (newest first)
- File metadata visible

### Organizing Evidence

**By Control:**
- Each control has its own evidence collection
- Evidence is automatically associated with control
- No manual linking required

**By Domain:**
- Navigate by domain to see related controls
- Each control maintains its own evidence

### Evidence Best Practices

**Upload Timing:**
- Upload evidence as you assess controls
- Keep evidence current
- Update if configurations change

**Evidence Quality:**
- Ensure evidence is relevant to control
- Use clear, descriptive filenames
- Include context in descriptions when possible

**Evidence Organization:**
- Group related evidence together
- Use consistent naming conventions
- Keep evidence files organized

---

## Integration with Assessment Workflow

### Evidence in Assessment Process

**Assessment Phase:**
1. Review control requirements
2. Assess current state
3. Upload evidence supporting assessment
4. Update control status

**Evidence Collection:**
- Collect evidence as you assess
- Upload immediately after review
- Update evidence if state changes

**Review Phase:**
- Review uploaded evidence
- Ensure evidence meets requirements
- Add additional evidence if needed

### Evidence and Gap Analysis

**Evidence in Gap Analysis:**
- Evidence collection impacts gap analysis
- Complete evidence = better gap identification
- Missing evidence may indicate gaps

**Evidence and Recommendations:**
- Elena agent considers evidence when generating recommendations
- Better evidence = more accurate recommendations
- Evidence helps prioritize remediation

---

## Technical Details

### Storage

**Azure Blob Storage:**
- Evidence stored in Azure Blob Storage
- Organized by tenant and control
- Secure access via SAS tokens

**Storage Structure:**
```
assessments/
  {tenant_id}/
    {control_id}/
      {timestamp}_{filename}
```

### API Endpoints

**Upload Evidence:**
```
POST /api/tenant/{tenant_id}/control/{control_id}/evidence
Content-Type: multipart/form-data
```

**List Evidence:**
```
GET /api/tenant/{tenant_id}/control/{control_id}/evidence
```

**Get Control Details:**
```
GET /api/tenant/{tenant_id}/control/{control_id}
```

### File Handling

**Supported Formats:**
- All file types supported
- Files stored as-is in blob storage
- Metadata extracted automatically

**File Limits:**
- Check with administrator for size limits
- Large files may take longer to upload
- Progress indicator shows upload status

---

## Troubleshooting

### Upload Issues

**File Not Uploading:**
- Check file size limits
- Verify network connectivity
- Check browser console for errors
- Try a different file format

**Upload Slow:**
- Large files take longer
- Check network speed
- Wait for upload to complete

### Access Issues

**Cannot View Evidence:**
- Verify you have access to the control
- Check file URL is accessible
- Contact administrator if issues persist

**Evidence Not Appearing:**
- Refresh the page
- Check upload was successful
- Verify correct control page

---

## Examples

### Example 1: Uploading Configuration Evidence

1. Navigate to control **SEC-NET-001** (Network Segmentation)
2. Review control requirements
3. Export Azure Firewall rules to JSON file
4. Click **"Upload Evidence"**
5. Select `firewall-rules-2025-01-15.json`
6. Evidence appears in list
7. Update control status to "In Progress"

### Example 2: Collecting Screenshot Evidence

1. Navigate to control **SEC-ID-001** (Identity Management)
2. Review conditional access policies in Azure AD
3. Take screenshot showing policy configuration
4. Click **"Upload Evidence"**
5. Select screenshot file
6. Evidence appears in list
7. Add description: "Conditional access policy screenshot"
8. Save control updates

---

## Best Practices

### Evidence Collection

1. **Collect Early** - Start collecting evidence as you begin assessment
2. **Be Thorough** - Include all relevant evidence
3. **Be Organized** - Use descriptive filenames
4. **Keep Current** - Update evidence if configurations change
5. **Verify Relevance** - Ensure evidence supports control assessment

### Evidence Management

1. **Review Regularly** - Periodically review uploaded evidence
2. **Maintain Quality** - Ensure evidence is clear and relevant
3. **Organize Systematically** - Use consistent naming and organization
4. **Archive Old Evidence** - Remove outdated evidence when updated
5. **Document Context** - Add descriptions explaining evidence

---

## Related Documentation

- [Controls Guide](docs/wiki/Controls-Guide.md) - Control management
- [Platform Features](docs/wiki/Platform-Features.md) - Overall platform features
- [User Guide](docs/wiki/User-Guide.md) - Complete user documentation
- [Agent Integration](docs/wiki/Agent-Integration.md) - Agent-assisted workflows

---

**Last Updated**: 2025-01-15

