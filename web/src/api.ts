/**
 * SecAI Radar API Client
 * Handles all API calls with automatic fallback to demo data when backend is unavailable
 */

import {
  getDemoSummaryByDomain,
  getDemoGaps,
  getDemoReport,
  getDemoAIRecommendation,
  DEMO_CONTROLS,
  VENDOR_TOOLS,
  DOMAINS,
  getToolCapabilityCoverage
} from './demoData';

const API = import.meta.env.VITE_API_BASE || '/api';
const TENANT = import.meta.env.VITE_DEFAULT_TENANT || "CONTOSO";

// Flag to track if we're in demo mode (API unavailable)
let _demoMode = false;

// Check if response is valid JSON
async function safeJsonParse(response: Response): Promise<any> {
  const text = await response.text();
  try {
    // Check if response looks like HTML (API returning error page)
    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
      console.warn('API returned HTML instead of JSON, switching to demo mode');
      _demoMode = true;
      return null;
    }
    return JSON.parse(text);
  } catch (e) {
    console.warn('Failed to parse API response as JSON:', e);
    _demoMode = true;
    return null;
  }
}

// Fetch with demo fallback
async function fetchWithFallback<T>(
  url: string,
  options: RequestInit | undefined,
  fallbackFn: () => T
): Promise<T> {
  // If already in demo mode, skip API call
  if (_demoMode) {
    return fallbackFn();
  }

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      console.warn(`API request failed: ${response.status}`);
      _demoMode = true;
      return fallbackFn();
    }

    const data = await safeJsonParse(response);
    if (data === null) {
      return fallbackFn();
    }
    return data;
  } catch (e) {
    console.warn('API request error, using demo data:', e);
    _demoMode = true;
    return fallbackFn();
  }
}

// Check if we're in demo mode
export function isDemoMode(): boolean {
  return _demoMode;
}

// Force demo mode (for testing)
export function setDemoMode(enabled: boolean): void {
  _demoMode = enabled;
}

// Domains
export const getDomains = () => fetchWithFallback(
  `${API}/domains`,
  undefined,
  () => ({ domains: DOMAINS })
);

// Summary
export const getSummary = (tenant = TENANT) => fetchWithFallback(
  `${API}/tenant/${tenant}/summary`,
  undefined,
  () => ({ byDomain: getDemoSummaryByDomain() })
);

// Controls
export const getControls = (tenant = TENANT, p: { domain?: string; status?: string; q?: string } = {}) => {
  const qs = new URLSearchParams(p as Record<string, string>).toString();

  return fetchWithFallback(
    `${API}/tenant/${tenant}/controls${qs ? `?${qs}` : ""}`,
    undefined,
    () => {
      let items = [...DEMO_CONTROLS];

      if (p.domain) {
        items = items.filter(c => c.DomainCode === p.domain);
      }
      if (p.status) {
        items = items.filter(c => c.Status === p.status);
      }
      if (p.q) {
        const query = p.q.toLowerCase();
        items = items.filter(c =>
          c.ControlID.toLowerCase().includes(query) ||
          c.ControlTitle.toLowerCase().includes(query)
        );
      }

      return { items, total: items.length };
    }
  );
};

// Post Tools
export const postTools = (tenant = TENANT, body: any) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/tools`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    },
    () => ({ ok: true, message: "Demo mode: Tool configuration saved" })
  );

// Get Tools Inventory
export const getToolsInventory = (tenant = TENANT) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/tools`,
    undefined,
    () => ({
      tools: VENDOR_TOOLS,
      coverage: getToolCapabilityCoverage()
    })
  );

