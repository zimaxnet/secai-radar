---
layout: default
title: Glossary
---

# Glossary

Terms and definitions for SecAI Radar.

---

## A

### Assessment Run

A complete security assessment execution, including collection, normalization, analysis, and reporting.

### Azure OpenAI

Microsoft's managed OpenAI service for deploying AI models in Azure.

---

## B

### Bronze Layer

Raw, unprocessed evidence from cloud discovery and collectors. Immutable and timestamped.

---

## C

### Capability

A security capability that a tool can provide (e.g., SIEM, EDR, firewall).

### Capability Coverage

The extent to which security tools cover required capabilities for a control.

### Capability Weight

The importance of a capability for a control (0-1 scale).

### Classification Model

AI model role responsible for mapping evidence to controls and domains.

### Control

A security control that must be implemented to meet security requirements.

### Control ID

Unique identifier for a security control (e.g., SEC-NET-0001).

### Coverage Score

Combined metric representing capability coverage (strength × configScore).

### CSV Import

Method of importing controls via CSV file format.

---

## D

### Domain

A security domain grouping related controls (e.g., Network Security, Identity Management).

### Domain Code

Abbreviation for a security domain (e.g., NET, IDM, LOG).

---

## E

### Evidence

Security evidence collected from cloud resources and used for assessment.

### Evidence Reference

Link to original evidence in Bronze layer for auditability.

---

## F

### Framework

A security control framework defining controls and requirements (e.g., CIS, NIST).

---

## G

### Gap

A shortfall in security capability coverage.

### Generation Model

AI model role responsible for generating reports and narratives.

### Gold/RAG Layer

Text chunks of Silver data, embedded and searchable for AI/RAG retrieval.

---

## H

### Hard Gap

A missing capability with no tool coverage (coverage = 0.0).

---

## I

### Infrastructure Layer

Layer 1: Containerized API + worker, background jobs, secure config/secrets.

---

## M

### Model Layer

Layer 2: Role-based AI models (reasoning, classification, generation).

### Model Role

A role-based model definition (reasoning_model, classification_model, generation_model).

---

## N

### Normalization

Process of transforming raw evidence (Bronze) into normalized records (Silver).

### Normalizer

Component that transforms Bronze data to Silver format.

---

## O

### Orchestration Layer

Layer 4: Multi-step AI workflows coordinating assessment runs.

---

## R

### RAG (Retrieval-Augmented Generation)

AI technique using embeddings and search for context retrieval.

### Reasoning Model

AI model role responsible for multi-step security analysis.

---

## S

### Silver Layer

Normalized records with resource, domain, control, and status information.

### Soft Gap

A capability that exists but is misconfigured (coverage < minimum threshold).

### Status

Assessment status of a control (Complete, InProgress, NotStarted, NotApplicable).

---

## T

### Tenant

A customer or organization identifier used to scope assessments.

### Tool

A security tool that provides security capabilities.

### Tool Configuration Score

Quality score (0.0-1.0) representing how well a tool is configured.

---

## V

### Vendor Tool ID

Standard identifier for a security tool (e.g., wiz-cspm, crowdstrike-falcon).

---

## Additional Terms

### Application Layer

Layer 5: Web UI for browsing runs and downloading reports.

### Data Layer

Layer 3: Bronze (raw), Silver (normalized), Gold/RAG (embedded) data patterns.

### Orchestrator

Component coordinating multi-step assessment workflows.

### Provider-Agnostic

Design principle ensuring no hardcoded vendor-specific dependencies.

### Role-Based Access

Accessing models by role (reasoning, classification, generation), not by brand.

### Vendor-Agnostic

Design principle ensuring no hardcoded vendor names or dependencies.

---

**Related**: [Architecture](/wiki/Architecture) | [User Guide](/wiki/User-Guide)
