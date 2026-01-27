# Observability dashboard (T-133)

## Goals

- Pipeline run success rate, duration, and failures by stage.
- API error rates and latency percentiles.

## Implementation approach

1. **Pipeline runs:** Use the `pipeline_runs` table (or run log from T-080). Expose an internal or admin view that shows last N runs, status, duration, and `stages_json` / `errors_json`. A simple dashboard can query this and render tables or charts.
2. **API metrics:** Use Azure Application Insights (or equivalent) for the public-api and registry-api. Configure request tracking, dependency tracking, and failure rates. Dashboards can be built in Azure Portal or Grafana using the same data.
3. **Alerting:** Define alerts for pipeline failure rate above threshold and API 5xx rate above threshold.

## Placeholder

Until T-080 (run logs) and Application Insights are wired, document the above and add a stub endpoint or doc link from the app if needed. The dashboard itself can be implemented as a small React page that calls `GET /api/v1/public/status` (when available) and an internal pipeline-runs API, or as an Azure dashboard backed by App Insights + DB queries.
