# GitHub Project and Issues — Review

**Date:** 2026-01-26  
**Repo:** [zimaxnet/secai-radar](https://github.com/zimaxnet/secai-radar)  
**Project:** [Verified MCP MVP Implementation (Project #3)](https://github.com/orgs/zimaxnet/projects/3)  
**Backlog source of truth:** [mvp-build-tickets.md](mvp-build-tickets.md)

---

## 0. Ensure everything is trackable on the board

T-206, T-207, T-208 **already exist** as #130, #131, #132 (created via `./scripts/create-plan-step-issues.sh`). T-080 and T-081 have issues #98, #39 and #99, #40 respectively.

1. **Add plan-step issues to Project #3 if missing**  
   Ensure #130, #131, #132 are on the project board and in the right column (e.g. Backlog or Done).

2. **Confirm T-080 and T-081 are on the project**  
   Add #98 / #99 (or the chosen canonical pair) to Project #3 if not already there.

3. **Create plan-step issues only if missing**  
   From repo root: `./scripts/create-plan-step-issues.sh` (or `--dry-run` to preview).

---

## 1. Summary

- **Project board** and **milestones** (Phase 0–4, MVP Launch) exist and are in use.
- **Labels** (category:*, priority:*, phase:*, status:*) are applied; many issues use Phase 0 due to bulk creation defaults.
- **~50 open, ~82 closed** (as of 2026-01-26). Many tickets have **duplicate issues** (same T-XXX, different issue numbers). Canonical coverage is good; hygiene needs work.
- **Backlog is ahead of GitHub:** Phase 3/4 tickets T-090–T-113, T-120–T-122, T-130–T-134 are **Completed** (or Partial) in the backlog but many are still **OPEN** on GitHub. Plan-step issues #130 (T-206), #131 (T-207), and T-080/T-081 are **done in code** (commit 23fc244) and should be closed with a short comment.

---

## 2. Issue counts (from `gh issue list --state all`)

| State  | Count (approx) |
|--------|-----------------|
| Open   | ~50             |
| Closed | ~82             |

Canonical ticket coverage: all T-001–T-076, T-080–T-081, T-090–T-113, T-120–T-122, T-130–T-132, T-200–T-205, and T-206–T-208 have at least one issue. Duplicates inflate the total.

---

## 3. Fully functioning Verified MCP — current issue status (2026-01-26)

Plan-step and step‑6 issues exist. Implementation is done in code (commit 23fc244) for T-206, T-207, T-080, T-081; T-208 is script/runbook complete, execution is ops.

| Issue | Title | Backlog / code state | Recommended action |
|-------|--------|----------------------|--------------------|
| **#130** | Doc sync: Update MVP-IMPLEMENTATION-PLAN Phase 3/4 status (T-206) | T-206 ✅ Completed in backlog; MVP plan, build-order, mvp-build-tickets updated | **Close** with comment: “Done in 23fc244. Phase 3/4 docs aligned with implementation.” |
| **#131** | Registry: GET /evidence-packs and Evidence tab list (T-207) | GET /evidence-packs and Evidence tab already in registry API + RegistryEvidence UI | **Close** with comment: “GET /evidence-packs and Evidence tab list already implemented. See registry routes and RegistryEvidence.tsx.” |
| **#132** | RSS gate: Execute full Path 2 run + verify Tier 1 + deploy feeds (T-208) | Script and runbook in place (`run-full-path2.sh`, README). Running and deploy are ops. | **Leave open** until someone runs the script and verifies feeds in target env; or close and open a new “RSS gate: run in prod” issue to track execution. |
| **#98, #39** | T-080: Run logs + run status table | T-080 ✅ Completed in backlog; 007_pipeline_runs, record_pipeline_run.py, run-full-path2.sh | **Close #39** as duplicate of #98; **close #98** with comment: “Done in 23fc244. pipeline_runs, record_pipeline_run.py, run-full-path2.sh.” |
| **#99, #40** | T-081: Status endpoint + stale banner support | T-081 ✅ Completed in backlog; status.py returns lastSuccessfulRun; stale banner in both MCP layouts | **Close #40** as duplicate of #99; **close #99** with comment: “Done in 23fc244. GET /api/v1/public/status + stale banner in public-web and web.” |

**Copy-paste close commands (run from repo root):**

```bash
# T-206 doc sync — done
gh issue close 130 --repo zimaxnet/secai-radar --comment "Done in 23fc244. Phase 3/4 docs aligned with implementation."

# T-207 evidence-packs — already in code
gh issue close 131 --repo zimaxnet/secai-radar --comment "GET /evidence-packs and Evidence tab list already implemented. See registry API and RegistryEvidence.tsx."

# T-080: close duplicate, then canonical
gh issue close 39 --repo zimaxnet/secai-radar --comment "Duplicate of #98. T-080 done in 23fc244."
gh issue close 98 --repo zimaxnet/secai-radar --comment "Done in 23fc244. pipeline_runs, record_pipeline_run.py, run-full-path2.sh."

# T-081: close duplicate, then canonical
gh issue close 40 --repo zimaxnet/secai-radar --comment "Duplicate of #99. T-081 done in 23fc244."
gh issue close 99 --repo zimaxnet/secai-radar --comment "Done in 23fc244. GET /api/v1/public/status + stale banner in both MCP layouts."
```

---

## 4. Backlog–GitHub sync gaps (implemented per backlog, still OPEN on GitHub)

These are **Done** (or **Partial**) in [mvp-build-tickets.md](mvp-build-tickets.md) but were **OPEN** at review time. Close the **canonical** issue for each with a one-line reference to the backlog (and optionally commit 23fc244). Use one issue per ticket when closing (see §5 Duplicates).

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

**Phase 3 / Phase 4 (Completed in backlog 2026-01-26, still OPEN on GitHub):**

| Ticket | Backlog status | Issue # (canonical / duplicate) | Suggested action |
|--------|----------------|----------------------------------|------------------|
| T-090  | Completed      | #100, #41                        | Close one as duplicate, close the other: "Done per backlog 2026-01-26. See mvp-build-tickets.md, commit 23fc244." |
| T-091  | Completed      | #101, #42                        | Same pattern. |
| T-092  | Completed      | #102, #43                        | Same pattern. |
| T-100  | Completed      | #103, #44                        | Same pattern. |
| T-101  | Completed      | #104, #45                        | Same pattern. |
| T-102  | Completed      | #105, #46                        | Same pattern. |
| T-103  | Completed      | #106, #47                        | Same pattern. |
| T-104  | Completed      | #107, #48                        | Same pattern. |
| T-105  | Completed      | #108, #49                        | Same pattern. |
| T-110  | Completed      | #109, #50                        | Same pattern. |
| T-111  | Completed      | #110, #51                        | Same pattern. |
| T-112  | Completed      | #111, #52                        | Same pattern. |
| T-113  | Partial        | #112, #53                        | Same pattern; note "list evidence packs" is optional (T-207). |
| T-120  | Completed      | #113, #54                        | Same pattern. |
| T-121  | Completed      | #114, #55                        | Same pattern. |
| T-122  | Completed      | #115, #56                        | Same pattern. |
| T-130  | Completed      | #57                             | Close: "Done per backlog. In-API rate_limit middleware. See mvp-build-tickets.md." |
| T-131  | Completed      | #58                             | Close: "Done per backlog. audit_log repo, registry routes. See mvp-build-tickets.md." |
| T-132  | Completed      | #59                             | Close: "Done per backlog. BACKUPS-AND-RETENTION.md. See mvp-build-tickets.md." |
| T-133  | Completed      | —                               | If an issue exists, close it. |
| T-134  | Completed      | —                               | If an issue exists, close it (Fairness.tsx, /mcp/fairness). |

---

## 5. Duplicate issues (same T-XXX, multiple issue numbers)

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

## 6. Milestones and labels

- **Milestones** — Phase 0 (due 2026-01-24), Phase 1 (2026-01-29), Phase 2 (2026-02-05), Phase 3 (2026-02-12), Phase 4 (2026-02-19), MVP Launch (2026-02-20). Useful for reporting.
- **Phase labels** — Some issues are labeled `phase:0` even when they belong to Phase 3/4 (e.g. T-090–T-113, T-120–T-122). Aligning `phase:*` with the backlog (and with the milestone on the canonical issue) will make filters and project views accurate.
- **status:completed** — Already used on several issues. Adding it when closing “Done” tickets keeps the board consistent.

---

## 7. Suggested next actions

1. **Close “Done” issues**  
   For each ticket in the tables in §3 (plan steps) and §4 (Backlog–GitHub sync), close the canonical issue with a short comment pointing to the backlog (and optionally commit 23fc244).

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

## 8. Fully functioning Verified MCP — issues for Project #3

T-206, T-207, T-208 **already exist** as #130, #131, #132. T-080 and T-081 have issues #98, #39 and #99, #40. For current status and close commands, see **§3**. Original “create if missing” guidance:

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

## 9. Quick reference

- **Backlog:** [docs/backlog/mvp-build-tickets.md](mvp-build-tickets.md)  
- **Fully functioning plan steps:** [mvp-build-tickets.md](mvp-build-tickets.md) § "Fully functioning Verified MCP — plan steps" (T-206, T-207, T-208; T-080, T-081)  
- **Implementation plan:** [docs/implementation/MVP-IMPLEMENTATION-PLAN.md](../implementation/MVP-IMPLEMENTATION-PLAN.md)  
- **Project:** https://github.com/orgs/zimaxnet/projects/3  
- **Repo issues:** https://github.com/zimaxnet/secai-radar/issues  
- **List all issues:** `gh issue list --repo zimaxnet/secai-radar --state all`  
- **Close and comment:** `gh issue close <N> --repo zimaxnet/secai-radar --comment "Done. See docs/backlog/mvp-build-tickets.md"`
