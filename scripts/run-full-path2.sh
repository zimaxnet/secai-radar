#!/bin/bash
# One full Path 2 run for RSS-with-real-data gate (plan step 5a/5b).
# Order: Scout → Curator → Evidence Miner → Scorer (WRITE_TO_STAGING=1) → Drift → Daily Brief → Publisher.
# Prereqs: migrations applied (raw_observations, latest_scores_staging, pipeline_runs, etc.). Tier 1 source must return parseable data.
# T-080: records run in pipeline_runs for status endpoint and stale banner.
set -e
cd "$(dirname "$0")/.."

if [ -z "${DATABASE_URL}" ]; then
  KV_NAME="${KEY_VAULT_NAME:-secai-radar-kv}"
  if command -v az &>/dev/null && az account show &>/dev/null 2>&1; then
    DATABASE_URL=$(az keyvault secret show --vault-name "$KV_NAME" --name database-url --query value -o tsv 2>/dev/null || true)
  fi
fi

if [ -z "${DATABASE_URL}" ]; then
  echo "DATABASE_URL is not set. Set it or use Azure CLI + Key Vault (secai-radar-kv / database-url)."
  exit 1
fi

export DATABASE_URL

VENV="${PWD}/apps/public-api/.venv"
RECORD_PY="${PWD}/apps/public-api/scripts/record_pipeline_run.py"
RUN_ID=""
finish_run() {
  if [ -n "$RUN_ID" ] && [ -f "$RECORD_PY" ]; then
    "$VENV/bin/python" "$RECORD_PY" --finish "$RUN_ID" --failed 2>/dev/null || true
  fi
}
trap finish_run EXIT

if [ -d "$VENV" ] && [ -f "$RECORD_PY" ]; then
  RUN_ID=$("$VENV/bin/python" "$RECORD_PY" --start --trigger "run-full-path2.sh" 2>/dev/null || true)
fi

echo "==> Scout (T-070)"
./scripts/run-scout.sh

echo "==> Curator (T-071)"
./scripts/run-curator.sh

echo "==> Evidence Miner (T-072)"
./scripts/run-evidence-miner.sh

echo "==> Scorer with WRITE_TO_STAGING=1 (T-073, T-051)"
WRITE_TO_STAGING=1 ./scripts/run-scorer.sh

echo "==> Drift Sentinel (T-074)"
./scripts/run-drift-sentinel.sh

echo "==> Daily Brief (T-075)"
./scripts/run-daily-brief.sh

echo "==> Publisher (T-076) — validate staging, flip latest_scores, refresh rankings_cache"
./scripts/run-publisher.sh

if [ -n "$RUN_ID" ] && [ -f "$RECORD_PY" ]; then
  trap - EXIT
  "$VENV/bin/python" "$RECORD_PY" --finish "$RUN_ID" 2>/dev/null || true
fi

echo "==> Full Path 2 run complete. Verify feeds: GET /mcp/feed.xml and GET /mcp/feed.json"
