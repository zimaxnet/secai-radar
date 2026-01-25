/**
 * SecAI Radar Demo Data
 * Comprehensive mock data for demonstration without backend connectivity
 */

// Security Domains
export const DOMAINS = {
  NET: "Network Security",
  ID: "Identity Management",
  PA: "Privileged Access",
  DATA: "Data Protection",
  ASSET: "Asset Management",
  LOG: "Logging & Threat Detection",
  IR: "Incident Response",
  POST: "Posture & Vulnerability Management",
  END: "Endpoint Security",
  BAK: "Backup & Recovery",
  DEV: "DevOps Security",
  GOV: "Governance & Strategy"
};

// Vendor Tools with capabilities
export const VENDOR_TOOLS = [
  { id: "cloudflare", name: "Cloudflare", vendor: "Cloudflare", capabilities: ["waf", "ddos", "casb", "ztna", "swg"], enabled: true, configScore: 0.85 },
  { id: "cribl", name: "Cribl", vendor: "Cribl", capabilities: ["observability-pipeline", "log-collect"], enabled: true, configScore: 0.75 },
  { id: "crowdstrike-falcon", name: "CrowdStrike Falcon", vendor: "CrowdStrike", capabilities: ["edr", "fim", "identity-protection", "ti"], enabled: true, configScore: 0.90 },
  { id: "google-secops", name: "Google SecOps (Chronicle)", vendor: "Google", capabilities: ["siem", "ueba", "ti"], enabled: true, configScore: 0.85 },
  { id: "google-secops-siemplify", name: "Google SecOps (Siemplify)", vendor: "Google", capabilities: ["soar"], enabled: true, configScore: 0.70 },
  { id: "virustotal", name: "VirusTotal", vendor: "Google", capabilities: ["ti", "sandboxing"], enabled: true, configScore: 0.80 },
  { id: "mandiant-breach-analytics", name: "Mandiant Breach Analytics", vendor: "Mandiant", capabilities: ["ti", "ir"], enabled: false, configScore: 0.0 },
  { id: "mandiant-managed-soc", name: "Mandiant Managed SOC", vendor: "Mandiant", capabilities: ["ir", "ti"], enabled: false, configScore: 0.0 },
  { id: "paloalto-fw", name: "Palo Alto Firewall", vendor: "Palo Alto Networks", capabilities: ["ns-firewall", "ids-ips", "url-filtering"], enabled: true, configScore: 0.88 },
  { id: "paloalto-wildfire", name: "WildFire", vendor: "Palo Alto Networks", capabilities: ["sandboxing", "ti"], enabled: true, configScore: 0.75 },
  { id: "prisma-access", name: "Prisma Access", vendor: "Palo Alto Networks", capabilities: ["ztna", "swg", "casb"], enabled: true, configScore: 0.72 },
  { id: "proofpoint-efd", name: "Proofpoint EFD", vendor: "Proofpoint", capabilities: ["email-sec", "dlp"], enabled: true, configScore: 0.82 },
  { id: "proofpoint-tr", name: "Proofpoint Threat Response", vendor: "Proofpoint", capabilities: ["soar"], enabled: false, configScore: 0.0 },
  { id: "proofpoint-psat", name: "Proofpoint PSAT", vendor: "Proofpoint", capabilities: ["phish-sim"], enabled: true, configScore: 0.78 },
  { id: "proofpoint-phalarm", name: "Proofpoint PhishAlarm", vendor: "Proofpoint", capabilities: ["user-reporting"], enabled: true, configScore: 0.65 },
  { id: "upguard", name: "UpGuard", vendor: "UpGuard", capabilities: ["third-party-risk", "externalscan"], enabled: true, configScore: 0.70 },
  { id: "qualys-vm", name: "Qualys VM", vendor: "Qualys", capabilities: ["vuln-mgmt"], enabled: true, configScore: 0.85 },
  { id: "veracode", name: "Veracode", vendor: "Veracode", capabilities: ["sast", "dast", "sca"], enabled: true, configScore: 0.80 },
  { id: "wiz-cspm", name: "Wiz", vendor: "Wiz", capabilities: ["cspm", "cnapp"], enabled: true, configScore: 0.88 },
  { id: "microsoft-defender", name: "Microsoft Defender for Cloud", vendor: "Microsoft", capabilities: ["cspm", "cwpp", "vulnerability-assessment"], enabled: true, configScore: 0.75 },
  { id: "azure-sentinel", name: "Microsoft Sentinel", vendor: "Microsoft", capabilities: ["siem", "soar"], enabled: true, configScore: 0.80 }
];

