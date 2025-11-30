const API = import.meta.env.VITE_API_BASE || '/api';

const TENANT = import.meta.env.VITE_DEFAULT_TENANT || "CONTOSO";



export const getDomains = () => fetch(`${API}/domains`).then(r=>r.json());

export const getSummary = (tenant=TENANT) => fetch(`${API}/tenant/${tenant}/summary`).then(r=>r.json());

export const getControls = (tenant=TENANT, p: {domain?:string;status?:string;q?:string} = {}) => {

  const qs = new URLSearchParams(p as any).toString();

  return fetch(`${API}/tenant/${tenant}/controls${qs?`?${qs}`:""}`).then(r=>r.json());

};

export const postTools = (tenant=TENANT, body:any) =>

  fetch(`${API}/tenant/${tenant}/tools`, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)}).then(r=>r.json());

export const importControls = (tenant=TENANT, csv:string) =>

  fetch(`${API}/tenant/${tenant}/import`, { method:"POST", headers:{"Content-Type":"text/csv"}, body: csv }).then(r=>r.json());

export const getGaps = (tenant=TENANT, includeAI = false) => {
  const url = `${API}/tenant/${tenant}/gaps${includeAI ? '?ai=true' : ''}`;
  return fetch(url).then(r=>r.json());
};

export const getAIRecommendation = (tenant=TENANT, controlId: string) => 
  fetch(`${API}/tenant/${tenant}/ai/recommendations?controlId=${controlId}`).then(r=>r.json());

export const getAIGapExplanation = (tenant=TENANT, controlId: string, capabilityId: string, gapType: 'hard' | 'soft' = 'hard') => 
  fetch(`${API}/tenant/${tenant}/ai/recommendations?controlId=${controlId}&capabilityId=${capabilityId}&gapType=${gapType}`).then(r=>r.json());

export const getAIUsageSummary = (tenant=TENANT) =>
  fetch(`${API}/tenant/${tenant}/ai/usage`).then(r => r.json());

export const getAIHelp = (tenant=TENANT, question: string, context: Record<string, any>) =>
  fetch(`${API}/tenant/${tenant}/ai/help`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, context })
  }).then(r => r.json());

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

export const getControl = (tenant=TENANT, controlId: string) => 
  fetch(`${API}/tenant/${tenant}/controls?q=${controlId}`).then(r=>r.json()).then(d => d.items?.[0]);

export const getEvidence = (tenant=TENANT, controlId: string) => 
  fetch(`${API}/tenant/${tenant}/evidence/${controlId}`).then(r=>r.json());

export const uploadEvidence = (tenant=TENANT, controlId: string, file: File, description?: string) => {
  return new Promise((resolve, reject) => {
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

export const getControlsByDomain = (tenant=TENANT, domain: string) => 
  fetch(`${API}/tenant/${tenant}/controls?domain=${domain}`).then(r=>r.json());

export const updateControl = (tenant=TENANT, controlId: string, updates: any) =>
  fetch(`${API}/tenant/${tenant}/controls/${controlId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  }).then(r=>r.json());

// Agent Registry API
export const getAgents = (filters?: { status?: string; collection?: string; blueprint?: string; capability?: string }) => {
  const qs = new URLSearchParams(filters as any).toString();
  return fetch(`${API}/registry/agents${qs ? `?${qs}` : ''}`).then(r => r.json());
};

export const getAgent = (agentId: string) =>
  fetch(`${API}/registry/agents/${agentId}`).then(r => r.json());

export const updateAgentStatus = (agentId: string, status: string) =>
  fetch(`${API}/registry/agents/${agentId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  }).then(r => r.json());

export const quarantineAgent = (agentId: string) =>
  fetch(`${API}/registry/agents/${agentId}/quarantine`, {
    method: 'POST'
  }).then(r => r.json());

export const unquarantineAgent = (agentId: string) =>
  fetch(`${API}/registry/agents/${agentId}/quarantine`, {
    method: 'DELETE'
  }).then(r => r.json());

// Agent Observability API
export const getAgentObservability = (agentId?: string, timeRange?: string) => {
  const params = new URLSearchParams();
  if (agentId) params.append('agent_id', agentId);
  if (timeRange) params.append('time_range', timeRange);
  return fetch(`${API}/observability/metrics?${params}`).then(r => r.json());
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
  fetch(`${API}/evaluations/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }).then(r => r.json());

