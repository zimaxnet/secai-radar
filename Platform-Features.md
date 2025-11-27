---
layout: default
title: Platform Features
permalink: /platform-features/
---

# SecAI Radar Platform Features

## Overview

SecAI Radar v2.0 is a unified platform that combines comprehensive security assessment workflows with an advanced multi-agent AI system. The interface has been completely redesigned into a **"Command Center"** experience—featuring a dark-mode, glassmorphism-styled UI with high-density Bento Grid layouts.

---

## Command Center Interface

### Visual Design

The new interface features:

- **Dark Theme** - Deep navy/slate background (#020617) with layered depth
- **Glassmorphism** - Frosted glass panels with backdrop blur effects
- **Bento Grid Layout** - High-density information display in organized grid cells
- **Glowing Accents** - Cyan/blue glow effects on interactive elements
- **Progress Rings** - SVG-based circular progress indicators

### Navigation

The platform features a glassmorphic top navigation bar:

- **Overview** - Assessment overview and status
- **Dashboard** - Command Center with radar and KPIs
- **Controls** - Masonry grid control management
- **Tools** - Security tools inventory
- **Gaps** - Split-screen AI-powered gap analysis
- **Report** - Assessment report generation

---

## Assessment Workflow Features

### Command Center Dashboard

The Dashboard provides a comprehensive overview using a **Bento Grid Layout**:

- **Security Score Ring** - Large percentage ring showing overall compliance (0-100%)
- **Active Gaps Counter** - Real-time count of identified security gaps
- **AI Threat Analysis** - Generative AI summary of current risk posture
- **Coverage Radar** - Glowing multi-axis radar chart showing domain coverage
- **Domain Grid** - Scrollable grid of domain cards with progress bars

### Controls Management (Masonry Grid)

**Domain View**
- Masonry grid layout of control cards
- Each card features an SVG progress ring
- Status badges (Complete, In Progress, Not Started)
- Gap indicators (red/orange dots)

**Station View (Control Detail)**
- Split-column layout: Assessment Form | Context Panel
- Drag-and-drop evidence upload zone
- AI Insight panel with "Generate AI Guidance" button
- Detected gaps card with deficiency breakdown

### Gap Analysis (Split-Screen)

**Left Panel: Gaps List**
- Scrollable list of controls with gaps
- Hard gaps (red badges) and Soft gaps (orange badges)
- Click to load details in right panel

**Right Panel: AI Glass Panel**
- Control context header
- Deficiency breakdown
- AI Remediation Plan (when Copilot active)
- "Activate AI Copilot" toggle button

### Tools Inventory

- Security tools catalog with capability mapping
- Configuration scoring (ConfigScore 0.0 - 1.0)
- Enabled/disabled status toggles
- Glass card styling with hover effects

### Report Generation

- Executive summary generation with AI
- Domain-by-domain breakdown
- Gap remediation recommendations
- PDF export capability

---

## Multi-Agent AI System

### Agent Overview

SecAI Radar features 7 specialized AI agents:

1. **Aris Thorne** - Knowledge Base Guardian (Framework expertise)
2. **Leo Vance** - Identity & Access Analyst (IAM specialist)
3. **Ravi Patel** - Infrastructure Architect (Infrastructure analysis)
4. **Kenji Sato** - Findings Analyst (Data correlation)
5. **Elena Bridges** - Business Impact Strategist (Risk and recommendations)
6. **Marcus Sterling** - Conflict Resolution (Trade-off analysis)
7. **Priya Desai** - System Orchestrator (Workflow management)

### Agent Integration

**Gap Analysis AI Copilot**
- Toggle "Enable AI Copilot" in the Gaps view
- Automatically generates remediation plans for selected controls
- Prioritizes tuning existing tools before suggesting new ones

**Control Detail AI Insight**
- Click "Generate AI Guidance" for control-specific help
- Context-aware recommendations based on control metadata

**Voice Interaction**
- Opt-in microphone mode for voice queries
- Streams audio to Azure OpenAI `gpt-realtime`
- Spoken replies with text transcription

---

## User Experience Features

### Onboarding Tour

- First-run guided tour powered by React Joyride
- Highlights key interface elements
- "Restart tour" option in help assistant

### Conversational Assistant

- Floating help widget (bottom-right corner)
- Azure OpenAI powered responses
- Context-aware based on current page
- FAQ shortcuts

### Accessibility

- Keyboard navigation support
- ARIA labels on interactive elements
- High contrast text on dark backgrounds
- Responsive design for all screen sizes

---

## Technical Stack

### Frontend

- **React 18** with TypeScript
- **Vite 7** build tool
- **Tailwind CSS 4** utility-first styling
- **Recharts** for radar and chart visualizations
- **React Router 7** client-side routing
- **React Joyride** onboarding tours

### Backend

- **Azure Functions** (Python) HTTP triggers
- **Azure Table Storage** for assessment data
- **Azure Blob Storage** for evidence files
- **Azure OpenAI Service** for AI features
- **Azure Key Vault** for secrets management

### AI/ML

- **Azure OpenAI GPT-4** for recommendations
- **Azure OpenAI Realtime** for voice interaction
- **Google File Search** for RAG retrieval
- **LangGraph** for multi-agent orchestration

---

## Related Documentation

- [User Guide](User-Guide.md) - Complete user documentation
- [Multi-Agent System](Multi-Agent-System.md) - Agent architecture details
- [Dashboard Guide](Dashboard-Guide.md) - Command Center usage
- [Controls Guide](Controls-Guide.md) - Masonry Grid control management
- [Gaps Guide](Gaps-Guide.md) - Split-screen gap analysis
- [API Reference](API-Reference.md) - API documentation

---

**Last Updated**: 2025-11-27
