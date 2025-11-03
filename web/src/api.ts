const API = import.meta.env.VITE_API_BASE || '/api';

const TENANT = import.meta.env.VITE_DEFAULT_TENANT || "NICO";



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

export const getGaps = (tenant=TENANT) => fetch(`${API}/tenant/${tenant}/gaps`).then(r=>r.json());