// Import Controls
export const importControls = (tenant = TENANT, csv: string) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/import`,
    {
      method: "POST",
      headers: { "Content-Type": "text/csv" },
      body: csv
    },
    () => ({ ok: true, imported: 0, message: "Demo mode: Import simulated" })
  );

// Gaps
export const getGaps = (tenant = TENANT, includeAI = false) => {
  const url = `${API}/tenant/${tenant}/gaps${includeAI ? '?ai=true' : ''}`;
  return fetchWithFallback(
    url,
    undefined,
    () => ({ items: getDemoGaps(), aiEnabled: includeAI })
  );
};

// AI Recommendation
export const getAIRecommendation = (tenant = TENANT, controlId: string) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/ai/recommendations?controlId=${controlId}`,
    undefined,
    () => ({
      recommendation: getDemoAIRecommendation(controlId),
      controlId,
      aiEnabled: true
    })
  );

// AI Gap Explanation
export const getAIGapExplanation = (tenant = TENANT, controlId: string, capabilityId: string, gapType: 'hard' | 'soft' = 'hard') =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/ai/recommendations?controlId=${controlId}&capabilityId=${capabilityId}&gapType=${gapType}`,
    undefined,
    () => ({
      explanation: `This ${gapType} gap for capability "${capabilityId}" means the control ${controlId} ${gapType === 'hard' ? 'is missing a required capability' : 'has insufficient configuration'}. Review your tool configurations and consider enabling additional features or deploying complementary tools.`,
      aiEnabled: true
    })
  );

// AI Usage Summary
export const getAIUsageSummary = (tenant = TENANT) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/ai/usage`,
    undefined,
    () => ({
      totalTokens: 15420,
      totalCalls: 47,
      lastRun: new Date().toISOString(),
      estimatedCost: "$0.32"
    })
  );

// AI Help
export const getAIHelp = (tenant = TENANT, question: string, context: Record<string, any>) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/ai/help`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context })
    },
    () => ({
      answer: `Based on your question about "${question}", I recommend reviewing the relevant security controls and tool configurations. In demo mode, I can provide general guidance. For specific AI-powered analysis, ensure the backend API is connected.`,
      aiEnabled: true
    })
  );

// Realtime Session
export const createRealtimeSession = async (sdpOffer: string, options?: { deployment?: string }) => {
  const response = await fetch(`${API}/realtime/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sdpOffer, deployment: options?.deployment })
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(text || response.statusText);
  }
  return text;
};

// Control by ID
export const getControl = (tenant = TENANT, controlId: string) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/controls?q=${controlId}`,
    undefined,
    () => {
      const control = DEMO_CONTROLS.find(c => c.ControlID === controlId);
      return control || null;
    }
  );

// Evidence
export const getEvidence = (tenant = TENANT, controlId: string) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/evidence/${controlId}`,
    undefined,
    () => ({
      items: [
        { id: "ev-001", controlId, fileName: "network_topology.png", type: "screenshot", uploadedAt: "2024-11-15T10:30:00Z", description: "Network architecture diagram" },
        { id: "ev-002", controlId, fileName: "nsg_rules_export.json", type: "config_export", uploadedAt: "2024-11-14T09:15:00Z", description: "NSG configuration export" },
        { id: "ev-003", controlId, fileName: "firewall_logs.csv", type: "log", uploadedAt: "2024-11-13T14:20:00Z", description: "Azure Firewall logs sample" }
      ]
    })
  );

