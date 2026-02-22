<div align="center">
  <img src="https://secairadar.cloud/vite.svg" alt="SecAI Radar Logo" width="120" />
</div>

<h1 align="center">SecAI Radar</h1>

<p align="center">
  <strong>The Agentic-First Trust Verifier for Model Context Protocol (MCP) Servers and AI Agents.</strong>
</p>

<p align="center">
  <a href="https://github.com/zimaxnet/secai-radar/actions/workflows/ci.yml"><img src="https://github.com/zimaxnet/secai-radar/actions/workflows/ci.yml/badge.svg" alt="Build Status"></a>
  <a href="https://wiki.secai-radar.zimax.net"><img src="https://img.shields.io/badge/docs-wiki-blue" alt="Wiki"></a>
  <a href="https://secairadar.cloud"><img src="https://img.shields.io/badge/platform-live-success" alt="Live Platform"></a>
</p>

---

## 🧭 Overview

**SecAI Radar** is an enterprise-grade discovery and verification platform designed specifically for the rapidly expanding ecosystem of specialized AI Agents and Model Context Protocol (MCP) servers.

Rather than relying purely on human curation, SecAI Radar is built from the ground up to be **Agentic-First**. Our infrastructure leverages automated scouting agents and programmatic NLP analyzers to continuously crawl, verify, and score AI integrations for trust, security, and operational reliability.

This platform isn't just *about* agents; it's heavily optimized *for* agents. Through rigorous semantic DOM structures, `llms.txt` directories, and JSON-LD schema injections, LLM engines are inherently guided to parse the platform's data programmatically.

## ✨ Core Capabilities

- 🔍 **Parallel Integration Tracking**: Discovers and monitors both MCP servers (from official and private registries) and third-party AI Agents natively.
- 🧮 **Automated Trust Scoring**: Integrates a highly tuned Risk Matrix and Temporal Decay engine, evaluating integrations across Authentication, Data Protection, and Operational Security domains.
- 🤖 **Agentic-First Architecture**: Exposes rigorous machine-readable interfaces (`/.well-known/llms.txt`) allowing Copilots to natively crawl API data and trust rankings.
- 🏢 **Enterprise Ready**: Full support for authenticated Submissions Queues, multi-tenant Workspaces, and Private Registries.

## 🚀 Quick Start (Local Development)

To run the full stack locally for development or testing, check out the [LOCAL-BUILD-GUIDE.md](LOCAL-BUILD-GUIDE.md).

At a high level:

1. Ensure **Node.js 20+**, **Python 3.11+**, and **Docker** are installed.
2. Clone the repository and configure your `.env` (see `.env.example`).
3. Run the automated build script:

   ```bash
   ./scripts/build-local.sh
   ```

## 📚 Documentation & Wiki

For comprehensive system documentation, architecture diagrams, assessment workflows, and deployment guides, please visit our official Wiki:

🔗 **[SecAI Radar Documentation Wiki](https://zimaxnet.github.io/secai-radar/)**

*(Note: Our documentation is uniquely auto-deployed from the `docs/wiki/` folder via GitHub Actions, prioritizing up-to-date structural knowledge.)*

## 🤝 Contributing

We welcome community contributions! Please review our [Contributing Guide](docs/wiki/Contributing.md) before submitting pull requests.

Whether you're submitting a new integration or expanding our core logic, check the existing `task.md` checklists or submit a request directly through the platform.

---
<div align="center">
  <i>Empowering safe AI expansion through zero-trust integration observability.</i>
</div>