// Capability definitions
export const CAPABILITIES = [
  { id: "siem", name: "SIEM" },
  { id: "soar", name: "SOAR" },
  { id: "ueba", name: "UEBA" },
  { id: "edr", name: "EDR" },
  { id: "fim", name: "FIM" },
  { id: "identity-protection", name: "Identity Protection" },
  { id: "ids-ips", name: "IDS/IPS" },
  { id: "ns-firewall", name: "Network Firewall" },
  { id: "url-filtering", name: "URL Filtering" },
  { id: "sandboxing", name: "Sandboxing" },
  { id: "waf", name: "WAF" },
  { id: "ddos", name: "DDoS Protection" },
  { id: "ztna", name: "ZTNA" },
  { id: "swg", name: "Secure Web Gateway" },
  { id: "casb", name: "CASB" },
  { id: "cspm", name: "CSPM" },
  { id: "cnapp", name: "CNAPP" },
  { id: "email-sec", name: "Email Security" },
  { id: "phish-sim", name: "Phishing Simulation" },
  { id: "user-reporting", name: "User Reporting" },
  { id: "vuln-mgmt", name: "Vulnerability Management" },
  { id: "sast", name: "SAST" },
  { id: "dast", name: "DAST" },
  { id: "sca", name: "SCA" },
  { id: "third-party-risk", name: "Third-Party Risk" },
  { id: "externalscan", name: "External Attack Surface" },
  { id: "ti", name: "Threat Intelligence" },
  { id: "observability-pipeline", name: "Observability Pipeline" },
  { id: "log-collect", name: "Log Collection" },
  { id: "dlp", name: "Data Loss Prevention" },
  { id: "backup", name: "Backup & Recovery" },
  { id: "ir", name: "Incident Response" }
];

