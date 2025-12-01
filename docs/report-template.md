# SecAI Radar — Assessment Report Template

> Generic assessment report template for cloud security assessments. This template is vendor-agnostic and contains no customer-specific references.

---

## Report Structure

### 1. Executive Summary

**Overview**
- Assessment scope and objectives
- Assessment methodology
- Key findings summary
- Overall security posture score

**Executive Summary Narrative**
> AI-generated narrative explaining the overall security posture, key strengths, and critical gaps. This section should be written in plain language suitable for executive leadership.

**Key Metrics**
- Total controls assessed: `{count}`
- Controls compliant: `{count}` (`{percentage}%`)
- Controls non-compliant: `{count}` (`{percentage}%`)
- Controls not applicable: `{count}` (`{percentage}%`)
- Overall security score: `{score}/100`

**Critical Findings**
- List of high-priority findings requiring immediate attention
- Each finding should include: control ID, title, impact, recommendation

---

### 2. Assessment Methodology

**Scope**
- Assessment period: `{start_date}` to `{end_date}`
- Tenants/subscriptions assessed: `{list}`
- Security domains covered: `{list}`
- Assessment approach: `{description}`

**Data Collection**
- Evidence collection methods: `{list}`
- Tools and collectors used: `{list}` (generic names only)
- Data sources: `{list}`

**Assessment Framework**
- Framework used: `{framework_name}` (generic, e.g., "Industry Standard Security Framework")
- Control mapping: `{description}`
- Scoring methodology: `{description}`

---

### 3. Findings by Domain

For each security domain (e.g., Network, Identity, Logging, Security):

### Domain: {Domain Name} (Code: {DOMAIN_CODE})

**Domain Overview**
> AI-generated narrative explaining the security posture for this domain, including strengths, weaknesses, and trends.

**Domain Score**
- Domain compliance score: `{score}/100`
- Controls assessed: `{count}`
- Controls compliant: `{count}` (`{percentage}%`)
- Controls non-compliant: `{count}` (`{percentage}%`)

**Findings**

For each control in this domain:

#### Control: {Control Title} (ID: {CONTROL_ID})

**Status**: `{compliant|non_compliant|not_applicable|unknown}`

**Control Description**
> {Control description from framework}

**Question**
> {Assessment question}

**Finding**
> AI-generated narrative explaining the current state, evidence found, and compliance status.

**Evidence**
- Evidence type: `{type}`
- Evidence sources: `{list}`
- Evidence links: `{links}`
- Screenshots/documents: `{attachments}`

**Coverage Analysis**
- Capability requirements: `{list}`
- Tool coverage: `{analysis}`
- Coverage score: `{score}/100`
- Configuration quality: `{score}/100`

**Recommendations**
> AI-generated recommendations for remediation, including:
> - Specific actions to achieve compliance
> - Priority level (high/medium/low)
> - Estimated effort
> - Reference to best practices

**Remediation Steps**
1. `{step 1}`
2. `{step 2}`
3. `{step 3}`

---

### 4. Gap Analysis

**Gap Summary**
- Total gaps identified: `{count}`
- High-priority gaps: `{count}`
- Medium-priority gaps: `{count}`
- Low-priority gaps: `{count}`

**Gap Categories**

#### Hard Gaps (Missing Capabilities)
- Gaps where required capabilities are not covered by any tool
- List of controls with hard gaps
- Impact analysis

#### Soft Gaps (Configuration Issues)
- Gaps where capabilities exist but are misconfigured
- List of controls with soft gaps
- Configuration recommendations

#### Coverage Gaps (Partial Coverage)
- Gaps where capabilities are partially covered
- List of controls with partial coverage
- Recommendations for improvement

**Gap Prioritization**
- Priority matrix based on impact and effort
- Recommended remediation roadmap
- Timeline estimates

---

### 5. Recommendations and Roadmap

**Immediate Actions (0-30 days)**
> AI-generated list of high-priority recommendations requiring immediate attention.

**Short-term Improvements (1-3 months)**
> AI-generated list of recommendations for short-term improvements.

**Long-term Roadmap (3-12 months)**
> AI-generated strategic roadmap for long-term security posture improvement.

**Recommendations by Domain**
- Network Security: `{list}`
- Identity and Access Management: `{list}`
- Logging and Monitoring: `{list}`
- Security Operations: `{list}`
- (Other domains as applicable)

---

### 6. Appendices

**Appendix A: Control Coverage Matrix**
- Matrix showing all controls, their status, and tool coverage
- Format: Table or spreadsheet

**Appendix B: Evidence Index**
- Complete list of evidence collected
- Links to evidence files
- Evidence metadata

**Appendix C: Tool Inventory**
- List of security tools in use
- Tool capabilities and coverage
- Configuration quality scores

**Appendix D: Scoring Methodology**
- Detailed explanation of scoring approach
- Weighting factors
- Calculation formulas

**Appendix E: Glossary**
- Terms and definitions
- Acronyms
- Framework references

---

## Report Generation Guidelines

### AI-Generated Content
- All narrative sections should be generated by the AI model
- Use the `generation_model` role for report writing
- Maintain consistency in tone and style
- Ensure explainability and traceability

### Evidence Linking
- All findings must link to evidence in Bronze/Silver layers
- Provide direct links to evidence files where possible
- Include screenshot references for visual evidence

### Vendor-Agnostic Language
- Use generic terms: "security tool" instead of vendor names
- Use generic capability names: "SIEM capability" instead of "Sentinel"
- Avoid customer-specific references
- Use placeholder patterns: `{tenant_id}`, `{subscription_id}`

### Format Support
- **Markdown**: Primary format for version control and editing
- **HTML**: For web viewing and sharing
- **DOCX**: For final delivery to customers

### Quality Assurance
- Review AI-generated content for accuracy
- Verify evidence links are valid
- Ensure all findings are supported by evidence
- Check for consistency across sections

---

## Template Variables

The following variables should be replaced during report generation:

- `{count}` - Counts and numbers
- `{percentage}` - Percentages
- `{score}` - Scores (0-100)
- `{date}` - Dates in ISO format
- `{list}` - Lists of items
- `{description}` - Descriptive text
- `{Domain Name}` - Domain name (e.g., "Network Security")
- `{DOMAIN_CODE}` - Domain code (e.g., "NET")
- `{Control Title}` - Control title
- `{CONTROL_ID}` - Control ID (e.g., "SEC-NET-0007")
- `{tenant_id}` - Tenant identifier (generic)
- `{subscription_id}` - Subscription identifier (generic)

---

## References

- `blueprint.md` — Architecture overview
- `data-model.md` — Data layer and evidence structure
- `config/frameworks.yaml` — Control and domain definitions