// Upload Evidence
export const uploadEvidence = (tenant = TENANT, controlId: string, file: File, description?: string) => {
  return new Promise((resolve, reject) => {
    if (_demoMode) {
      // Simulate upload in demo mode
      setTimeout(() => {
        resolve({
          ok: true,
          message: "Demo mode: Evidence upload simulated",
          evidence: {
            id: `ev-demo-${Date.now()}`,
            controlId,
            fileName: file.name,
            type: "upload",
            uploadedAt: new Date().toISOString(),
            description: description || ""
          }
        });
      }, 1000);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1];
      fetch(`${API}/tenant/${tenant}/evidence/${controlId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file: base64,
          fileName: file.name,
          description: description || ''
        })
      })
        .then(r => r.json())
        .then(resolve)
        .catch(reject);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// Controls by Domain
export const getControlsByDomain = (tenant = TENANT, domain: string) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/controls?domain=${domain}`,
    undefined,
    () => ({
      items: DEMO_CONTROLS.filter(c => c.DomainCode === domain),
      total: DEMO_CONTROLS.filter(c => c.DomainCode === domain).length
    })
  );

// Update Control
export const updateControl = (tenant = TENANT, controlId: string, updates: any) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/controls/${controlId}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    },
    () => ({
      ok: true,
      message: "Demo mode: Control update simulated",
      control: { ...DEMO_CONTROLS.find(c => c.ControlID === controlId), ...updates }
    })
  );

// Report Generation
export const getReport = (tenant = TENANT, includeAI = true) =>
  fetchWithFallback(
    `${API}/tenant/${tenant}/report?includeAI=${includeAI}`,
    undefined,
    () => getDemoReport(tenant)
  );

// Agent Registry API
export const getAgents = (filters?: { status?: string; collection?: string; blueprint?: string; capability?: string }) => {
  const qs = new URLSearchParams(filters as Record<string, string>).toString();
  return fetchWithFallback(
    `${API}/registry/agents${qs ? `?${qs}` : ''}`,
    undefined,
    () => ({
      agents: [
        { agent_id: "secops-analyst", entra_agent_id: "sa-001", name: "SecOps Analyst", role: "Security Operations Analyst", status: "active", collections: ["security-monitoring"], capabilities: ["threat-detection", "incident-triage"], last_active_at: new Date().toISOString(), blueprint: "security-analyst" },
        { agent_id: "compliance-auditor", entra_agent_id: "ca-001", name: "Compliance Auditor", role: "Compliance Specialist", status: "active", collections: ["compliance"], capabilities: ["policy-validation", "evidence-review"], last_active_at: new Date().toISOString(), blueprint: "compliance-checker" },
        { agent_id: "vuln-scanner", entra_agent_id: "vs-001", name: "Vulnerability Scanner", role: "Security Scanner", status: "active", collections: ["scanning"], capabilities: ["vuln-assessment", "risk-scoring"], last_active_at: new Date().toISOString(), blueprint: "scanner" },
        { agent_id: "threat-hunter", entra_agent_id: "th-001", name: "Threat Hunter", role: "Threat Intelligence Analyst", status: "standby", collections: ["threat-intel"], capabilities: ["threat-hunting", "ioc-detection"], last_active_at: new Date(Date.now() - 3600000).toISOString(), blueprint: "threat-hunter" }
      ]
    })
  );
};

export const getAgent = (agentId: string) =>
  fetchWithFallback(
    `${API}/registry/agents/${agentId}`,
    undefined,
    () => ({
      agent_id: agentId,
      entra_agent_id: `${agentId}-001`,
      name: agentId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      role: "Security Agent",
      status: "active",
      collections: ["default"],
      capabilities: ["analysis", "reporting"],
      last_active_at: new Date().toISOString(),
      blueprint: "security-agent",
      metrics: {
        tasksCompleted: 147,
        avgResponseTime: "2.3s",
        successRate: 0.94
      }
    })
  );

export const updateAgentStatus = (agentId: string, status: string) =>
  fetchWithFallback(
    `${API}/registry/agents/${agentId}/status`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    },
    () => ({ ok: true, agentId, status })
  );

export const quarantineAgent = (agentId: string) =>
  fetchWithFallback(
    `${API}/registry/agents/${agentId}/quarantine`,
    { method: 'POST' },
    () => ({ ok: true, agentId, quarantined: true })
  );

export const unquarantineAgent = (agentId: string) =>
  fetchWithFallback(
    `${API}/registry/agents/${agentId}/quarantine`,
    { method: 'DELETE' },
    () => ({ ok: true, agentId, quarantined: false })
  );

