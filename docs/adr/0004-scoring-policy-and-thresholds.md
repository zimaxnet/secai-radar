# ADR 0004: Scoring policy & thresholds (capability weights, minStrength, evidence factor)

- **Status:** Proposed
- **Date:** 2025-11-03

## Context
To score controls vendor-neutrally, we map each control to capability requirements. We must standardize weights, thresholds, and evidence influence for consistency and explainability.

## Decision
- **Weights:** For each control, capability weights `w_i` must sum to **1.0**; default single capability is `w=1.0`.
- **MinStrength:** Default **0.6** per capability; controls can override (e.g., SIEM-heavy controls at **0.7**).
- **Coverage:** For each capability, coverage is `max( tool_strength × configScore )` across enabled tools.
- **ControlScore:** `Coverage × 100` (rounded). Optionally multiply by an **evidence factor** (0.6–1.0) when evidence is required but incomplete.
- **Gap types:** 
  - **Hard Gap:** coverage for a capability == 0 with weight ≥ 0.25.
  - **Soft Gap:** coverage > 0 but `< minStrength`.
- **Recommendations policy:** Prefer **tuning existing tools** (raise `configScore`) before suggesting net-new spend.

## Options Considered
- Weighted average vs minimum capability: min is too punitive for overlapping tools; weighted average is explainable and stable.
- Fixed minStrength (global) vs per-capability defaults: adopt per-capability defaults with per-control overrides.
- Evidence as hard gate vs multiplier: start with **multiplier** for smoother rollout; revisit later.

## Consequences
- + Transparent math, easy to explain to stakeholders.
- + Works with overlapping tools; rewards tuning/detection quality.
- - Requires curation of `ControlRequirements` and `ToolCapabilities` seeds.

## Follow-ups
- Publish per-capability default minStrengths.
- Add unit tests for scoring and classification edge cases.
