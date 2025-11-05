# Tools Guide

Complete guide to configuring security tools in SecAI Radar.

---

## Overview

The Tools page allows you to manage security tool configurations, set configuration quality scores, and enable/disable tools.

---

## Understanding Tool Configuration

### Why Configure Tools?

Security tools are assessed based on:
- **Capability Coverage**: What security capabilities the tool provides
- **Configuration Quality**: How well the tool is configured
- **Coverage Score**: Combined metric (capability strength × config score)

### Configuration Score

The configuration score (0.0 - 1.0) represents:
- **1.0**: Perfectly configured, fully optimized
- **0.9 - 0.99**: Excellent configuration
- **0.7 - 0.89**: Good configuration, minor improvements possible
- **0.5 - 0.69**: Fair configuration, significant improvements needed
- **0.0 - 0.49**: Poor configuration, major improvements required

---

## Adding a Tool

### Step 1: Enter Vendor Tool ID

Enter the standard tool identifier:
- **Format**: `vendor-tool-name` (lowercase, hyphenated)
- **Examples**:
  - `wiz-cspm` - Wiz CSPM
  - `crowdstrike-falcon` - CrowdStrike Falcon
  - `paloalto-fw` - Palo Alto Firewall
  - `google-secops` - Google SecOps

**Finding Tool IDs**:
- Check the tool catalog in the system
- Use standard naming conventions
- Contact administrator if unsure

### Step 2: Enable/Disable

Toggle tool activation:
- **Enabled**: Tool is active and contributing to coverage
- **Disabled**: Tool is not active (excluded from analysis)

**When to Disable**:
- Tool is not deployed
- Tool is being replaced
- Tool is temporarily unavailable

### Step 3: Set Configuration Score

Set the configuration quality score:
- **Use Slider**: Drag slider for visual selection
- **Enter Value**: Type value directly (0.0 - 1.0)
- **Default**: 0.8 (good configuration)

**Scoring Guidelines**:
- **0.9 - 1.0**: Fully optimized, all features enabled
- **0.7 - 0.89**: Well configured, minor tuning possible
- **0.5 - 0.69**: Basic configuration, needs improvement
- **0.0 - 0.49**: Poorly configured, major work needed

### Step 4: Save Configuration

Click **Save Tool Configuration** to:
- Save tool to inventory
- Update coverage calculations
- Refresh gap analysis

---

## Configuration Score Guide

### Excellent (0.9 - 1.0)

**Characteristics**:
- All features enabled
- Optimal configuration
- Regular tuning
- Best practices followed

**Example**: WAF with all rules enabled, custom rules configured, logging enabled

### Good (0.7 - 0.89)

**Characteristics**:
- Core features enabled
- Good configuration
- Some tuning done
- Most best practices followed

**Example**: SIEM with core log sources configured, basic correlation rules

### Fair (0.5 - 0.69)

**Characteristics**:
- Basic features enabled
- Default configuration
- Minimal tuning
- Some best practices followed

**Example**: EDR with default policies, basic monitoring enabled

### Poor (0.0 - 0.49)

**Characteristics**:
- Limited features enabled
- Poor configuration
- No tuning
- Best practices not followed

**Example**: Firewall with default rules only, no custom policies

---

## Best Practices

### 1. Accurate Scoring

- **Be Honest**: Accurate scores lead to better analysis
- **Regular Updates**: Update scores as tools are tuned
- **Document Reasons**: Note why scores are set (for future reference)

### 2. Prioritize Tuning

- **Improve Existing**: Tune existing tools before adding new ones
- **Higher ROI**: Often better to improve config than add tools
- **Incremental**: Improve scores incrementally over time

### 3. Regular Reviews

- **Monthly**: Review tool configurations monthly
- **After Changes**: Update scores after tool changes
- **Document**: Document configuration improvements

### 4. Enable/Disable Appropriately

- **Enable**: Only tools that are actively deployed
- **Disable**: Tools that are not in use
- **Update**: Update status as tools are deployed/retired

### 5. Tool Selection

- **Use Standards**: Use standard tool identifiers
- **Check Catalog**: Verify tool exists in catalog
- **Ask Questions**: Contact administrator if unsure

---

## Tool Coverage Analysis

### How Tools Affect Coverage

Tools contribute to control coverage based on:
1. **Capability Match**: Tool provides required capability
2. **Capability Strength**: How well tool provides capability (0-1)
3. **Configuration Score**: How well tool is configured (0-1)
4. **Coverage Score**: `strength × configScore`

### Example Calculation

**Control**: SEC-NET-0001 (requires network firewall)
**Tool**: Palo Alto Firewall
- Capability Strength: 0.9 (excellent firewall capability)
- Configuration Score: 0.8 (good configuration)
- **Coverage Score**: 0.9 × 0.8 = 0.72 (72%)

**To Improve Coverage**:
- Improve configuration: 0.9 × 0.95 = 0.855 (85.5%)
- Add second tool: max(0.855, 0.7) = 0.855 (if second tool is weaker)

---

## Tips & Tricks

1. **Start Conservative**: Start with lower scores, increase as you improve
2. **Regular Updates**: Update scores monthly or after changes
3. **Document Changes**: Keep notes on why scores changed
4. **Compare Tools**: Compare configuration scores across similar tools
5. **Review Gaps**: Check gaps page to see impact of configuration changes

---

## Troubleshooting

### Tool Not Found

- **Error**: "Tool not found in catalog"
- **Solution**: Verify tool ID format, check catalog, contact administrator

### Coverage Not Updating

- **Check**: Tool is enabled
- **Check**: Configuration score is set
- **Action**: Refresh gaps page, wait a few moments

### Score Not Saving

- **Check**: All required fields filled
- **Check**: Network connection
- **Action**: Try again, check for error messages

---

## Advanced Topics

### Multiple Tools

- **Multiple Coverage**: Best tool for each capability is selected
- **Redundancy**: Multiple tools can provide redundancy
- **Configuration**: Each tool scored independently

### Tool Lifecycle

- **Deployment**: Add tool when deployed
- **Tuning**: Increase score as tool is tuned
- **Retirement**: Disable tool when retired
- **Replacement**: Disable old, enable new tool

---

**Related Guides**: [Gaps Guide](/wiki/Gaps-Guide) | [User Guide](/wiki/User-Guide)

