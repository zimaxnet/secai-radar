---
layout: default
title: Agent Integration
permalink: /agent-integration/
---

# Agent Integration in Assessment Workflows

## Overview

SecAI Radar integrates its multi-agent AI system directly into the assessment workflow, providing intelligent assistance at every stage of the security assessment process.

---

## Gap Analysis Integration

### Elena Agent for Recommendations

**Automatic Recommendations**

When analyzing security gaps, Elena agent automatically generates business-focused recommendations for controls with identified gaps.

**How It Works**

1. **Gap Detection** - System identifies hard gaps (missing capabilities) and soft gaps (configuration issues)
2. **Agent Analysis** - Elena agent analyzes the gaps in context of:
   - Available tenant tools
   - Current tool configuration scores
   - Coverage requirements
3. **Recommendation Generation** - Elena provides actionable advice prioritizing:
   - Tool tuning (raising ConfigScore) over adding new tools
   - Business impact (ROI, risk reduction)
   - Implementation steps

**Using AI Recommendations**

1. Navigate to **Gap Analysis** page
2. Toggle **"AI Recommendations"** switch
3. View recommendations in highlighted sections for each control with gaps
4. Review Elena's prioritized advice
5. Take action on recommendations

**Example Recommendation**

```
Control: SEC-NET-001 - Network segmentation

Hard Gaps: firewall-monitoring, traffic-analysis
Soft Gaps: network-visibility (current: 0.6, needed: 0.8)

Recommendation:
Your network segmentation control has gaps in firewall monitoring and 
traffic analysis capabilities. I recommend first tuning your existing 
Azure Firewall configuration to improve network visibility from 0.6 to 
0.8. This can be achieved by enabling enhanced logging and integrating 
with Azure Monitor. If gaps remain after optimization, consider adding 
Azure Network Watcher for comprehensive traffic analysis. This approach 
minimizes additional tool costs while improving coverage incrementally.

Business Impact: Improved network security reduces risk of lateral 
movement in case of breach, potentially avoiding $500K+ in incident 
response costs.
```

---

## Control Detail Integration

### Context-Aware Agent Chat

**Agents on Control Pages**

Control detail pages include an integrated agent chat sidebar that provides context-aware assistance.

**Available Agents**

- **Aris** - Framework questions and control requirements
- **Elena** - Risk analysis and recommendations
- **Leo** - IAM-specific guidance

**Context Awareness**

When chatting from a control page, agents automatically receive:

- Control ID and title
- Domain information
- Control description
- Your question in context

**Example Usage**

1. Navigate to a control detail page
2. Click **"Show AI Agents"** button
3. Select an agent (e.g., Aris for framework questions)
4. Ask: "What are the CIS requirements for this control?"
5. Aris responds with framework-specific guidance for that exact control

**Agent-Specific Help**

**Aris (Knowledge Base Guardian)**
- "What does this control require according to CAF?"
- "Show me NIST best practices for this control"
- "What evidence should I collect for this control?"

**Elena (Business Impact Strategist)**
- "What's the business risk if I don't implement this control?"
- "Help me prioritize remediation for this control"
- "What's the ROI of implementing this control?"

**Leo (Identity & Access Analyst)**
- "How does this control relate to RBAC?"
- "What IAM considerations apply here?"
- "Help me configure conditional access for this control"

---

## Agent Workflow Integration

### Assessment Phase Integration

**Discovery Phase**
- **Ravi** assists with infrastructure scanning
- **Kenji** helps correlate findings

**Analysis Phase**
- **Elena** provides risk analysis and prioritization
- **Aris** answers framework questions

**Remediation Phase**
- **Elena** recommends specific actions
- **Marcus** helps resolve conflicts between security and usability

**Reporting Phase**
- **Coordinator** synthesizes findings
- **Elena** generates executive summaries

---

## Best Practices

### When to Use Agents

**Use Aris When:**
- You need framework-specific guidance
- You want to understand control requirements
- You're looking for best practices

**Use Elena When:**
- You need business-focused recommendations
- You want to understand risk and ROI
- You need prioritization advice

**Use Leo When:**
- You're working on IAM controls
- You need RBAC guidance
- You're configuring access policies

### Effective Agent Queries

**Good Queries:**
- "What are the CAF requirements for control SEC-NET-001?"
- "What's the business impact if I don't implement network segmentation?"
- "How do I configure conditional access for this control?"

**Better Queries (with context):**
- When on a control page, simply ask: "What are the requirements?" - agents have context
- "Help me prioritize remediation for these gaps" - agents see the gaps
- "What evidence should I collect?" - agents know the control requirements

### Agent Collaboration

**Multi-Agent Approach:**

1. **Start with Aris** - Understand framework requirements
2. **Ask Elena** - Get business context and recommendations
3. **Consult Leo** - Get IAM-specific guidance if applicable
4. **Use Coordinator** - Synthesize insights across agents

---

## Technical Details

### API Integration

**Gap Analysis Endpoint**
```
GET /api/tenant/{tenant_id}/gaps?ai=true
```

When `ai=true` is specified, the endpoint:
1. Calculates gaps as usual
2. For controls with gaps, calls Elena agent
3. Returns recommendations in response

**Agent Chat Endpoint**
```
POST /api/agents/{agent_id}/chat
{
  "message": "Your question"
}
```

Control context is automatically included when querying from control pages.

### Recommendation Generation

Elena's recommendation generation considers:

- **Control Context** - Control ID, title, domain
- **Gap Analysis** - Hard gaps and soft gaps identified
- **Tool Inventory** - Available tenant tools and configuration scores
- **Coverage Score** - Current coverage percentage

The agent provides:
- Prioritized recommendations (tune existing tools first)
- Business impact analysis
- Implementation steps
- Risk reduction context

---

## Examples

### Example 1: Gap Analysis with AI

1. Navigate to **Gap Analysis** page
2. Toggle **AI Recommendations** ON
3. View gaps:
   - Control SEC-ID-001 has 2 hard gaps, 1 soft gap
   - Elena recommendation appears automatically
4. Read Elena's recommendation:
   - "Prioritize tuning Azure AD conditional access policies..."
   - "Add Microsoft Defender for Identity if gaps remain..."
   - "Expected risk reduction: 40% reduction in account compromise risk"
5. Click on control to view details and take action

### Example 2: Control-Specific Agent Help

1. Navigate to **Controls** page
2. Click on control **SEC-NET-001**
3. Click **"Show AI Agents"** button
4. Select **Aris** agent
5. Ask: "What evidence should I collect for this control?"
6. Aris responds with framework-specific evidence requirements
7. Switch to **Elena** and ask: "What's the risk if I skip this control?"
8. Elena provides business-focused risk analysis

---

## Troubleshooting

### Agents Not Responding

- Check that `GOOGLE_API_KEY` is configured
- Verify network connectivity
- Check browser console for errors

### Recommendations Not Appearing

- Ensure **AI Recommendations** toggle is ON
- Verify controls have identified gaps
- Check backend logs for agent errors

### Context Missing in Chat

- Ensure you're on a control detail page
- Verify control data loaded successfully
- Check agent receives context in API call

---

## Related Documentation

- [Multi-Agent System](docs/wiki/Multi-Agent-System.md) - Agent architecture
- [Platform Features](docs/wiki/Platform-Features.md) - Overall platform features
- [Controls Guide](docs/wiki/Controls-Guide.md) - Control management
- [Gaps Guide](docs/wiki/Gaps-Guide.md) - Gap analysis
- [User Guide](docs/wiki/User-Guide.md) - Complete user documentation

---

**Last Updated**: 2025-01-15

