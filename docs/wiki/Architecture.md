---
layout: default
title: System Architecture
---

# System Architecture

The platform operates using a distributed, cloud-native architecture.

## 1. Frontend: React Web App (`public-web`)

Built on **React / Vite / Tailwind**, the frontend serves as the human-in-the-loop dashboard. It queries public endpoints and handles complex submission processes securely.

## 2. API Backend (`public-api`)

A robust **FastAPI (Python)** layer acting as the orchestrator.

- Evaluates inbound submissions
- Exposes ranking endpoints
- Powers the public `/metrics` telemetry

## 3. Data Tier: Postgres + pgvector

Running on **Azure Flexible PostgreSQL**.

- **`agents` & `mcp_servers`** tables to track entities parallelly.
- Snapshot tables (`score_snapshots`, `latest_scores`) for point-in-time trust state.

## 4. Background Workers

To keep rankings fresh without locking the API tier, specialized **Python Background Workers** do the heavy lifting:

- **`scout` / `agent_scout`**: Polls official registries, git repos, and direct submissions to enqueue raw payload items.
- **`analyzer` / `scorer`**: Synthesizes the data, applies heuristic evaluation matrix strategies (Authentication checks, documentation parsing), and emits the 0-100 `Trust Score`, computing temporal decay properties natively.
