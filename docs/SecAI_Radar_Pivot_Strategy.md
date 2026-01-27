# Strategic Pivot: SecAI Radar & The ctxEco Ecosystem
**Date:** January 25, 2026
**Project:** SecAI Radar Authority (formerly Verified MCP Reports)
**Status:** Architecture Definition & Marketplace Submission

---

## 1. Executive Summary: The Pivot
We have fundamentally shifted the mission of `secairadar.cloud`.
* **The Original Plan:** A passive reporting tool ("Verified MCP Daily Report") that likely scanned or audited MCP servers and sent a summary of their health or security status.
* **The New Plan:** An active **"Verified MCP Authority"** middleware. It is no longer just *watching* the ecosystem; it is *governing* it. It sits between the Azure AI Agent and the MCP Server, enforcing security protocols in real-time.

**Why this matters:**
Reporting is a "Day 2" concern (optimizing). Governance is a "Day 0" concern (blocking/allowing). This pivot moves `secairadar` from a "nice-to-have" tool to a "must-have" piece of security infrastructure for any Enterprise using Azure AI Foundry.

---

## 2. The Strategic Shift

| Feature | **Old Plan: "Daily Report"** | **New Plan: "Authority Middleware"** |
| :--- | :--- | :--- |
| **Role** | Observer / Auditor | Gatekeeper / Enforcer |
| **Value Prop** | "Here is a list of your risky tools." | "We blocked a risky tool from running." |
| **Technology** | Periodic Scans | Real-time Proxy & Azure Policy |
| **Engagement** | User reads an email. | System automatically enforces rules. |
| **Monetization** | Subscription for data/feeds. | Infrastructure/Platform usage fees. |

### The "Authority" Value Proposition
Microsoft's "Shared Responsibility Model" for Azure AI Foundry leaves a gap: *Who secures the context coming from external tools?*
* **Microsoft** secures the rails (transport).
* **SecAI Radar** secures the payload (context).

We are positioning SecAI Radar as the "SSL Certificate Authority" for the Agentic Age. Just as you wouldn't visit a website without HTTPS, an Enterprise shouldn't connect an Agent without SecAI Radar.

---

## 3. The New Technical Architecture

### A. The "Gk" Protocol (Graph Knowledge)
Instead of unstructured text, our system enforces a new standard for context data: **Graph Knowledge**.
* **What it is:** Data is returned as structured Nodes and Edges, not blobs of text.
* **Why it's secure:**
    * **Merkle Proofs:** Every response is hashed and signed. If a malicious actor (or prompt injection) alters a single word, the cryptographic signature fails.
    * **Hallucination Firewall:** The Agent is constrained to reason only across the "Edges" explicitly defined in the graph.

### B. The Middleware (SecAI Radar)
A transparent proxy that sits between Azure AI Foundry and the MCP Server (`ctxEco`).
1.  **Intercepts** the traffic.
2.  **Validates** the user's Entra ID (Identity Propagation).
3.  **Verifies** the Gk Signature (Anti-Tamper).
4.  **Permits** or **Denies** the transaction.

### C. The Governance Lock (Azure Policy)
We designed a custom Azure Policy definition that "locks" the customer's environment.
* **The Rule:** "Deny any connection to an MCP server that is not routed through `api.secairadar.cloud`."
* **The Effect:** Once an Enterprise Admin turns this on, `secairadar` becomes the mandatory gateway for all their AI tools.

---

## 4. Designed Artifacts (Summary)

We have created the following assets to execute this pivot in the Azure Marketplace:

### 1. The Gk Verification Schema (`gk-proof-v1.json`)
* **Purpose:** A JSON schema that defines exactly what a "Verified" response looks like.
* **Key Fields:** `integrity_proof` (Merkle Root), `security_context` (User ID), `provenance` (Source ID).

### 2. The Azure Policy Definition
* **Purpose:** A JSON policy rule that audits or blocks unverified connections in Azure AI Foundry.
* **Mechanism:** Inspects the `target` URL of all `Microsoft.MachineLearningServices/workspaces/connections` resources.

### 3. The "One-Click" ARM Template (`mainTemplate.json`)
* **Purpose:** Deploys the entire stack in minutes.
* **Resources Deployed:**
    * `ctxEco` Container App (The Tool).
    * Managed Identity (The Security).
    * Policy Assignment (The Governance).

### 4. The Marketplace UI (`createUiDefinition.json`)
* **Purpose:** The visual wizard customers see in the Azure Portal.
* **Key Feature:** Locks the "Authority URL" field so users cannot bypass the governance layer.

---

## 5. Next Steps

1.  **Package:** Zip the ARM Template and UI Definition.
2.  **Submit:** Upload to Azure Partner Center as an "Azure Application" (Solution Template).
3.  **Deploy:** Once certified, use the "Enforce Policy" marketing angle to drive adoption among security-conscious Enterprises.