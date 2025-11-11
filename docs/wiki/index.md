---
layout: default
title: Index
permalink: /index/
---

# SecAI Radar Documentation

Welcome to the SecAI Radar documentation wiki.

## What is SecAI Radar?

SecAI Radar is an open-source, cloud-security assessment application that:

1. **Collects** configuration and evidence from cloud resources
2. **Normalizes** evidence into a common "controls/domains" data model
3. **Uses AI** to explain security posture and identify gaps
4. **Generates** human-readable assessment reports (Markdown/HTML/DOCX)

SecAI Radar is designed to be **vendor-agnostic** and **generic**—no hardcoded customer names, vendor names, or consulting firm names.

---

## Quick Links

### For Users
- **[Getting Started](Getting-Started)** - Quick start guide
- **[User Guide](User-Guide)** - Complete user documentation
- **[User Journey](User-Journey)** - Complete assessment journey from start to finish
- **[Dashboard Guide](Dashboard-Guide)** - Understanding the dashboard
- **[Controls Guide](Controls-Guide)** - Managing security controls
- **[Tools Guide](Tools-Guide)** - Configuring security tools
- **[Gaps Guide](Gaps-Guide)** - Understanding security gaps

### For Administrators
- **[Installation](Installation)** - Installation and deployment
- **[Configuration](Configuration)** - System configuration
- **[API Reference](API-Reference)** - API documentation

### For Developers
- **[Architecture](Architecture)** - System architecture overview
- **[AI Integration](AI-Integration)** - AI-powered features
- **[Contributing](Contributing)** - Contributing to SecAI Radar

### Help & Support
- **[FAQ](FAQ)** - Frequently asked questions
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[Glossary](Glossary)** - Terms and definitions

---

## Key Features

### 🔍 Security Assessment
- Automated collection of cloud security evidence
- Multi-tenant support
- Assessment runs with progress tracking

### 📊 Dashboard & Analytics
- Real-time dashboard with security posture overview
- Domain-based compliance metrics
- Radar charts for visual analysis

### 🎯 Control Management
- Security control assessment
- CSV import/export
- Status tracking (Complete, In Progress, Not Started)

### 🔧 Tool Configuration
- Security tool inventory management
- Configuration quality scoring
- Capability coverage analysis

### 📈 Gap Analysis
- Hard gap identification (missing capabilities)
- Soft gap analysis (configuration issues)
- Remediation recommendations

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

See **[Architecture](Architecture)** for detailed information.

---

## Getting Help

- **Documentation**: Browse this wiki for detailed guides
- **Issues**: Report bugs or request features on GitHub
- **Questions**: Check the [FAQ](FAQ) for common questions

---

## License

SecAI Radar is open-source. See the repository LICENSE file for details.

---

**Last Updated**: 2025-01-27
