---
layout: default
title: User Guide
---

# SecAI Radar User Guide

Complete guide to using SecAI Radar for cloud security assessments.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Command Center Dashboard](#command-center-dashboard)
4. [Controls Management](#controls-management)
5. [Tools Inventory](#tools-inventory)
6. [Gap Analysis](#gap-analysis)
7. [AI Features](#ai-features)
8. [Report Generation](#report-generation)
9. [Best Practices](#best-practices)

---

## Overview

SecAI Radar provides a web-based **Command Center** interface for managing cloud security assessments. The application features a dark-mode, glassmorphism-styled UI with high-density Bento Grid layouts designed for immersive security analysis.

### Key Features

- **Command Center Interface**: Dark theme with glass panels and glowing accents
- **Bento Grid Layout**: High-density information visualization
- **Masonry Grid Controls**: Visual control cards with progress rings
- **Split-Screen Gap Analysis**: List view + AI Copilot panel
- **Multi-Agent AI System**: 7 specialized agents for intelligent assistance
- **Voice Interaction**: Speak to the AI assistant using your microphone

---

## Getting Started

### First Time Users

1. **Visit the Landing Page**: Learn about SecAI Framework
2. **Start New Assessment**: Create a new tenant/assessment
3. **Take the Tour**: Follow the onboarding tour to learn the interface
4. **Configure Tools**: Add your security tools inventory
5. **Import Controls**: Load your control framework

### Navigation

The Command Center uses a glassmorphic top navigation bar:

| Link | Description |
|------|-------------|
| **Overview** | Assessment overview and status |
| **Dashboard** | Command Center with radar chart and KPIs |
| **Controls** | Masonry grid control management |
| **Tools** | Security tools inventory |
| **Gaps** | Split-screen AI-powered gap analysis |
| **Report** | Generate assessment reports |

---

## Command Center Dashboard

The Dashboard is the heart of the Command Center.

### Top Row: Key Performance Indicators

Three glass panels display high-level metrics:

1. **Security Score** - Overall compliance percentage (ring chart)
2. **Active Gaps** - Count of identified security gaps
3. **AI Threat Analysis** - Generative AI summary of risk posture

### Coverage Radar (Middle Left)

A glowing multi-axis radar chart showing domain coverage:
- Each axis = one security domain
- Filled area = current coverage
- Goal: Full, balanced shape

### Domain Grid (Middle Right)

Scrollable grid of domain cards:
- Domain code and score
- Progress bar (blue/green)
- Click to drill into controls

---

## Controls Management

### Domain View (Masonry Grid)

When you select a domain, you see a **Masonry Grid** of control cards:

- **Progress Ring**: SVG circle showing coverage %
- **Status Badge**: Complete | In Progress | Not Started
- **Gap Indicators**: Red/orange dots if issues exist

**Action**: Click any card to enter the Station View.

### Station View (Control Detail)

A focused workspace for assessing individual controls:

**Left Column: Assessment Form**
- Status selector dropdown
- Owner assignment field
- Notes/findings textarea
- Evidence drop zone (drag-and-drop upload)

**Right Column: Context Panel**
- Control description
- Validation question
- Detected gaps card (if any)
- AI Insight panel with "Generate AI Guidance" button

---

## Tools Inventory

### Adding a Tool

1. Enter **Vendor Tool ID** (e.g., `wiz-cspm`, `crowdstrike-falcon`)
2. Toggle **Enabled/Disabled**
3. Set **Configuration Score** (0.0 - 1.0)
4. Click **Save Tool Configuration**

### Configuration Score Guide

| Score | Quality |
|-------|---------|
| 0.9 - 1.0 | Excellent configuration |
| 0.7 - 0.89 | Good configuration |
| 0.5 - 0.69 | Fair configuration |
| 0.0 - 0.49 | Poor configuration |

---

## Gap Analysis

### Split-Screen Interface

**Left Panel: Gaps List**
- All controls with identified gaps
- Hard gaps (red) = missing capability
- Soft gaps (orange) = misconfiguration
- Click to load details

**Right Panel: AI Glass Panel**
- Control context header
- Deficiency breakdown
- AI Remediation Plan (when Copilot active)

### Using the AI Copilot

1. Click **"Enable AI Copilot"** toggle in the header
2. Select a gap from the left list
3. Wait for AI analysis to load
4. Read remediation steps
5. Take action (update tools, fix config)

---

## AI Features

### Conversational Assistant

A floating help widget in the bottom-right corner:
- Click to expand chat interface
- Ask questions about the current page
- Get context-aware guidance

### Voice Interaction

If supported by your browser:
1. Click the microphone icon in the assistant
2. Speak your question
3. Hear the AI response
4. Transcription appears in chat

### Multi-Agent System

7 specialized agents available:
- **Aris** - Framework knowledge
- **Elena** - Business recommendations
- **Leo** - IAM specialist
- **Ravi** - Infrastructure
- **Kenji** - Data analysis
- **Marcus** - Conflict resolution
- **Priya** - Orchestration

---

## Report Generation

1. Navigate to **Report** in the top nav
2. Click **Generate Report**
3. Wait for AI to generate executive summary
4. Review domain breakdowns
5. Download PDF or print

---

## Best Practices

### 1. Configure Tools First
Before importing controls, set up your security tool inventory with accurate configuration scores.

### 2. Use the Tour
First-time users should complete the onboarding tour to learn the interface.

### 3. Work Domain by Domain
Focus on one security domain at a time rather than jumping around.

### 4. Upload Evidence
Don't just mark controls "Complete" - upload evidence to prove compliance.

### 5. Leverage AI
Use the AI Copilot for gap analysis and the AI Insight button for control guidance.

### 6. Check the Radar
Regularly check the Coverage Radar for imbalanced areas.

---

**Need Help?** See [FAQ](/wiki/FAQ) or [Troubleshooting](/wiki/Troubleshooting) for assistance.

---

**Last Updated**: 2025-11-27
