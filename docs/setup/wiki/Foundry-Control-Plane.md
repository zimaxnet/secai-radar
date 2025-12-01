---
layout: default
title: Foundry Control Plane
permalink: /foundry-control-plane/
---

# Foundry Control Plane

## Overview

The Foundry Control Plane provides comprehensive observability, evaluation, and security controls for all AI agents in SecAI Radar. It enables real-time monitoring, continuous evaluation, and proactive issue detection.

## What is the Foundry Control Plane?

The Foundry Control Plane is Microsoft's control plane for AI agents, providing:

- **Observability** - End-to-end monitoring and tracing
- **Evaluation** - AI-powered quality assessment
- **Guardrails** - Content safety and tool controls
- **Security** - Integration with Defender and Purview

## Observability

### OpenTelemetry Integration

SecAI Radar uses OpenTelemetry for comprehensive observability:

- **Distributed Tracing** - Track requests across services
- **Metrics** - Performance and usage metrics
- **Logs** - Structured logging with context

### Metrics Tracked

**Performance Metrics**:
- `agent_response_time_ms` - Response time per agent action
- `agent_token_usage` - Token consumption per agent
- `agent_tool_calls` - Number of tool calls
- `agent_actions` - Success/failure counts

**Evaluation Metrics**:
- `groundedness_score` - Response grounded in context (0-1)
- `task_adherence_score` - Agent followed instructions (0-1)
- `tool_accuracy_score` - Tool calls succeeded (0-1)
- `relevance_score` - Response relevant to query (0-1)

### Tracing

Every agent action is traced:

```python
# Automatic tracing in agent code
with observability.trace_agent_action(
    agent_id="aris_thorne",
    action="process_task",
    attributes={"task_type": "framework_query"}
):
    # Agent action code
    result = agent.process_task(state)
```

**Trace Information**:
- Agent ID and action
- Duration
- Success/failure
- Input/output (sanitized)
- Tool calls
- Errors

### Viewing Observability Data

**Observability Dashboard**:

1. Navigate to **Observability** in the main menu
2. Select time range (1h, 24h, 7d, 30d)
3. Filter by agent (optional)
4. View:
   - Response time trends
   - Token usage
   - Evaluation scores
   - Activity metrics

**Agent Detail View**:

1. Navigate to agent detail page
2. View performance metrics
3. See evaluation scores
4. Review activity timeline

## AI-Powered Evaluators

### Continuous Evaluation

Agents are continuously evaluated using AI-powered evaluators:

**Groundedness Evaluator**:
- Verifies responses are grounded in provided context
- Detects hallucinations and unsupported claims
- Score: 0.0 (ungrounded) to 1.0 (fully grounded)

**Task Adherence Evaluator**:
- Checks agent followed assigned task instructions
- Detects deviations from task scope
- Score: 0.0 (off-task) to 1.0 (fully adheres)

**Tool Accuracy Evaluator**:
- Validates tool call correctness
- Checks tool selection and parameters
- Score: 0.0 (inaccurate) to 1.0 (fully accurate)

**Relevance Evaluator**:
- Assesses response relevance to query
- Detects off-topic content
- Score: 0.0 (irrelevant) to 1.0 (highly relevant)

### Running Evaluations

**Automatic Evaluation**:
- Evaluations run automatically on agent responses
- Sample rate configurable (default: 10%)
- Results stored in observability system

**Manual Evaluation**:

```http
POST /api/evaluations/evaluate
Content-Type: application/json

{
  "agent_id": "aris_thorne",
  "response": "Agent response text",
  "context": "Context provided to agent",
  "task_instruction": "Task instruction",
  "query": "Original query",
  "tool_calls": [...]
}
```

**Response**:

