---
layout: default
title: Platform Features
permalink: /platform-features/
---

# SecAI Radar Platform Features

## Overview

SecAI Radar v2.0 is a unified platform that combines comprehensive security assessment workflows with an advanced multi-agent AI system. All features are brought front and center in a professional, compelling interface.

---

## Unified Platform

### Architecture

SecAI Radar combines:

1. **Assessment Workflow System** - Complete security assessment lifecycle
2. **Multi-Agent AI System** - 7 specialized AI agents working together
3. **Modern Web Interface** - Professional, responsive UI with seamless navigation

### Navigation

The platform features a unified navigation structure:

- **Dashboard** - Overview of assessment progress and agent status
- **AI Agents** - Interactive agent showcase with chat interfaces
- **Controls** - Control management and evidence collection
- **Tools** - Security tools inventory
- **Gap Analysis** - AI-powered gap identification and recommendations
- **Report** - Assessment report generation

---

## Assessment Workflow Features

### Dashboard

The Dashboard provides a comprehensive overview:

- **Assessment Statistics**
  - Total controls count
  - Completed controls tracking
  - In-progress controls monitoring
  - Overall progress percentage

- **Domain Progress**
  - Visual progress bars per domain
  - Status breakdown (Complete/In Progress/Not Started)
  - Clickable domain cards for navigation

- **AI Agents Status**
  - Real-time agent availability
  - Last activity timestamps
  - Quick access to agent chat

### Controls Management

**Control Listing**
- Search and filter controls by domain, status, or keywords
- Import controls from CSV or JSON
- Export controls for reporting
- Status indicators and progress tracking

**Control Detail Page**
- Complete control information display
- Status management (Not Started → In Progress → Complete)
- Owner assignment
- Notes and comments
- Evidence collection and upload
- Agent chat integration for context-aware assistance

**Evidence Collection**
- Upload evidence files directly to controls
- Evidence file management and viewing
- Evidence metadata tracking (filename, size, upload date)
- Direct links to evidence files

### Tools Inventory

- Security tools catalog
- Tenant tool configuration
- Configuration scoring (ConfigScore)
- Enabled/disabled status
- Tool capability mapping

### Gap Analysis

- **Automated Gap Detection**
  - Hard gaps (missing capabilities)
  - Soft gaps (configuration issues)
  - Coverage scoring per control

- **AI-Powered Recommendations**
  - Toggle AI recommendations on/off
  - Elena agent generates business-focused recommendations
  - Prioritizes tool tuning before suggesting new tools
  - Actionable advice with implementation steps

- **Visual Gap Display**
  - Color-coded gap severity
  - Coverage percentage visualization
  - Gap breakdown by control

### Report Generation

- Executive summary generation
- Detailed findings reports
- PDF export capability
- Print-friendly formatting

---

## Multi-Agent AI System

### Agent Overview

SecAI Radar features 7 specialized AI agents:

1. **Aris** - Knowledge Base Guardian (Framework expertise)
2. **Leo** - Identity & Access Analyst (IAM specialist)
3. **Ravi** - Infrastructure Architect (Infrastructure analysis)
4. **Kenji** - Findings Analyst (Data correlation)
5. **Elena** - Business Impact Strategist (Risk and recommendations)
6. **Marcus** - Conflict Resolution (Trade-off analysis)
7. **Coordinator** - System Orchestrator (Workflow management)

### Agent Integration

**Gap Analysis Integration**
- Elena agent automatically generates recommendations for controls with gaps
- Business-focused advice prioritizing ROI and risk reduction
- Actionable steps for improving coverage

**Control Detail Integration**
- Agents available directly from control detail pages
- Context-aware chat automatically includes control information
- Specialized agents for different types of questions:
  - **Aris** for framework questions
  - **Elena** for recommendations and risk analysis
  - **Leo** for IAM-specific guidance

**Agent Showcase**
- Interactive agent cards with animations
- Detailed agent descriptions and capabilities
- Live chat interfaces embedded in agent detail views
- Professional UI with gradient designs

### Agent Capabilities

**Aris (Knowledge Base Guardian)**
- Answers framework questions (CAF, CIS, NIST)
- Provides control requirements and best practices
- Accesses uploaded knowledge base documents
- Framework guidance and implementation help

