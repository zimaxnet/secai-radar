---
layout: default
title: Faq
---

# Frequently Asked Questions (FAQ)

Common questions and answers about SecAI Radar.

---

## General Questions

### What is SecAI Radar?

SecAI Radar is an open-source, cloud-security assessment application that:
- Collects security evidence from cloud resources
- Normalizes evidence into a common data model
- Uses AI to analyze security posture and identify gaps
- Generates human-readable assessment reports

### Is SecAI Radar free to use?

Yes, SecAI Radar is open-source and free to use. See the repository LICENSE file for details.

### What cloud providers does SecAI Radar support?

SecAI Radar is designed to be cloud-agnostic. It can work with Azure, AWS, GCP, and other cloud providers. The data model and architecture are provider-agnostic.

---

## Getting Started

### How do I get started?

1. Access the SecAI Radar application
2. Configure your security tools
3. Import security controls
4. Review the dashboard
5. Analyze gaps

See [Getting Started](/wiki/Getting-Started) for detailed instructions.

### What do I need to use SecAI Radar?

- Access to a cloud environment
- API credentials for your cloud provider
- (Optional) Azure OpenAI API access for AI features
- Modern web browser

### How do I configure my tenant?

The tenant ID is set automatically based on your URL or environment. You can change it in the URL path: `/tenant/{tenant-id}/dashboard`

---

## Controls

### How do I import controls?

1. Navigate to **Controls** page
2. Click **Import CSV**
3. Prepare CSV with required headers
4. Paste CSV content
5. Click **Import Controls**

See [Controls Guide](/wiki/Controls-Guide) for CSV format details.

### What CSV format is required?

Required headers (exact order):
```
ControlID,Domain,ControlTitle,ControlDescription,Question,RequiredEvidence,
Status,Owner,Frequency,ScoreNumeric,Weight,Notes,SourceRef,Tags,UpdatedAt
```

### What are valid status values?

- `Complete` - Control is fully implemented
- `InProgress` or `In Progress` - Control is being worked on
- `NotStarted` or `Not Started` - Control has not been started
- `NotApplicable` - Control does not apply

### Can I export controls?

Export functionality is planned for future releases. Currently, keep CSV files as backup.

---

## Tools

### How do I add a security tool?

1. Navigate to **Tools** page
2. Enter **Vendor Tool ID** (e.g., `wiz-cspm`)
3. Toggle **Enabled** if tool is active
4. Set **Configuration Score** (0.0 - 1.0)
5. Click **Save Tool Configuration**

### What is a configuration score?

The configuration score (0.0 - 1.0) represents how well a tool is configured:
- **1.0**: Perfectly configured
- **0.7-0.89**: Good configuration
- **0.5-0.69**: Fair configuration
- **0.0-0.49**: Poor configuration

### How do I find the correct tool ID?

Tool IDs follow standard naming conventions (e.g., `wiz-cspm`, `crowdstrike-falcon`). Check the tool catalog or contact your administrator.

### Should I add multiple tools?

Yes, if you have multiple tools providing similar capabilities. The system will select the best tool for each capability.

---

## Gaps

### What is a hard gap?

A **hard gap** is a missing capability with no tool coverage. No tool provides the required capability.

**Example**: Control requires SIEM capability, but no SIEM tool is deployed.

### What is a soft gap?

A **soft gap** is a capability that exists but is misconfigured. A tool provides the capability, but coverage is below the minimum threshold.

**Example**: SIEM is deployed but configuration score is 0.4 (below 0.7 threshold).

### How is coverage calculated?

Coverage = weighted sum of best tool coverage for each required capability:
- For each capability, find best tool (strength × configScore)
- Calculate weighted sum: `Σ (weight × coverage)`
- Normalize to 0-100%

### What should I prioritize?

1. **Tune existing tools** (improve configuration scores)
2. **Address soft gaps** (fix configuration issues)
3. **Address hard gaps** (add new tools if needed)

### Why prioritize tuning over adding tools?

Tuning existing tools often provides better ROI than adding new tools. It's usually faster and cheaper to improve configuration than deploy new tools.

---

## Dashboard

### What do the dashboard metrics mean?

- **Total Controls**: Total number of controls being assessed
- **Complete**: Number of controls marked as complete
- **In Progress**: Number of controls currently being worked on
- **Not Started**: Number of controls not yet started

### How do I interpret the radar chart?

The radar chart shows compliance status across domains:
- Each axis represents a security domain
- Distance from center indicates quantity
- Green = Complete, Yellow = In Progress, Red = Not Started

### Why isn't my dashboard updating?

- Check that controls have been imported
- Check that tools have been configured
- Refresh the page
- Clear browser cache if needed

---

## Technical

### What browsers are supported?

Modern browsers including:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Do I need to install anything?

No, SecAI Radar is a web application. Just access it via your browser.

### Is my data secure?

SecAI Radar follows security best practices:
- Data is scoped by tenant
- No hardcoded credentials
- Secure API communication
- See security documentation for details

### Can I use SecAI Radar offline?

No, SecAI Radar requires network connectivity to access the API and store data.

---

## Troubleshooting

### Controls not showing

- Check filters (clear filters to see all)
- Verify tenant ID is correct
- Verify controls were imported successfully

### Import fails

- Check CSV header format (exact match required)
- Verify all required fields are present
- Check CSV encoding (use UTF-8)
- Verify CSV format (commas, not semicolons)

### Coverage not updating

- Check tool configuration scores are set
- Verify tools are enabled
- Refresh page
- Wait a few moments for processing

### Tool not found

- Verify tool ID format
- Check tool catalog
- Contact administrator

---

## AI Features

### What AI models are used?

SecAI Radar uses role-based AI models:
- **Reasoning Model**: Multi-step security analysis
- **Classification Model**: Evidence classification
- **Generation Model**: Report generation

### How do I configure AI models?

AI models are configured in `config/models.yaml`. See [Model Integration](docs/wiki/model-integration.md) for details.

### Do I need Azure OpenAI access?

Azure OpenAI access is required for AI features. See [Installation](/wiki/Installation) for configuration details.

---

## Contributing

### How can I contribute?

See [Contributing](/wiki/Contributing) guide for details on:
- Reporting bugs
- Requesting features
- Contributing code
- Improving documentation

### Where do I report bugs?

Report bugs on the GitHub Issues page. Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

---

## Additional Resources

- [Getting Started](/wiki/Getting-Started)
- [User Guide](/wiki/User-Guide)
- [API Reference](/wiki/API-Reference)
- [Architecture](/wiki/Architecture)
- [Troubleshooting](/wiki/Troubleshooting)

---

**Still have questions?** Check the [Troubleshooting](/wiki/Troubleshooting) guide or open an issue on GitHub.
