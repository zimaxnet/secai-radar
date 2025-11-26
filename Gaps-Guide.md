---
layout: default
title: Gaps Guide
---

# Gaps Guide

Complete guide to understanding and remediating security gaps using the **Split-Screen AI Workspace**.

---

## Overview

The Gaps page is designed as a focused workspace for remediation. It uses a **Split-Screen Layout**:
- **Left Panel**: Interactive list of all identified gaps
- **Right Panel**: AI Glass Panel for detailed analysis and remediation advice

---

## The Split-Screen Interface

### Left Panel: Gaps List
- **Scrollable List**: All controls with identified gaps are listed here.
- **Indicators**:
  - **Hard Gaps**: Red badges (Missing capability)
  - **Soft Gaps**: Orange badges (Misconfiguration)
- **Interaction**: Click any item to load its details into the Right Panel.

### Right Panel: AI Glass Panel
This is your "Copilot" for fixing issues.
- **Context Header**: Shows the control title and ID.
- **Deficiency List**: Detailed breakdown of exactly *what* is missing (e.g., "Missing 'DLP' capability").
- **AI Remediation Plan**: A generative AI section that explains *how* to fix the gap using your existing tools or recommended new ones.

---

## Understanding Gaps

### Gap Types

#### Hard Gaps (Red)
**Definition**: You have a requirement (e.g., "Firewall") but NO tool in your inventory provides that capability.
- **Fix**: Purchase/Install a tool that provides the missing capability.

#### Soft Gaps (Orange)
**Definition**: You have a tool, but it is not configured strongly enough (Config Score < Minimum).
- **Fix**: Tune the existing tool (increase its Config Score in the Tools page).

---

## Using the AI Copilot

1. **Select a Gap**: Click a control in the left list.
2. **Activate AI**: If the AI panel is closed, click "Activate AI Copilot".
3. **Read Insights**: The AI will analyze your specific toolset and tell you:
   - "You have Palo Alto Firewall, but it's not configured for SSL Decryption."
   - "Enable this feature to close the gap."
4. **Take Action**: Go to the [Tools](/wiki/Tools-Guide) page to update your configuration score after making changes.

---

## Remediation Strategy

### 1. Soft Gaps First
Always prioritize **Soft Gaps**. These are "quick wins" because you already own the tool—you just need to configure it better.

### 2. Use the AI
Don't guess. Let the AI explain the gap. It understands the specific capabilities of hundreds of security tools.

### 3. Update Inventory
Once you fix a gap (e.g., by installing a new tool), go to the **Tools** page and add it. The Gaps list will automatically update and remove the resolved item.

---

**Related Guides**: [Tools Guide](/wiki/Tools-Guide) | [Dashboard Guide](/wiki/Dashboard-Guide)
