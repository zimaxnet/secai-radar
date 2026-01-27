# GitHub Project and Issues — Review

**Date:** 2026-01-23  
**Repo:** [zimaxnet/secai-radar](https://github.com/zimaxnet/secai-radar)  
**Project:** [Verified MCP MVP Implementation (Project #3)](https://github.com/orgs/zimaxnet/projects/3)  
**Backlog source of truth:** [mvp-build-tickets.md](mvp-build-tickets.md)

---

## 0. Ensure everything is trackable on the board

To make every Fully functioning Verified MCP plan step visible on Project #3:

1. **Create T-206, T-207, T-208 and add them to the project**  
   From the repo root (with `gh` authenticated):
   ```bash
   ./scripts/create-plan-step-issues.sh
   ```
   Use `./scripts/create-plan-step-issues.sh --dry-run` to print what would run without creating issues.

2. **Confirm T-080 and T-081 are on the project**  
   If either is missing, add the existing T-080 / T-081 issue(s) to Project #3 and place them in the right column (e.g. Backlog or Phase 2).

3. **Result**  
   All plan steps 1–6 are then trackable: T-206 (steps 1–3), T-207 (step 4), T-208 (steps 5a–5c), T-080/T-081 (step 6).

---

## 1. Summary

- **Project board** and **milestones** (Phase 0–4, MVP Launch) exist and are in use.
- **Labels** (category:*, priority:*, phase:*, status:*) are applied; many issues use Phase 0 due to bulk creation defaults.
- **~90 issue rows** exist, but many tickets have **duplicate issues** (same T-XXX, different issue numbers). The backlog lists **60+ tickets**; canonical coverage is good, hygiene needs work.
- **Backlog is ahead of GitHub:** several tickets marked **Done** in the backlog are still **OPEN** (and sometimes unclosed) in GitHub. Closing them and adding a short “Done per backlog 2026-01-23” comment will align the board with reality.

---

## 2. Issue counts (from `gh issue list --state all`)

| State  | Count (approx) |
|--------|-----------------|
| Open   | ~55             |
| Closed | ~35             |

Canonical ticket coverage: all T-001–T-076, T-080–T-081, T-090–T-113, T-120–T-122, T-130–T-132, T-200–T-205 have at least one issue. Duplicates inflate the total.

---

## 3. Backlog–GitHub sync gaps (implemented per backlog, still OPEN on GitHub)

These are **Done** (or **Partial**) in [mvp-build-tickets.md](mvp-build-tickets.md) but were **OPEN** at review time. Prefer closing the **canonical** issue for each (usually the lower issue number when duplicates exist) with a one-line reference to the backlog.

| Ticket | Backlog status | Example issue # | Suggested action |
|--------|----------------|-----------------|------------------|
| T-011  | Done           | #65, #6         | Close with comment “Done: latest_scores, get_latest_score, refresh script. See backlog.” |
| T-012  | Pending        | #66, #7         | Optional: add note that rankings_cache is filled by Publisher (T-076); implementation may satisfy “cache write” and only “read path + TTL” remains. |
| T-027  | Done           | #74, #15        | Close with comment “Done: ETag + Cache-Control middleware. See backlog.” |
| T-051  | Done           | #87, #28        | Close with comment “Done: latest_scores_staging, Scorer WRITE_TO_STAGING, Publisher validate+flip. See backlog.” |
| T-052  | Done           | —               | If an issue exists, close it; otherwise no change. |
| T-053  | Done           | —               | If an issue exists, close it; otherwise no change. |
| T-061  | Done           | #89, #30        | Close with comment “Done: packages/scoring, deterministic scoring + tests. See backlog.” |
| T-062  | Done           | #90, #31        | Close with comment “Done: evidence confidence 0–3 in packages/scoring. See backlog.” |
| T-070  | Done           | #91, #32        | Close with comment “Done: run-scout.sh, raw_observations. See backlog.” |
| T-071  | Done           | #92, #33        | Close with comment “Done: run-curator.sh, canonicalize+dedupe. See backlog.” |
| T-072  | Done           | #93, #34        | Close with comment “Done: run-evidence-miner.sh, evidence_items/claims. See backlog.” |
| T-073  | Done           | #94, #35        | Close with comment “Done: run-scorer.sh, score_snapshots + latest_scores. See backlog.” |
| T-074  | Done           | #95, #36        | Close with comment “Done: run-drift-sentinel.sh, drift_events. See backlog.” |
| T-075  | Done           | #96, #37        | Close with comment “Done: run-daily-brief.sh, daily_briefs. See backlog.” |
| T-076  | Done           | #97, #38        | Close with comment “Done: run-publisher.sh, rankings_cache refresh + feeds. See backlog.” |

Use one issue per ticket when closing (see “Duplicates” below).

---

## 4. Duplicate issues (same T-XXX, multiple issue numbers)

Many T-XXX tickets have 2 or 3 issues. Examples:

| Ticket | Issue numbers | Prefer for “canonical” |
|--------|----------------|-------------------------|
| T-001  | #1, #60        | #1                      |
| T-002  | #2, #61        | #2                      |
| T-003  | #3, #62        | #3                      |
| T-004  | #4, #63, #116  | #4 (others can be closed as duplicate) |
| T-010  | #5, #64        | #64 (closed)            |
| T-011  | #6, #65        | #6 or #65 (then close the other) |
| T-040  | #18, #77, #117 | #18 or #77 (close duplicates) |
| T-041  | #19, #78, #118 | #19 or #78              |
| T-042  | #20, #79, #119 | #20 or #79              |
| T-043  | #21, #80, #120 | #21 or #80              |
| T-046  | #24, #83, #121 | #24 or #83              |
| T-047  | #25, #84, #122 | #25 or #84              |
| T-048  | #26, #85, #123 | #26 or #85 (one open #123 left) |
| T-060  | #29, #88       | #29 or #88              |
| T-120  | #54, #113      | One, close other        |
| T-121  | #55, #114      | One, close other        |
| T-122  | #56, #115      | One, close other        |
| T-110–T-113 | #50–#53, #109–#112 | One per ticket, close rest |

**Recommended cleanup:** Pick one issue per T-XXX as canonical (often the older/lower number). Close the others with a comment: “Duplicate of #N. Track T-XXX in #N.”

---

## 5. Milestones and labels

- **Milestones** — Phase 0 (due 2026-01-24), Phase 1 (2026-01-29), Phase 2 (2026-02-05), Phase 3 (2026-02-12), Phase 4 (2026-02-19), MVP Launch (2026-02-20). Useful for reporting.
- **Phase labels** — Some issues are labeled `phase:0` even when they belong to Phase 3/4 (e.g. T-090–T-113, T-120–T-122). Aligning `phase:*` with the backlog (and with the milestone on the canonical issue) will make filters and project views accurate.
- **status:completed** — Already used on several issues. Adding it when closing “Done” tickets keeps the board consistent.

---

## 6. Suggested next actions

1. **Close “Done” issues**  
   For each ticket in the table in §3, close the canonical issue with a short comment pointing to the backlog (and optionally to the implementing PR/commit).

2. **Deduplicate**  
   For each T-XXX with multiple issues, choose one canonical issue, close the others with “Duplicate of #N. Track T-XXX in #N.”

3. **Fix phase labels**  
   Set `phase:3` / `phase:4` (and correct milestones) on T-090–T-113 and T-120–T-122 so the project view by phase matches the backlog.

4. **Optionally use a script**  
   `scripts/create-github-issues.py` is described in [GITHUB-SETUP-FINAL.md](../GITHUB-SETUP-FINAL.md). It can be extended to:
   - Avoid creating a new issue when one for that T-XXX already exists, or  
   - Output a list of (T-XXX, issue_number) for “should be closed as done” from the backlog, so you can bulk-close via `gh issue close` and a small wrapper.

5. **Keep backlog as source of truth**  
   Continue updating [mvp-build-tickets.md](mvp-build-tickets.md) and [MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md) first; use GitHub for visibility and project board workflow, and sync by closing/commenting as above.

---

## 7. Fully functioning Verified MCP — issues to create for Project #3

All steps from the plan *Fully functioning Verified MCP* must be trackable on the project board. The backlog defines **T-206, T-207, T-208** and references **T-080, T-081** for steps 6. Create these issues and add them to Project #3 so progress is visible.

| Ticket | Plan step(s) | GitHub issue title | Labels (suggested) |
|--------|--------------|--------------------|--------------------|
| **T-206** | 1–3 (doc sync) | `Doc sync: Update MVP-IMPLEMENTATION-PLAN Phase 3/4 status (T-206)` | `phase:4` or `phase:3`, `priority:P1`, `category:docs` |
| **T-207** | 4 (evidence list) | `Registry: GET /evidence-packs and Evidence tab list (T-207)` | `phase:3`, `priority:P2`, `category:backend` or `frontend` |
| **T-208** | 5a–5c (RSS gate) | `RSS gate: Execute full Path 2 run + verify Tier 1 + deploy feeds (T-208)` | `phase:2` or `phase:4`, `priority:P1`, `category:devops` |
| **T-080** | 6 (run logs) | *(use existing T-080 issue)* | Ensure on Project #3 and in correct column |
| **T-081** | 6 (status + stale banner) | *(use existing T-081 issue)* | Ensure on Project #3 and in correct column |

**Body template for new issues:**  
Add to each new issue body:  
`Tracking: Fully functioning Verified MCP plan. Acceptance criteria and details in [mvp-build-tickets.md](mvp-build-tickets.md) section "Fully functioning Verified MCP — plan steps" (T-206 / T-207 / T-208).`

**Create via GitHub UI or CLI:**  
```bash
# Example for T-206 (adjust repo/org as needed):
gh issue create --repo zimaxnet/secai-radar --title "Doc sync: Update MVP-IMPLEMENTATION-PLAN Phase 3/4 status (T-206)" \
  --body "Tracking: Fully functioning Verified MCP plan. Acceptance criteria in docs/backlog/mvp-build-tickets.md (T-206)." \
  --label "priority:P1"
```  
Then add each new issue to Project #3 and place in the appropriate column (e.g. Backlog or Phase 4).

---

## 8. Quick reference

- **Backlog:** [docs/backlog/mvp-build-tickets.md](mvp-build-tickets.md)  
- **Fully functioning plan steps:** [mvp-build-tickets.md](mvp-build-tickets.md) § "Fully functioning Verified MCP — plan steps" (T-206, T-207, T-208; T-080, T-081)  
- **Implementation plan:** [docs/implementation/MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md)  
- **Project:** https://github.com/orgs/zimaxnet/projects/3  
- **Repo issues:** https://github.com/zimaxnet/secai-radar/issues  
- **List all issues:** `gh issue list --repo zimaxnet/secai-radar --state all`  
- **Close and comment:** `gh issue close <N> --repo zimaxnet/secai-radar --comment "Done. See docs/backlog/mvp-build-tickets.md"`