// Demo Controls data
export const DEMO_CONTROLS = [
  // Network Security (NET)
  { ControlID: "SEC-NET-0001", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Establish network segmentation boundaries", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "VNET Isolation and usage of NSG rules have been implemented." },
  { ControlID: "SEC-NET-0002", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Secure cloud native services with network controls", Status: "InProgress", ScoreNumeric: 60, Criticality: "High", ComplianceStatus: "Partial", Observations: "Private Endpoints planned for MCA Subscriptions." },
  { ControlID: "SEC-NET-0003", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Deploy firewall at the edge of enterprise network", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Palo Alto deployed for protection at Edge, Cloudflare and Azure WAF at the edge." },
  { ControlID: "SEC-NET-0004", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Deploy intrusion detection/prevention systems (IDS/IPS)", Status: "InProgress", ScoreNumeric: 60, Criticality: "High", ComplianceStatus: "Partial", Observations: "Palo Alto NGFW configured with IPS/IDS." },
  { ControlID: "SEC-NET-0005", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Deploy DDoS protection", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Cloudflare DDoS protection enabled at VNET level." },
  { ControlID: "SEC-NET-0006", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Deploy web application firewall", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Cloudflare at Edge and Azure WAF in use." },
  { ControlID: "SEC-NET-0007", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Simplify network security configuration", Status: "NotStarted", ScoreNumeric: 0, Criticality: "Medium", ComplianceStatus: "Not Started", Observations: "" },
  { ControlID: "SEC-NET-0008", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Detect and disable insecure services and protocols", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "All insecure ports and protocols disabled by default." },
  { ControlID: "SEC-NET-0009", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Connect on-premises or cloud network privately", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "MCA uses ExpressRoute." },
  { ControlID: "SEC-NET-0010", Domain: "Network Security", DomainCode: "NET", ControlTitle: "Ensure Domain Name System (DNS) security", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Secure DNS provider in use." },
  
  // Identity Management (ID)
  { ControlID: "SEC-ID-0001", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Use centralized identity and authentication system", Status: "NotStarted", ScoreNumeric: 0, Criticality: "High", ComplianceStatus: "Partial", Observations: "AD on-prem with AD Connect to Entra ID. Some storage accounts enabled with shared key access." },
  { ControlID: "SEC-ID-0002", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Protect identity and authentication systems", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "MFA mandated for admin access, CyberArk PAM, EntraID PIM in use." },
  { ControlID: "SEC-ID-0003", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Manage application identities securely and automatically", Status: "NotStarted", ScoreNumeric: 0, Criticality: "Medium", ComplianceStatus: "Not Started", Observations: "" },
  { ControlID: "SEC-ID-0004", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Authenticate server and services", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Resources configured with TLS 1.2." },
  { ControlID: "SEC-ID-0005", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Use single sign-on (SSO) for application access", Status: "Complete", ScoreNumeric: 100, Criticality: "Medium", ComplianceStatus: "Compliant", Observations: "Okta and Entra ID configured." },
  { ControlID: "SEC-ID-0006", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Use strong authentication controls", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "MFA enforced for admin access, CyberArk PAM in use." },
  { ControlID: "SEC-ID-0007", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Restrict resource access based on conditions", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Zero Trust: Geolocation-based access policies enabled." },
  { ControlID: "SEC-ID-0008", Domain: "Identity Management", DomainCode: "ID", ControlTitle: "Restrict the exposure of credentials and secrets", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Veracode for scanning, Azure Key Vault for secrets." },

  // Privileged Access (PA)
  { ControlID: "SEC-PA-0001", Domain: "Privileged Access", DomainCode: "PA", ControlTitle: "Separate and limit highly privileged/administrative users", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "PIM and CyberArk in use for privileged access." },
  { ControlID: "SEC-PA-0002", Domain: "Privileged Access", DomainCode: "PA", ControlTitle: "Avoid standing access for user accounts", Status: "InProgress", ScoreNumeric: 70, Criticality: "High", ComplianceStatus: "Partial", Observations: "JIT access being implemented via PIM." },
  { ControlID: "SEC-PA-0003", Domain: "Privileged Access", DomainCode: "PA", ControlTitle: "Manage lifecycle of identities and entitlements", Status: "Complete", ScoreNumeric: 100, Criticality: "Medium", ComplianceStatus: "Compliant", Observations: "Identity governance policies established." },

  // Data Protection (DATA)
  { ControlID: "SEC-DATA-0001", Domain: "Data Protection", DomainCode: "DATA", ControlTitle: "Discover, classify, and label sensitive data", Status: "InProgress", ScoreNumeric: 50, Criticality: "High", ComplianceStatus: "Partial", Observations: "Microsoft Purview being deployed for data classification." },
  { ControlID: "SEC-DATA-0002", Domain: "Data Protection", DomainCode: "DATA", ControlTitle: "Use encryption at rest for data protection", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "All storage encrypted with customer-managed keys." },
  { ControlID: "SEC-DATA-0003", Domain: "Data Protection", DomainCode: "DATA", ControlTitle: "Use encryption in transit for data protection", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "TLS 1.2+ enforced on all services." },
  { ControlID: "SEC-DATA-0004", Domain: "Data Protection", DomainCode: "DATA", ControlTitle: "Protect keys and certificates", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Azure Key Vault with HSM protection." },

  // Logging & Threat Detection (LOG)
  { ControlID: "SEC-LOG-0001", Domain: "Logging & Threat Detection", DomainCode: "LOG", ControlTitle: "Enable threat detection services", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Microsoft Defender for Cloud and Google SecOps enabled." },
  { ControlID: "SEC-LOG-0002", Domain: "Logging & Threat Detection", DomainCode: "LOG", ControlTitle: "Enable security logging for cloud resources", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "All resource logs sent to Log Analytics and Chronicle." },
  { ControlID: "SEC-LOG-0003", Domain: "Logging & Threat Detection", DomainCode: "LOG", ControlTitle: "Enable network logging for threat detection", Status: "InProgress", ScoreNumeric: 60, Criticality: "High", ComplianceStatus: "Partial", Observations: "NSG flow logs enabled, traffic analytics pending." },

  // Incident Response (IR)
  { ControlID: "SEC-IR-0001", Domain: "Incident Response", DomainCode: "IR", ControlTitle: "Prepare for incident response", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "IR playbooks and runbooks documented." },
  { ControlID: "SEC-IR-0002", Domain: "Incident Response", DomainCode: "IR", ControlTitle: "Implement incident identification and triage", Status: "InProgress", ScoreNumeric: 75, Criticality: "High", ComplianceStatus: "Partial", Observations: "Automated triage with SOAR being implemented." },

  // Posture & Vulnerability Management (POST)
  { ControlID: "SEC-POST-0001", Domain: "Posture & Vulnerability Management", DomainCode: "POST", ControlTitle: "Establish and maintain a secure configuration baseline", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Azure Policy and CIS benchmarks applied." },
  { ControlID: "SEC-POST-0002", Domain: "Posture & Vulnerability Management", DomainCode: "POST", ControlTitle: "Ensure software is supported and updated", Status: "InProgress", ScoreNumeric: 80, Criticality: "High", ComplianceStatus: "Partial", Observations: "Automated patching enabled for most workloads." },
  { ControlID: "SEC-POST-0003", Domain: "Posture & Vulnerability Management", DomainCode: "POST", ControlTitle: "Conduct vulnerability assessments", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Qualys VM and Wiz scanning active." },

  // Endpoint Security (END)
  { ControlID: "SEC-END-0001", Domain: "Endpoint Security", DomainCode: "END", ControlTitle: "Deploy endpoint detection and response (EDR)", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "CrowdStrike Falcon deployed on all endpoints." },
  { ControlID: "SEC-END-0002", Domain: "Endpoint Security", DomainCode: "END", ControlTitle: "Enable endpoint protection platform", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "CrowdStrike real-time protection enabled." },

  // Backup & Recovery (BAK)
  { ControlID: "SEC-BAK-0001", Domain: "Backup & Recovery", DomainCode: "BAK", ControlTitle: "Ensure regular automated backups", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Azure Backup configured for all critical workloads." },
  { ControlID: "SEC-BAK-0002", Domain: "Backup & Recovery", DomainCode: "BAK", ControlTitle: "Protect backup data", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Immutable backup storage enabled." },

  // DevOps Security (DEV)
  { ControlID: "SEC-DEV-0001", Domain: "DevOps Security", DomainCode: "DEV", ControlTitle: "Ensure secure DevOps by auditing controls", Status: "InProgress", ScoreNumeric: 70, Criticality: "High", ComplianceStatus: "Partial", Observations: "GitHub Advanced Security being rolled out." },
  { ControlID: "SEC-DEV-0002", Domain: "DevOps Security", DomainCode: "DEV", ControlTitle: "Integrate static application security testing", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Veracode SAST integrated into CI/CD." },
  { ControlID: "SEC-DEV-0003", Domain: "DevOps Security", DomainCode: "DEV", ControlTitle: "Integrate dynamic application security testing", Status: "InProgress", ScoreNumeric: 60, Criticality: "Medium", ComplianceStatus: "Partial", Observations: "Veracode DAST being expanded." },

  // Governance & Strategy (GOV)
  { ControlID: "SEC-GOV-0001", Domain: "Governance & Strategy", DomainCode: "GOV", ControlTitle: "Define and implement enterprise security strategy", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "Security strategy documented and approved." },
  { ControlID: "SEC-GOV-0002", Domain: "Governance & Strategy", DomainCode: "GOV", ControlTitle: "Define and implement security roles and responsibilities", Status: "Complete", ScoreNumeric: 100, Criticality: "High", ComplianceStatus: "Compliant", Observations: "RACI matrix established for security operations." },

  // Asset Management (ASSET)
  { ControlID: "SEC-ASSET-0001", Domain: "Asset Management", DomainCode: "ASSET", ControlTitle: "Establish and maintain an asset inventory", Status: "InProgress", ScoreNumeric: 80, Criticality: "High", ComplianceStatus: "Partial", Observations: "Azure Resource Graph and tagging being standardized." },
  { ControlID: "SEC-ASSET-0002", Domain: "Asset Management", DomainCode: "ASSET", ControlTitle: "Manage the lifecycle of assets", Status: "InProgress", ScoreNumeric: 70, Criticality: "Medium", ComplianceStatus: "Partial", Observations: "Decommissioning processes being formalized." }
];

// Generate summary by domain
export function getDemoSummaryByDomain() {
  const domains: Record<string, { domain: string; total: number; complete: number; inProgress: number; notStarted: number }> = {};
  
  DEMO_CONTROLS.forEach(c => {
    const code = c.DomainCode;
    if (!domains[code]) {
      domains[code] = { domain: code, total: 0, complete: 0, inProgress: 0, notStarted: 0 };
    }
    domains[code].total++;
    if (c.Status === "Complete") domains[code].complete++;
    else if (c.Status === "InProgress") domains[code].inProgress++;
    else domains[code].notStarted++;
  });
  
  return Object.values(domains);
}

// Generate gaps data
export function getDemoGaps() {
  const gaps = DEMO_CONTROLS.filter(c => c.Status !== "Complete").map(c => {
    // Generate realistic gaps based on control type
    const hardGaps: { capabilityId: string; weight: number }[] = [];
    const softGaps: { capabilityId: string; weight: number; best: number; min: number }[] = [];
    
    // Add relevant gaps based on domain
    if (c.DomainCode === "NET") {
      if (c.Status === "NotStarted") {
        hardGaps.push({ capabilityId: "adaptive-hardening", weight: 0.6 });
      } else {
        softGaps.push({ capabilityId: "ns-firewall", weight: 0.4, best: 0.5, min: 0.7 });
      }
    } else if (c.DomainCode === "ID") {
      if (c.Status === "NotStarted") {
        hardGaps.push({ capabilityId: "identity-protection", weight: 0.8 });
      } else {
        softGaps.push({ capabilityId: "mfa-enforcement", weight: 0.6, best: 0.6, min: 0.8 });
      }
    } else if (c.DomainCode === "LOG") {
      softGaps.push({ capabilityId: "siem", weight: 0.7, best: 0.6, min: 0.8 });
    } else if (c.DomainCode === "DEV") {
      if (c.Status === "InProgress") {
        softGaps.push({ capabilityId: "dast", weight: 0.5, best: 0.5, min: 0.7 });
      }
    } else {
      // Generic soft gap for other domains
      softGaps.push({ capabilityId: "generic-capability", weight: 0.5, best: 0.5, min: 0.7 });
    }
    
    const coverage = c.ScoreNumeric / 100;
    
    return {
      ControlID: c.ControlID,
      ControlTitle: c.ControlTitle,
      Domain: c.Domain,
      DomainPartition: c.DomainCode,
      Coverage: coverage,
      HardGaps: hardGaps,
      SoftGaps: softGaps
    };
  });
  
  return gaps;
}

// Generate demo report
export function getDemoReport(tenantId: string) {
  const summaryByDomain = getDemoSummaryByDomain();
  const gaps = getDemoGaps();
  
  const totalControls = DEMO_CONTROLS.length;
  const totalGaps = gaps.length;
  const criticalGaps = gaps.filter(g => g.HardGaps.length > 0).length;
  
  return {
    tenantId,
    summary: {
      byDomain: summaryByDomain,
      totalControls,
      totalGaps,
      criticalGaps
    },
    gaps,
    generatedAt: new Date().toISOString(),
    executiveSummary: `## Executive Summary

**Security Posture Assessment for ${tenantId}**

### Overall Assessment
The organization demonstrates a **strong security foundation** with ${Math.round(((totalControls - totalGaps) / totalControls) * 100)}% of security controls in compliant status. The security program shows maturity in core areas including network perimeter protection, identity management, and endpoint security.

### Key Strengths
- **Network Security**: Edge protection with Palo Alto, Cloudflare DDoS, and Azure WAF provides comprehensive perimeter defense
- **Identity & Access**: MFA enforcement, CyberArk PAM, and Entra ID PIM demonstrate strong identity governance
- **Endpoint Protection**: CrowdStrike Falcon deployment ensures comprehensive endpoint visibility
- **Data Protection**: Encryption at rest and in transit with customer-managed keys

### Areas Requiring Attention
- **${criticalGaps} Critical Gaps**: Controls with missing capabilities requiring immediate attention
- **${totalGaps - criticalGaps} Configuration Gaps**: Controls with below-threshold tool configurations
- **Network Hardening**: Adaptive Network Hardening recommendations not yet implemented
- **Application Identity**: Managed identity adoption for workloads incomplete

### Priority Recommendations
1. Enable Adaptive Network Hardening in Microsoft Defender for Cloud
2. Migrate remaining storage accounts from shared key to Azure AD authentication
3. Expand Veracode DAST coverage to all production applications
4. Complete SOAR playbook implementation for automated incident response

### Next Steps
Quarterly review scheduled to track remediation progress. Focus on closing critical gaps within 30 days and configuration gaps within 90 days.`,
    aiEnabled: true
  };
}

// AI Recommendations (cached responses for demo)
export function getDemoAIRecommendation(controlId: string): string {
  const control = DEMO_CONTROLS.find(c => c.ControlID === controlId);
  if (!control) return "Control not found.";
  
  const recommendations: Record<string, string> = {
    "SEC-NET-0002": `## Remediation Plan for ${controlId}

**Current Status**: Private Endpoints partially deployed

### Immediate Actions (0-7 days)
1. **Inventory Assessment**: Document all PaaS services requiring Private Link
2. **DNS Planning**: Plan Azure Private DNS zones for each service type
3. **Network Design**: Ensure subnets have sufficient IP space for private endpoints

### Short-term Actions (7-30 days)
1. **Deploy Private Endpoints**: 
   - Azure Storage accounts: Use \`privatelink.blob.core.windows.net\`
   - Azure Key Vault: Use \`privatelink.vaultcore.azure.net\`
   - Azure SQL: Use \`privatelink.database.windows.net\`
2. **Disable Public Access**: After Private Link is confirmed working
3. **Update NSG Rules**: Remove public IP allowances

### Tool Configuration Recommendations
- **Wiz** (Config Score: 0.88): Enable "Private Endpoint Coverage" policy
- **Microsoft Defender** (Config Score: 0.75): Enable "Secure transfer to storage" recommendation auto-remediation

### Validation
- Test connectivity through private endpoints
- Verify DNS resolution returns private IP addresses
- Confirm public access denied`,

    "SEC-NET-0004": `## Remediation Plan for ${controlId}

**Current Status**: IDS/IPS partially configured via Palo Alto

### Recommended Improvements
1. **Enable Azure Firewall IDPS** (Premium SKU)
   - Alert mode first, then move to Alert and Deny
   - Subscribe to Microsoft Threat Intelligence feed
   
2. **Tune Detection Rules**:
   - Review false positive rates weekly
   - Create exclusions for known-good traffic
   - Enable signature updates auto-deployment

3. **SIEM Integration**:
   - Configure log forwarding to Google Chronicle
   - Create correlation rules for IDS alerts + other indicators
   - Set up 15-minute SLA for critical severity alerts

### Expected Impact
- 40% increase in threat detection coverage
- Reduced mean-time-to-detect (MTTD) for lateral movement`,

    "SEC-NET-0007": `## Remediation Plan for ${controlId}

**Current Status**: Network security simplification not started

### Implementation Steps
1. **Enable Adaptive Network Hardening**:
   - Navigate to Microsoft Defender for Cloud → Recommendations
   - Filter by "Network" category
   - Enable auto-remediation for low-risk rules

2. **Deploy Azure Virtual Network Manager**:
   - Create network groups for workload segmentation
   - Define security admin rules centrally
   - Enable connectivity configurations

3. **Policy-as-Code**:
   - Export current NSG rules to Bicep/ARM templates
   - Implement Azure Policy for NSG compliance
   - Use Azure Firewall Manager for policy consistency

### Tool Leverage
Your current tools can help:
- **Wiz**: Network exposure analysis for prioritization
- **Palo Alto**: Export rules for template creation`
  };
  
  return recommendations[controlId] || `## Remediation Plan for ${controlId}

**Control**: ${control.ControlTitle}
**Current Status**: ${control.Status}

### Analysis
This control requires attention to achieve full compliance. Based on your current tool inventory:

### Recommended Actions
1. Review current tool configurations for gaps
2. Enable relevant policies in Microsoft Defender for Cloud
3. Implement monitoring and alerting for this control area
4. Document evidence collection process

### Available Tools
Your security stack includes tools that can address this control. Review configuration scores and enable missing features.

### Timeline
- Week 1: Assessment and planning
- Week 2-3: Implementation
- Week 4: Validation and documentation`;
}

// Tool capability coverage matrix
export function getToolCapabilityCoverage() {
  return VENDOR_TOOLS.filter(t => t.enabled).map(tool => ({
    ...tool,
    capabilities: tool.capabilities.map(cap => ({
      id: cap,
      name: CAPABILITIES.find(c => c.id === cap)?.name || cap,
      strength: 0.7 + (Math.random() * 0.2) // 0.7-0.9
    }))
  }));
}

