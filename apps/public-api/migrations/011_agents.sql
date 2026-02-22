-- Add agents tables to parallel MCP tables

-- Agents
CREATE TABLE IF NOT EXISTS agents (
    agent_id VARCHAR(16) PRIMARY KEY,
    agent_slug VARCHAR(255) NOT NULL UNIQUE,
    agent_name VARCHAR(255) NOT NULL,
    provider_id VARCHAR(16) NOT NULL REFERENCES providers(provider_id),
    category_primary VARCHAR(100),
    tags TEXT[],
    agent_type VARCHAR(50) NOT NULL,
    repo_url TEXT,
    docs_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    metadata_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agents_provider ON agents(provider_id);
CREATE INDEX IF NOT EXISTS idx_agents_slug ON agents(agent_slug);
CREATE INDEX IF NOT EXISTS idx_agents_category ON agents(category_primary);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);


-- Agent Evidence Items
CREATE TABLE IF NOT EXISTS agent_evidence_items (
    evidence_id VARCHAR(16) PRIMARY KEY,
    agent_id VARCHAR(16) NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    evidence_class VARCHAR(1) DEFAULT 'C',
    url TEXT,
    blob_ref TEXT,
    captured_at TIMESTAMPTZ NOT NULL,
    confidence INTEGER NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    source_url TEXT NOT NULL,
    parser_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_evidence_server ON agent_evidence_items(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_evidence_type ON agent_evidence_items(type);
CREATE INDEX IF NOT EXISTS idx_agent_evidence_hash ON agent_evidence_items(content_hash);


-- Agent Evidence Claims
CREATE TABLE IF NOT EXISTS agent_evidence_claims (
    claim_id VARCHAR(16) PRIMARY KEY,
    evidence_id VARCHAR(16) NOT NULL REFERENCES agent_evidence_items(evidence_id) ON DELETE CASCADE,
    claim_type VARCHAR(50) NOT NULL,
    value_json JSONB NOT NULL,
    confidence INTEGER NOT NULL,
    source_url TEXT NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_claims_evidence ON agent_evidence_claims(evidence_id);
CREATE INDEX IF NOT EXISTS idx_agent_claims_type ON agent_evidence_claims(claim_type);
CREATE INDEX IF NOT EXISTS idx_agent_claims_json ON agent_evidence_claims USING GIN(value_json);


-- Agent Score Snapshots
CREATE TABLE IF NOT EXISTS agent_score_snapshots (
    score_id VARCHAR(16) PRIMARY KEY,
    agent_id VARCHAR(16) NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    methodology_version VARCHAR(50) NOT NULL,
    assessed_at TIMESTAMPTZ NOT NULL,
    d1 NUMERIC(3,1) NOT NULL,
    d2 NUMERIC(3,1) NOT NULL,
    d3 NUMERIC(3,1) NOT NULL,
    d4 NUMERIC(3,1) NOT NULL,
    d5 NUMERIC(3,1) NOT NULL,
    d6 NUMERIC(3,1) NOT NULL,
    trust_score NUMERIC(5,2) NOT NULL,
    tier VARCHAR(1) NOT NULL,
    enterprise_fit VARCHAR(50) NOT NULL,
    evidence_confidence INTEGER NOT NULL,
    fail_fast_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    explainability_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_score_server ON agent_score_snapshots(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_score_assessed ON agent_score_snapshots(assessed_at DESC);


-- Agent Latest Scores
CREATE TABLE IF NOT EXISTS agent_latest_scores (
    agent_id VARCHAR(16) PRIMARY KEY REFERENCES agents(agent_id) ON DELETE CASCADE,
    score_id VARCHAR(16) NOT NULL REFERENCES agent_score_snapshots(score_id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_latest_score ON agent_latest_scores(score_id);
