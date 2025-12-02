---
layout: default
title: Controls Guide
---

# Controls Guide

Complete guide to managing security controls using the **Masonry Grid** and **Station View**.

---

## Overview

Controls are the fundamental units of the SecAI Radar assessment. You interact with them in two main views:
1. **Domain View**: A high-level masonry grid of all controls in a domain.
2. **Station View (Detail)**: A focused workspace for assessing a single control.

---

## Domain View (Masonry Grid)

When you click a domain (e.g., "Network Security"), you see a **Masonry Grid** of control cards.

### Control Card Anatomy
- **Progress Ring**: A visual SVG ring showing the coverage percentage (Green/Orange/Red).
- **Status Badge**: "Complete", "In Progress", or "Not Started".
- **Title & Description**: Brief summary of the control.
- **Gap Indicators**: Small red/orange dots indicating if issues exist.

**Action**: Click any card to enter the **Station View**.

---

## Station View (Control Detail)

This is where the actual work happens. It follows a logical left-to-right flow:

### Left Column: Assessment Form
- **Status Selector**: Dropdown to change status (Not Started -> Complete).
- **Owner**: Assign a responsible person.
- **Notes**: Text area for your findings.
- **Evidence Drop Zone**: Modern drag-and-drop area to upload screenshots/PDFs.

### Right Column: Context Panel
- **Description**: Full detailed text of the control requirement.
- **Validation Question**: The specific question you need to answer (e.g., "Is MFA enabled on root?").
- **AI Insight**: A floating glass card that offers guidance. Click "Generate AI Guidance" if you're stuck.

---

## Importing Controls

To bulk-import controls:
1. Go to the **Controls** page via the top nav.
2. Click the **Import CSV** button (if available in your version).
3. Paste your CSV content.

**Required Columns**:
`ControlID, Domain, ControlTitle, ControlDescription, Status`

---

## Best Practices

### 1. Evidence First
Don't just mark it "Complete". Upload evidence to the **Drop Zone** to prove it. This is critical for audits.

### 2. Use the Notes
Use the **Notes** field to document *why* you marked it complete or why it's stuck.

### 3. Check the Ring
In the Domain View, look for "broken rings" (incomplete circles). These are your to-do list.

---

**Related Guides**: [Gaps Guide](/wiki/Gaps-Guide) | [Dashboard Guide](/wiki/Dashboard-Guide)
