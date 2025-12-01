---
layout: default
title: Dashboard Guide
---

# Dashboard Guide

Complete guide to understanding and using the SecAI Radar **Command Center**.

---

## Overview

The Dashboard (Command Center) provides a comprehensive, high-density overview of your security posture. It uses a **Bento Grid** layout to organize key metrics, domain breakdowns, and visual analytics into a unified "Heads Up Display" (HUD).

---

## Key Metrics (Top Row)

Three primary glass panels display high-level KPIs:

### 1. Security Score
- **Display**: Large percentage ring (0-100)
- **Meaning**: Overall compliance score across all controls
- **Visual**: Glowing cyan progress bar
- **Goal**: Aim for >80%

### 2. Active Gaps
- **Display**: Large count number
- **Meaning**: Total number of identified security gaps (Hard + Soft)
- **Visual**: Red "Requires Attention" pulse if >0
- **Goal**: 0 active gaps

### 3. AI Threat Analysis
- **Display**: Text summary inside a wide glass card
- **Meaning**: Generative AI summary of your current risk posture
- **Visual**: Dynamic text that changes based on detected gaps
- **Action**: Click "View Remediation Plan" to jump to the Gaps view

---

## Coverage Radar (Middle Left)

The centerpiece of the Command Center is the **Glowing Radar Chart**.

### Visualization
- **Axes**: Each axis represents one of the 12 Security Domains (NET, IDM, DATA, etc.)
- **Shape**: The blue filled area represents your current coverage
- **Goal**: A full, balanced shape (filling the outer edges)

### Interpretation
- **Spike**: Good coverage in that specific domain
- **Dip**: Low coverage/gaps in that domain
- **Small Shape**: Early stage assessment (mostly Not Started)

---

## Domain Breakdown (Middle Right)

To the right of the Radar is the **Domain Grid**.

### Interaction
- **Layout**: Scrollable grid of domain cards
- **Card Details**:
  - **Domain Code**: (e.g., NET)
  - **Score**: Percentage completion
  - **Progress Bar**: Blue (In Progress) or Green (Complete)
- **Action**: Click any card to drill down into that domain's controls

---

## Navigation

The Command Center uses a glassmorphic top navigation bar:
- **Overview**: High-level status (Assessment Overview)
- **Dashboard**: The Command Center view
- **Controls**: Manage individual controls
- **Tools**: Manage tool inventory
- **Gaps**: AI-powered gap analysis
- **Report**: Generate executive reports

---

## Best Practices

### 1. Daily Check-in
Use the Command Center as your morning landing page. Check the **Active Gaps** count and read the **AI Threat Analysis** for new priorities.

### 2. Drill Down
Don't just stare at the numbers. Click the **Domain Cards** to fix specific controls or click the **AI Analysis** to jump straight to remediation.

### 3. Monitor the Radar
Watch for "dips" in the radar chart. A balanced security posture is better than being 100% secure in Network but 0% in Identity.

---

**Related Guides**: [Controls Guide](/wiki/Controls-Guide) | [Gaps Guide](/wiki/Gaps-Guide)