// Agent Observability API
export const getAgentObservability = (agentId?: string, timeRange?: string) => {
  const params = new URLSearchParams();
  if (agentId) params.append('agent_id', agentId);
  if (timeRange) params.append('time_range', timeRange);

  return fetchWithFallback(
    `${API}/observability/metrics?${params}`,
    undefined,
    () => ({
      metrics: {
        totalRequests: 1247,
        avgLatency: 234,
        errorRate: 0.023,
        tokensUsed: 45820,
        activeAgents: 4
      },
      timeSeries: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        requests: Math.floor(40 + Math.random() * 60),
        latency: Math.floor(150 + Math.random() * 150),
        errors: Math.floor(Math.random() * 3)
      }))
    })
  );
};

// Agent Evaluations API
export const runEvaluation = (body: {
  agent_id: string;
  response: string;
  context?: string;
  task_instruction?: string;
  query?: string;
  tool_calls?: any[];
}) =>
  fetchWithFallback(
    `${API}/evaluations/evaluate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    },
    () => ({
      evaluation: {
        overall_score: 0.85,
        dimensions: {
          accuracy: 0.88,
          relevance: 0.92,
          safety: 1.0,
          helpfulness: 0.78
        },
        feedback: "Response demonstrates good understanding of security concepts with accurate recommendations."
      }
    })
  );

// Agent-Crafted Visualization Prompt (Elena Bridges - Business Impact Strategist)
export const craftVisualizationPrompt = async (
  intent: string,
  options?: {
    style?: 'diagram' | 'infographic' | 'chart' | 'architecture';
    contextType?: 'assessment' | 'gaps' | 'tools' | 'custom';
    assessmentData?: any;
  }
): Promise<{
  crafted_prompt: string;
  agent: string;
  agent_role: string;
  style: string;
  context_type: string;
  original_intent: string;
} | null> => {
  // In demo mode, use a fallback prompt crafter
  if (_demoMode) {
    const styleGuides: Record<string, string> = {
      diagram: 'Create a clear, professional technical diagram with labeled components, connecting lines, and a clean white or light gray background.',
      infographic: 'Create a modern infographic with icons, statistics, and visual hierarchy. Use a professional color palette.',
      chart: 'Create a clean data visualization chart suitable for executive presentations.',
      architecture: 'Create a system architecture diagram showing components, connections, and data flow.'
    };

    const style = options?.style || 'diagram';
    const contextData = options?.assessmentData;

    // Build context-aware prompt
    let contextEnhancement = '';
    if (contextData) {
      const summary = contextData.summary || {};
      const totalControls = summary.totalControls || 0;
      const totalGaps = summary.totalGaps || 0;
      const complianceRate = totalControls > 0 ? ((totalControls - totalGaps) / totalControls * 100).toFixed(0) : 0;

      contextEnhancement = `\n\nKey Metrics to Include:
- Compliance Rate: ${complianceRate}%
- Total Controls: ${totalControls}
- Controls with Gaps: ${totalGaps}
- Critical Gaps: ${summary.criticalGaps || 0}`;
    }

    const craftedPrompt = `${styleGuides[style]}

Executive Visualization Request: ${intent}
${contextEnhancement}

Create a professional, corporate-ready visualization that:
- Uses a sophisticated color palette (deep blues, teals, and accent colors)
- Includes clear labels and annotations
- Has logical visual hierarchy
- Is suitable for board-level presentations
- Emphasizes business impact and risk context`;

    return {
      crafted_prompt: craftedPrompt,
      agent: 'elena_bridges',
      agent_role: 'Business Impact Strategist',
      style: style,
      context_type: options?.contextType || 'assessment',
      original_intent: intent
    };
  }

  try {
    const response = await fetch(`${API}/visualization/prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        intent,
        style: options?.style || 'diagram',
        contextType: options?.contextType || 'assessment',
        assessmentData: options?.assessmentData
      })
    });

    if (!response.ok) {
      console.warn('Agent prompt crafting failed, using fallback');
      return null;
    }

    return await response.json();
  } catch (error) {
    console.warn('Error calling visualization prompt agent:', error);
    return null;
  }
};

