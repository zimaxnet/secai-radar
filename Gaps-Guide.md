---
layout: default
title: Gaps Guide
---

# Gaps Guide

Complete guide to understanding and analyzing security gaps in SecAI Radar.

---

## Overview

The Gaps page analyzes capability coverage and identifies security gaps in your control implementations.

---

## Understanding Gaps

### What is a Gap?

A **gap** is a shortfall in security capability coverage:
- **Missing Capability**: No tool provides required capability (Hard Gap)
- **Poor Configuration**: Tool exists but misconfigured (Soft Gap)

### Gap Types

#### Hard Gaps

**Definition**: Missing capabilities with no tool coverage

**Characteristics**:
- No tool provides the required capability
- Coverage score = 0.0
- May require adding new tools

**Example**: Control requires SIEM capability, but no SIEM tool is deployed

#### Soft Gaps

**Definition**: Capabilities exist but are misconfigured

**Characteristics**:
- Tool provides capability but coverage is below threshold
- Coverage score > 0.0 but < minimum required
- Can often be fixed by improving configuration

**Example**: SIEM is deployed but configuration score is 0.4 (below 0.7 threshold)

---

## Gap Analysis Display

### Control Card

Each control shows:

#### Header Section
- **Control ID**: Control identifier
- **Domain**: Security domain
- **Coverage Percentage**: Overall coverage (0-100%)
- **Status Badge**: Good/Fair/Poor based on coverage

#### Gap Sections

**Hard Gaps** (Red Section):
- List of missing capabilities
- Capability ID and weight
- Count of hard gaps

**Soft Gaps** (Yellow Section):
- List of under-configured capabilities
- Capability ID, current coverage, minimum required
- Tool identifier (if available)
- Count of soft gaps

---

## Coverage Calculation

### How Coverage is Calculated

1. **Control Requirements**: Each control requires specific capabilities with weights
2. **Tool Matching**: For each capability, find best tool (strength × configScore)
3. **Weighted Sum**: Calculate weighted sum: `Σ (weight × coverage)`
4. **Normalization**: Normalize to 0-100% for display

### Example Calculation

**Control**: SEC-NET-0001
**Requirements**:
- Network Firewall (weight: 0.6, min: 0.7)
- URL Filtering (weight: 0.4, min: 0.6)

**Tool Coverage**:
- Palo Alto FW: Firewall strength 0.9, Config 0.8 → Coverage 0.72
- Palo Alto FW: URL Filter strength 0.85, Config 0.8 → Coverage 0.68

**Coverage Score**:
- Firewall: 0.6 × 0.72 = 0.432
- URL Filter: 0.4 × 0.68 = 0.272
- **Total**: 0.432 + 0.272 = 0.704 (70.4%)

**Gap Analysis**:
- Firewall: 0.72 > 0.7 ✓ (No gap)
- URL Filter: 0.68 > 0.6 ✓ (No gap)
- **Status**: Good (70.4% coverage)

---

## Interpreting Coverage

### Coverage Percentages

- **80-100%**: Good coverage, minor gaps
- **50-79%**: Fair coverage, some gaps
- **0-49%**: Poor coverage, significant gaps

### Status Badges

- **Good**: Coverage ≥ 80%
- **Fair**: Coverage 50-79%
- **Poor**: Coverage < 50%

---

## Remediation Strategy

### Priority 1: Tune Existing Tools

**Why**: Often better ROI than adding new tools

**Actions**:
1. Review soft gaps
2. Identify tools with low configuration scores
3. Improve tool configuration
4. Update configuration scores in Tools page
5. Re-check gaps

**Example**: SIEM has config score 0.4 → Improve to 0.8 → Coverage increases

### Priority 2: Address Soft Gaps

**Why**: Easier to fix than hard gaps

**Actions**:
1. Review soft gaps list
2. Check tool configuration scores
3. Improve configurations
4. Update scores
5. Monitor coverage improvements

### Priority 3: Address Hard Gaps

**Why**: May require new tools or capabilities

**Actions**:
1. Review hard gaps list
2. Identify missing capabilities
3. Evaluate tool options
4. Add new tools (if needed)
5. Configure new tools
6. Re-check gaps

---

## Best Practices

### 1. Regular Review

- **Weekly**: Review gaps weekly
- **After Changes**: Check gaps after tool changes
- **Monthly**: Deep dive monthly

### 2. Prioritize Tuning

- **Tune First**: Always tune existing tools first
- **Better ROI**: Configuration improvements often better than new tools
- **Incremental**: Improve scores incrementally

### 3. Document Remediation

- **Track Changes**: Document what changed
- **Measure Impact**: Track coverage improvements
- **Learn**: Learn from successful remediations

### 4. Focus on High-Impact

- **High Weight**: Prioritize capabilities with high weights
- **Critical Controls**: Focus on critical controls first
- **Business Impact**: Consider business impact

### 5. Use Filters

- **By Domain**: Focus on specific domains
- **By Status**: Focus on Poor/Fair status
- **By Gap Type**: Focus on Hard or Soft gaps

---

## Tips & Tricks

1. **Start with Soft Gaps**: Easier to fix, often better ROI
2. **Check Tool Scores**: Review configuration scores before adding tools
3. **Compare Tools**: Compare similar tools' configuration scores
4. **Track Progress**: Monitor coverage improvements over time
5. **Document**: Document remediation steps and results

---

## Troubleshooting

### No Gaps Showing

- **Check**: Controls have been imported
- **Check**: Tools have been configured
- **Check**: Tool configuration scores are set
- **Action**: Import controls and configure tools

### Coverage Not Updating

- **Check**: Tool configuration scores updated
- **Check**: Tools are enabled
- **Action**: Refresh page, wait a few moments

### Unexpected Gaps

- **Check**: Control requirements
- **Check**: Tool capabilities
- **Check**: Configuration scores
- **Action**: Review control requirements and tool capabilities

---

## Advanced Topics

### Capability Weights

Capabilities have weights indicating importance:
- **High Weight (0.5+)**: Critical capability
- **Medium Weight (0.25-0.49)**: Important capability
- **Low Weight (<0.25)**: Nice-to-have capability

**Focus**: Prioritize high-weight capabilities

### Minimum Thresholds

Capabilities have minimum thresholds:
- **High Threshold (0.8+)**: Requires excellent coverage
- **Medium Threshold (0.6-0.79)**: Requires good coverage
- **Low Threshold (<0.6)**: Requires basic coverage

**Gap**: Coverage below threshold = Soft gap

### Tool Selection

Best tool for each capability is selected:
- **Multiple Tools**: Best tool used (highest coverage)
- **Redundancy**: Multiple tools can provide redundancy
- **Configuration**: Each tool scored independently

---

**Related Guides**: [Tools Guide](/wiki/Tools-Guide) | [User Guide](/wiki/User-Guide)
