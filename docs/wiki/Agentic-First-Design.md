---
layout: default
title: Agentic-First Design
---

# Agentic-First Design

SecAI Radar differentiates itself by prioritizing **machine readability** alongside human aesthetics. As a directory of Agents and MCPs, it is imperative that other Agents can securely and effectively ingest our registry data.

## 1. /llms.txt Standard

We expose a programmatic entrypoint specifically for AI tools via `/.well-known/llms.txt`.

This file acts as a manifest, directly mapping generic conversational intents to strict Open API calls (e.g. `/api/v1/public/mcp/rankings`).

## 2. Shared Semantic Understanding

Instead of massive nesting `<div>` trees, the frontend is rendered as a clean semantic structure:

- `<article>` tags for discreet items.
- `<header>`, `<nav>`, `<section>` wrappers for layout areas.
- **JSON-LD**: Embedded `SoftwareApplication` Schema.org scripts with live `aggregateRating` scores within the `<head>` of individual integration pages. This guarantees crawlers immediately identify the asset as an application with a definitive trust score.

## 3. Glassmorphism Aesthetics

Because it serves top-tier agents and AI copilots, SecAI Radar is visually presented with a **glassmorphic, deep-dark premium aesthetic**. It leverages Tailwind UI plugins, Google's *Outfit* font, and neon-glow utility variants to match the cutting-edge ecosystem it supports.
