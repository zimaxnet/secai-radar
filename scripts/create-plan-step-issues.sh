#!/usr/bin/env bash
#
# Create GitHub issues for Fully functioning Verified MCP plan steps (T-206, T-207, T-208)
# and add them to Project #3 so everything is trackable on the board.
#
# Usage: from repo root, run:
#   ./scripts/create-plan-step-issues.sh
#
# Requires: gh CLI, auth (gh auth status). Optional: --dry-run to print commands only.

set -e
REPO="${REPO:-zimaxnet/secai-radar}"
PROJECT_NUMBER="${PROJECT_NUMBER:-3}"
OWNER="${OWNER:-zimaxnet}"
DRY_RUN=""
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

run() {
  if [[ -n "$DRY_RUN" ]]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

create_and_add() {
  local title="$1"
  local body="$2"
  local labels="${3:-}"
  echo "Creating: $title"
  local url=""
  if [[ -n "$DRY_RUN" ]]; then
    echo "[dry-run] would create issue and add to project"
    return
  fi
  url=$(gh issue create --repo "$REPO" --title "$title" --body "$body" ${labels:+--label "$labels"} 2>/dev/null || true)
  if [[ -n "$url" ]]; then
    gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$url" 2>/dev/null || echo "  Add to project manually: $url"
  fi
}

BODY_206="Tracking: Fully functioning Verified MCP plan. Acceptance criteria in [docs/backlog/mvp-build-tickets.md](docs/backlog/mvp-build-tickets.md) section \"Fully functioning Verified MCP — plan steps\" (T-206).

- [ ] Update MVP-IMPLEMENTATION-PLAN.md: Phase 3 and Phase 4 status set to Done where implementation exists.
- [ ] Update mvp-build-tickets.md: T-090–T-113, T-120–T-122, T-130–T-134 marked Completed (or Partial) with Notes.
- [ ] Update build-order.md: Phase 3 and Phase 4 task checkboxes checked for implemented items."

BODY_207="Tracking: Fully functioning Verified MCP plan. Acceptance criteria in [docs/backlog/mvp-build-tickets.md](docs/backlog/mvp-build-tickets.md) (T-207).

- [ ] GET /api/v1/private/registry/evidence-packs (query by workspace, optional filters).
- [ ] Registry Evidence tab calls this endpoint and shows packs with status; \"validated\" when applicable."

BODY_208="Tracking: Fully functioning Verified MCP plan. Acceptance criteria in [docs/backlog/mvp-build-tickets.md](docs/backlog/mvp-build-tickets.md) (T-208).

- [ ] At least one full Path 2 run (Scout → Curator → Miner → Scorer WRITE_TO_STAGING=1 → Drift → Daily Brief → Publisher).
- [ ] Tier 1 source returns parseable data (or adapter in place); Publisher run confirmed.
- [ ] Deploy so GET /mcp/feed.xml and GET /mcp/feed.json are reachable; verify they return items from daily_briefs."

echo "Creating plan-step issues and adding to Project #$PROJECT_NUMBER..."
create_and_add "Doc sync: Update MVP-IMPLEMENTATION-PLAN Phase 3/4 status (T-206)" "$BODY_206" "priority:P1"
[[ -z "$DRY_RUN" ]] && sleep 1
create_and_add "Registry: GET /evidence-packs and Evidence tab list (T-207)" "$BODY_207" "priority:P2"
[[ -z "$DRY_RUN" ]] && sleep 1
create_and_add "RSS gate: Execute full Path 2 run + verify Tier 1 + deploy feeds (T-208)" "$BODY_208" "priority:P1"

echo "Done. Ensure T-080 and T-081 are on Project #$PROJECT_NUMBER (add manually if missing)."