// Nano Banana Pro Image Generation (Gemini API)
export const generateVisualization = async (
  prompt: string,
  options?: {
    style?: 'diagram' | 'infographic' | 'chart' | 'architecture';
    aspectRatio?: '1:1' | '16:9' | '4:3';
  }
) => {
  const apiKey = import.meta.env.VITE_GOOGLE_API_KEY;

  if (!apiKey) {
    console.warn('VITE_GOOGLE_API_KEY not configured for Nano Banana Pro');
    return {
      success: false,
      error: 'API key not configured. Set VITE_GOOGLE_API_KEY in your environment.',
      promptUsed: prompt
    };
  }

  const enhancedPrompt = buildVisualizationPrompt(prompt, options);

  try {
    // Gemini 2.0 Flash image generation endpoint
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [{ text: enhancedPrompt }]
          }],
          generationConfig: {
            responseModalities: ["image", "text"],
            responseMimeType: "image/png"
          }
        })
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Gemini API error: ${error}`);
    }

    const data = await response.json();

    // Extract image from response
    const imagePart = data.candidates?.[0]?.content?.parts?.find(
      (p: any) => p.inlineData?.mimeType?.startsWith('image/')
    );

    if (imagePart?.inlineData) {
      return {
        success: true,
        imageData: imagePart.inlineData.data,
        mimeType: imagePart.inlineData.mimeType,
        promptUsed: enhancedPrompt
      };
    }

    // If no image, return text description
    const textPart = data.candidates?.[0]?.content?.parts?.find((p: any) => p.text);
    return {
      success: false,
      textResponse: textPart?.text || 'No image generated',
      promptUsed: enhancedPrompt
    };

  } catch (error: any) {
    console.error('Nano Banana Pro generation failed:', error);
    return {
      success: false,
      error: error.message,
      promptUsed: enhancedPrompt
    };
  }
};

// Build enhanced prompt for visualization
function buildVisualizationPrompt(
  basePrompt: string,
  options?: { style?: string; aspectRatio?: string }
): string {
  const styleGuides: Record<string, string> = {
    diagram: 'Create a clear, professional technical diagram with labeled components, connecting lines, and a clean white or light gray background. Use a consistent color scheme with blues and grays.',
    infographic: 'Create a modern infographic with icons, statistics, and visual hierarchy. Use a professional color palette with accent colors for emphasis. Include relevant icons and visual metaphors.',
    chart: 'Create a clean data visualization chart suitable for executive presentations. Use professional colors, clear labels, and appropriate chart type for the data.',
    architecture: 'Create a system architecture diagram showing components, connections, and data flow. Use standard architecture diagram conventions with clear labeling and a logical layout.'
  };

  const style = options?.style || 'diagram';
  const styleGuide = styleGuides[style] || styleGuides.diagram;

  return `${styleGuide}

Intent: ${basePrompt}

Requirements:
- Professional, corporate-ready visual
- Clear text labels that are readable
- Logical visual hierarchy
- Modern, clean aesthetic
- No placeholder or dummy text - use actual labels
- High contrast for readability
${options?.aspectRatio ? `- Aspect ratio: ${options.aspectRatio}` : '- Standard aspect ratio'}

Generate the visualization now.`;
}

// Export visualization prompt builder for external use
export const buildNanoBananaPrompt = buildVisualizationPrompt;

// --- WebAuthn API ---

export const getRegistrationOptions = async (username: string, displayName: string) => {
  const response = await fetch(`${API}/auth/register/options`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, displayName })
  });
  if (!response.ok) throw new Error('Failed to get registration options');
  return response.json();
};

export const verifyRegistration = async (username: string, attResp: any) => {
  const response = await fetch(`${API}/auth/register/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, response: attResp })
  });
  if (!response.ok) throw new Error('Registration verification failed');
  return response.json();
};

export const getLoginOptions = async (username: string) => {
  const response = await fetch(`${API}/auth/login/options`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Failed to get login options');
  }
  return response.json();
};

export const verifyLogin = async (username: string, asseResp: any) => {
  const response = await fetch(`${API}/auth/login/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, response: asseResp })
  });
  if (!response.ok) throw new Error('Login verification failed');
  return response.json();
};