```json
{
  "agent_id": "aris_thorne",
  "scores": {
    "groundedness": 0.85,
    "task_adherence": 0.92,
    "tool_accuracy": 0.88,
    "relevance": 0.90
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Evaluation Thresholds

**Quality Gates**:
- Groundedness: ≥ 0.7 (acceptable), ≥ 0.9 (excellent)
- Task Adherence: ≥ 0.8 (acceptable), ≥ 0.95 (excellent)
- Tool Accuracy: ≥ 0.85 (acceptable), ≥ 0.95 (excellent)
- Relevance: ≥ 0.8 (acceptable), ≥ 0.9 (excellent)

**Alerts**:
- Low scores trigger alerts
- Behavioral drift detection
- Automatic quarantine for persistent low scores

## Guardrails and Content Safety

### Input Validation

All agent inputs are validated:

- **Prompt Injection Detection** - Detects injection attempts
- **Length Limits** - Maximum input length enforced
- **Content Safety** - AI-powered safety checks

### Output Filtering

Agent outputs are filtered for:

- **PII Detection** - Email, SSN, credit cards, phone numbers
- **Sensitive Data** - API keys, passwords, tokens
- **Content Safety** - Hate speech, violence, illegal content

**Automatic Redaction**:
- PII automatically redacted
- Sensitive data masked
- Unsafe content blocked

### Tool Authorization

Each agent is authorized for specific tools:

**Configuration** (`config/guardrails.yaml`):

```yaml
tool_authorization:
  agent_tools:
    aris_thorne:
      - "query_framework_knowledge"
      - "map_control_to_framework"
```

**Enforcement**:
- Unauthorized tool calls blocked
- Violations logged and alerted
- Automatic quarantine for repeated violations

### Rate Limiting

Agents are rate-limited to prevent abuse:

- **Per Minute**: 60 requests (default)
- **Per Hour**: 1000 requests (default)
- **Per Agent**: Limits applied individually

**Configuration**:

```yaml
rate_limiting:
  enabled: true
  max_requests_per_minute: 60
  max_requests_per_hour: 1000
```

## Security Integration

### Microsoft Defender

Integration with Microsoft Defender provides:

- **Security Posture** - Agent vulnerability scanning
- **Threat Detection** - Threat detection for agent activities
- **Recommendations** - Security recommendations
- **Incident Correlation** - Correlate threats across agents

### Microsoft Purview

Integration with Microsoft Purview provides:

- **Data Classification** - Classify data accessed by agents
- **Data Loss Prevention** - DLP for agent outputs
- **Compliance Labeling** - Compliance labels for agent content
- **Audit Trail** - Audit trail for sensitive data access

## Dashboard and Monitoring

### Agent Command Center

The Agent Command Center provides:

1. **Agent Health Overview** - Status of all agents
2. **Real-time Activity Feed** - Live agent actions
3. **Performance Metrics** - Response times, token usage
4. **Evaluation Scores** - Quality metrics
5. **Security Alerts** - Content safety violations

### Observability Dashboard

The Observability Dashboard provides:

1. **Trace Explorer** - End-to-end request traces
2. **Metric Charts** - Time-series performance data
3. **Evaluation Results** - Quality scores over time
4. **Cost Tracking** - Token usage and estimated costs
5. **Drift Detection** - Behavioral drift alerts

## Best Practices

### Observability

1. **Monitor Regularly** - Review metrics daily
2. **Set Alerts** - Configure alerts for anomalies
3. **Trace Analysis** - Analyze traces for bottlenecks
4. **Cost Management** - Monitor token usage

### Evaluation

1. **Continuous Evaluation** - Enable continuous evaluation
2. **Review Scores** - Review low scores promptly
3. **Improve Agents** - Use scores to improve agent prompts
4. **Quality Gates** - Set appropriate quality thresholds

### Guardrails

1. **Regular Review** - Review guardrail policies quarterly
2. **Tool Authorization** - Use least privilege for tools
3. **Rate Limits** - Adjust limits based on usage
4. **Content Safety** - Keep safety checks enabled

## API Reference

### Get Observability Metrics

```http
GET /api/observability/metrics?agent_id={agent_id}&time_range=24h
```

### Run Evaluation

```http
POST /api/evaluations/evaluate
POST /api/evaluations/groundedness
POST /api/evaluations/task-adherence
POST /api/evaluations/tool-accuracy
POST /api/evaluations/relevance
```

## Related Documentation

- [Entra Agent Identity](Entra-Agent-Identity.md) - Agent identity management
- [Agent Registry](Agent-Registry.md) - Centralized agent inventory
- [Security Integration](Security-Integration.md) - Defender and Purview integration
- [Agent Governance](Agent-Governance-Framework.md) - Governance framework

