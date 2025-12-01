# SecAI Radar - Documentation Wiki

Welcome to the SecAI Radar documentation wiki. This wiki provides comprehensive guidance for users, administrators, and developers working with SecAI Radar.

## What is SecAI Radar?

SecAI Radar is an open-source, cloud-security assessment application that:

1. **Collects** configuration and evidence from cloud resources
2. **Normalizes** evidence into a common "controls/domains" data model
3. **Uses AI** to explain security posture and identify gaps
4. **Generates** human-readable assessment reports (Markdown/HTML/DOCX)

SecAI Radar is designed to be **vendor-agnostic** and **generic**—no hardcoded customer names, vendor names, or consulting firm names.

**New in v2.0**: The interface has been overhauled into a **"Command Center"** experience—a dark-mode, glassmorphism-styled interface designed for high-density information and immersive analysis.

---

## Quick Links

### For Users
- **[Getting Started](/wiki/Getting-Started)** - Quick start guide
- **[User Guide](/wiki/User-Guide)** - Complete user documentation
- **[Dashboard Guide](/wiki/Dashboard-Guide)** - Understanding the Command Center
- **[Controls Guide](/wiki/Controls-Guide)** - Managing security controls
- **[Tools Guide](/wiki/Tools-Guide)** - Configuring security tools
- **[Gaps Guide](/wiki/Gaps-Guide)** - Understanding security gaps
- **[Interactive Guidance](/wiki/Interactive-Guidance)** - Tours, help assistant, and voice support

### For Administrators
- **[Installation](/wiki/Installation)** - Installation and deployment
- **[Configuration](/wiki/Configuration)** - System configuration
- **[API Reference](/wiki/API-Reference)** - API documentation

### For Developers
- **[Architecture](/wiki/Architecture)** - System architecture overview
- **[Contributing](/wiki/Contributing)** - Contributing to SecAI Radar
- **[Development Workflow](/wiki/Development-Workflow)** - Working with main and wiki branches

### Help & Support
- **[FAQ](/wiki/FAQ)** - Frequently asked questions
- **[Troubleshooting](/wiki/Troubleshooting)** - Common issues and solutions
- **[Glossary](/wiki/Glossary)** - Terms and definitions

---

## Key Features

### 🔍 Security Assessment
- Automated collection of cloud security evidence
- Multi-tenant support
- Assessment runs with progress tracking

### 📊 Command Center Dashboard
- **Bento Grid Layout**: High-density visualization of key metrics
- **Glowing Radar**: Real-time visual analysis of domain coverage
- **Glassmorphism UI**: Modern, immersive dark mode interface

### 🎯 Control Management
- **Masonry Grid**: Visual control cards with status rings
- **Station Layout**: Dedicated focus view for assessment
- **Status Tracking**: Complete, In Progress, Not Started

### 🔧 Tool Configuration
- Security tool inventory management
- Configuration quality scoring
- Capability coverage analysis

### 📈 Gap Analysis
- **Split-Screen View**: List vs. AI Analysis panel
- **AI Remediation**: Generative AI insights for closing gaps
- **Gap Types**: Hard (missing tool) vs. Soft (misconfiguration)

### 🧭 Guided Onboarding
- First-run tour powered by React Joyride
- Scripted demo mode that walks the landing ➜ assessment ➜ dashboard ➜ gaps ➜ report journey
- “Restart tour” and “Run guided demo” shortcuts in the help assistant

### 💬 Conversational Assistant
- Floating in-app help widget with Azure OpenAI answers
- Context-aware guidance based on the screen you are viewing
- FAQ shortcuts and AI usage telemetry

### 🗣️ Voice Interaction
- Opt-in microphone mode streams audio to Azure OpenAI `gpt-realtime`
- Spoken replies play back instantly while typed chat still uses `gpt-5-chat`
- Supported in modern Chromium browsers and Safari 17+ with WebRTC enabled

### 🤖 AI-Powered Analysis
- AI-assisted security posture analysis
- Evidence classification
- Automated report generation

---

## Architecture Overview

SecAI Radar follows a **5-layer architecture**:

1. **Infrastructure Layer** - Containerized API + worker
2. **Model Layer** - Role-based AI models (reasoning, classification, generation)
3. **Data Layer** - Bronze (raw), Silver (normalized), Gold/RAG (embedded)
4. **Orchestration Layer** - Multi-step AI workflows
5. **Application Layer** - Web UI for browsing runs and reports

See **[Architecture](/wiki/Architecture)** for detailed information.

---

## Getting Help

- **Documentation**: Browse this wiki for detailed guides
- **Issues**: Report bugs or request features on GitHub
- **Questions**: Check the [FAQ](/wiki/FAQ) for common questions

---

## License

SecAI Radar is open-source. See the repository LICENSE file for details.

---

**Last Updated**: 2025-11-26