**Elena (Business Impact Strategist)**
- Generates gap analysis recommendations
- Translates technical findings to business language
- Provides ROI-focused advice
- Prioritizes actions by business impact

**Leo (Identity & Access Analyst)**
- IAM-specific control guidance
- RBAC and privilege analysis
- Access pattern recognition
- Conditional access policy help

---

## User Experience Features

### Professional Design

- **Dark Theme** - Modern slate background with gradient accents
- **Responsive Layout** - Mobile-friendly with collapsible navigation
- **Smooth Animations** - Framer Motion transitions and animations
- **Visual Feedback** - Loading states, progress indicators, status badges
- **Consistent UI** - Unified design language across all pages

### Navigation

- **Top Navigation Bar** - Persistent header with all main sections
- **Mobile Sidebar** - Collapsible sidebar for mobile devices
- **Active Route Highlighting** - Clear indication of current page
- **Breadcrumbs** - Context-aware navigation paths
- **Quick Actions** - Shortcuts to common tasks

### Interactive Elements

- **Chat Interfaces** - Embedded chat for agent interactions
- **Progress Bars** - Visual progress tracking
- **Status Badges** - Color-coded status indicators
- **File Upload** - Drag-and-drop evidence upload
- **Search and Filter** - Quick control and tool discovery

---

## Technical Integration

### Backend Architecture

- **FastAPI** - Modern Python web framework
- **Azure Storage** - Table Storage for controls, Blob Storage for evidence
- **Google Generative AI** - Gemini 1.5 Pro for agent interactions
- **RESTful APIs** - Clean API structure for all features

### Frontend Architecture

- **React 19** - Latest React with TypeScript
- **Vite** - Fast build tool and development server
- **Tailwind CSS 4** - Modern utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **React Router 7** - Client-side routing

### Data Flow

1. **Assessment Data** → Azure Table Storage
2. **Evidence Files** → Azure Blob Storage
3. **Agent Queries** → Google Generative AI
4. **Real-time Updates** → React state management

---

## Getting Started

### For New Users

1. **Visit Landing Page** - Learn about SecAI Radar
2. **Navigate to Dashboard** - View assessment overview
3. **Import Controls** - Get started with your security controls
4. **Configure Tools** - Add your security tools inventory
5. **Run Gap Analysis** - Identify security gaps with AI recommendations
6. **Chat with Agents** - Get expert help when needed

### For Assessment Teams

1. **Set Up Tenant** - Configure your assessment scope
2. **Import Framework Controls** - Load controls from CSV/JSON
3. **Collect Evidence** - Upload evidence for each control
4. **Analyze Gaps** - Use AI-powered gap analysis
5. **Generate Report** - Create comprehensive assessment reports

---

## Best Practices

### Assessment Workflow

1. **Start with Controls** - Import or create your control framework
2. **Configure Tools** - Map your security tools to capabilities
3. **Collect Evidence** - Upload evidence as you assess controls
4. **Review Gaps** - Use AI recommendations to prioritize remediation
5. **Track Progress** - Monitor completion status on the dashboard

### Agent Usage

1. **Aris for Frameworks** - Ask about CAF, CIS, NIST requirements
2. **Elena for Recommendations** - Get business-focused gap remediation advice
3. **Leo for IAM** - Seek identity and access control guidance
4. **Context is Key** - Chat from control pages for context-aware responses

### Evidence Management

1. **Organize by Control** - Upload evidence directly to relevant controls
2. **Use Descriptive Names** - Name files clearly for easy identification
3. **Include Metadata** - Add descriptions when uploading
4. **Review Regularly** - Keep evidence up-to-date as assessments progress

---

## Related Documentation

- [User Guide](User-Guide.md) - Complete user documentation
- [Multi-Agent System](Multi-Agent-System.md) - Agent architecture details
- [Dashboard Guide](Dashboard-Guide.md) - Dashboard usage
- [Controls Guide](Controls-Guide.md) - Control management
- [Gaps Guide](Gaps-Guide.md) - Gap analysis
- [API Reference](API-Reference.md) - API documentation

---

**Last Updated**: 2025-01-15

