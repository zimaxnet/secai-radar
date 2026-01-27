-- SecAI Radar Verified MCP Database Schema
-- Based on Step 5: Reference Implementation Plan
-- PostgreSQL (Azure Database for PostgreSQL Flexible Server)

-- ============================================================================
-- 2.1 Public Core Tables
-- ============================================================================

-- Providers
CREATE TABLE providers (
    provider_id VARCHAR(16) PRIMARY KEY,
    provider_name VARCHAR(255) NOT NULL,
    primary_domain VARCHAR(255) NOT NULL,
    provider_type VARCHAR(50) NOT NULL CHECK (provider_type IN ('Vendor', 'Community', 'Directory', 'Official')),
    contact_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(primary_domain)
);

CREATE INDEX idx_providers_name ON providers(provider_name);
CREATE INDEX idx_providers_type ON providers(provider_type);

-- MCP Servers
CREATE TABLE mcp_servers (
    server_id VARCHAR(16) PRIMARY KEY,
    server_slug VARCHAR(255) NOT NULL UNIQUE,
    server_name VARCHAR(255) NOT NULL,
    provider_id VARCHAR(16) NOT NULL REFERENCES providers(provider_id),
    category_primary VARCHAR(100),
    tags TEXT[], -- Array of tags
    deployment_type VARCHAR(50) NOT NULL CHECK (deployment_type IN ('Remote', 'Local', 'Hybrid', 'Unknown')),
    auth_model VARCHAR(50) NOT NULL CHECK (auth_model IN ('OAuthOIDC', 'APIKey', 'PAT', 'mTLS', 'Unknown')),
    tool_agency VARCHAR(50) NOT NULL CHECK (tool_agency IN ('ReadOnly', 'ReadWrite', 'DestructivePresent', 'Unknown')),
    repo_url TEXT,
    docs_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Deprecated', 'Unknown')),
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mcp_servers_provider ON mcp_servers(provider_id);
CREATE INDEX idx_mcp_servers_slug ON mcp_servers(server_slug);
CREATE INDEX idx_mcp_servers_category ON mcp_servers(category_primary);
CREATE INDEX idx_mcp_servers_status ON mcp_servers(status);
CREATE INDEX idx_mcp_servers_tags ON mcp_servers USING GIN(tags);

-- Server Endpoints
CREATE TABLE server_endpoints (
    endpoint_id SERIAL PRIMARY KEY,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    host VARCHAR(255) NOT NULL,
    scheme VARCHAR(10) NOT NULL DEFAULT 'https',
    path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(server_id, url)
);

CREATE INDEX idx_server_endpoints_server ON server_endpoints(server_id);
CREATE INDEX idx_server_endpoints_host ON server_endpoints(host);

-- Evidence Items
CREATE TABLE evidence_items (
    evidence_id VARCHAR(16) PRIMARY KEY,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('Docs', 'Repo', 'Report', 'Config', 'Logs', 'Attestation')),
    url TEXT, -- public
    blob_ref TEXT, -- private (Azure Storage path)
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confidence INTEGER NOT NULL CHECK (confidence >= 1 AND confidence <= 3),
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for drift detection
    source_url TEXT NOT NULL,
    parser_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_items_server ON evidence_items(server_id);
CREATE INDEX idx_evidence_items_type ON evidence_items(type);
CREATE INDEX idx_evidence_items_confidence ON evidence_items(confidence);
CREATE INDEX idx_evidence_items_hash ON evidence_items(content_hash);

-- Evidence Claims (Extracted Claims)
CREATE TABLE evidence_claims (
    claim_id VARCHAR(16) PRIMARY KEY,
    evidence_id VARCHAR(16) NOT NULL REFERENCES evidence_items(evidence_id) ON DELETE CASCADE,
    claim_type VARCHAR(50) NOT NULL CHECK (claim_type IN (
        'AuthModel', 'TokenTTL', 'Scopes', 'HostingCustody', 'ToolList', 'ToolCapabilities',
        'AuditLogging', 'DataRetention', 'DataDeletion', 'Residency', 'Encryption',
        'SBOM', 'Signing', 'VulnDisclosure', 'IRPolicy'
    )),
    value_json JSONB NOT NULL, -- Flexible value storage
    confidence INTEGER NOT NULL CHECK (confidence >= 1 AND confidence <= 3),
    source_url TEXT NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_claims_evidence ON evidence_claims(evidence_id);
CREATE INDEX idx_evidence_claims_type ON evidence_claims(claim_type);
CREATE INDEX idx_evidence_claims_value ON evidence_claims USING GIN(value_json);

-- Score Snapshots (Append-only)
CREATE TABLE score_snapshots (
    score_id VARCHAR(16) PRIMARY KEY,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    methodology_version VARCHAR(50) NOT NULL,
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Domain subscores (0-5)
    d1 NUMERIC(3,1) NOT NULL CHECK (d1 >= 0 AND d1 <= 5), -- Authentication
    d2 NUMERIC(3,1) NOT NULL CHECK (d2 >= 0 AND d2 <= 5), -- Authorization
    d3 NUMERIC(3,1) NOT NULL CHECK (d3 >= 0 AND d3 <= 5), -- Data Protection
    d4 NUMERIC(3,1) NOT NULL CHECK (d4 >= 0 AND d4 <= 5), -- Audit & Logging
    d5 NUMERIC(3,1) NOT NULL CHECK (d5 >= 0 AND d5 <= 5), -- Operational Security
    d6 NUMERIC(3,1) NOT NULL CHECK (d6 >= 0 AND d6 <= 5), -- Compliance
    trust_score NUMERIC(5,2) NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    tier VARCHAR(1) NOT NULL CHECK (tier IN ('A', 'B', 'C', 'D')),
    enterprise_fit VARCHAR(50) NOT NULL CHECK (enterprise_fit IN ('Regulated', 'Standard', 'Experimental')),
    evidence_confidence INTEGER NOT NULL CHECK (evidence_confidence >= 0 AND evidence_confidence <= 3),
    fail_fast_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    explainability_json JSONB NOT NULL, -- ExplainabilityPayload
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_score_snapshots_server ON score_snapshots(server_id);
CREATE INDEX idx_score_snapshots_assessed ON score_snapshots(assessed_at DESC);
CREATE INDEX idx_score_snapshots_methodology ON score_snapshots(methodology_version);
CREATE INDEX idx_score_snapshots_tier ON score_snapshots(tier);
CREATE INDEX idx_score_snapshots_trust_score ON score_snapshots(trust_score DESC);

-- Drift Events (Append-only)
CREATE TABLE drift_events (
    drift_id VARCHAR(16) PRIMARY KEY,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'ToolsAdded', 'ToolsRemoved', 'AuthChanged', 'ScopeChanged', 'EndpointChanged',
        'DocsChanged', 'EvidenceAdded', 'EvidenceRemoved', 'FlagChanged', 'ScoreChanged'
    )),
    summary TEXT NOT NULL,
    diff_json JSONB, -- Structured diff payload
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_drift_events_server ON drift_events(server_id);
CREATE INDEX idx_drift_events_detected ON drift_events(detected_at DESC);
CREATE INDEX idx_drift_events_severity ON drift_events(severity);
CREATE INDEX idx_drift_events_type ON drift_events(event_type);

-- Daily Briefs
CREATE TABLE daily_briefs (
    date DATE PRIMARY KEY,
    headline VARCHAR(500) NOT NULL,
    narrative_long TEXT NOT NULL,
    narrative_short TEXT NOT NULL CHECK (LENGTH(narrative_short) <= 600),
    highlights JSONB NOT NULL, -- Array of strings
    payload_json JSONB NOT NULL, -- Full DailyBrief object
    methodology_version VARCHAR(50) NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_daily_briefs_generated ON daily_briefs(generated_at DESC);

-- Rubric Versions
CREATE TABLE rubric_versions (
    methodology_version VARCHAR(50) PRIMARY KEY,
    effective_date DATE NOT NULL,
    doc_url TEXT,
    changelog_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 2.2 Public Projections (for speed)
-- ============================================================================

-- Latest Scores (points to latest scoreId per server)
CREATE TABLE latest_scores (
    server_id VARCHAR(16) PRIMARY KEY REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    score_id VARCHAR(16) NOT NULL REFERENCES score_snapshots(score_id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_latest_scores_score ON latest_scores(score_id);

-- Latest Assessments View (Materialized View)
CREATE MATERIALIZED VIEW latest_assessments_view AS
SELECT 
    s.server_id,
    s.server_slug,
    s.server_name,
    s.provider_id,
    p.provider_name,
    s.category_primary,
    s.deployment_type,
    s.auth_model,
    s.tool_agency,
    ss.assessed_at AS last_assessed_at,
    ss.trust_score,
    ss.tier,
    ss.evidence_confidence,
    ss.enterprise_fit,
    ss.fail_fast_flags,
    ss.risk_flags,
    -- Calculate deltas (would need previous score)
    COALESCE(
        (SELECT trust_score FROM score_snapshots 
         WHERE server_id = s.server_id 
         AND assessed_at < ss.assessed_at 
         ORDER BY assessed_at DESC LIMIT 1),
        ss.trust_score
    ) AS previous_trust_score,
    ss.trust_score - COALESCE(
        (SELECT trust_score FROM score_snapshots 
         WHERE server_id = s.server_id 
         AND assessed_at < ss.assessed_at 
         ORDER BY assessed_at DESC LIMIT 1),
        ss.trust_score
    ) AS score_delta_24h,
    (SELECT COUNT(*) FROM drift_events 
     WHERE server_id = s.server_id 
     AND detected_at >= NOW() - INTERVAL '7 days') AS drift_events_7d
FROM mcp_servers s
JOIN providers p ON s.provider_id = p.provider_id
JOIN latest_scores ls ON s.server_id = ls.server_id
JOIN score_snapshots ss ON ls.score_id = ss.score_id;

CREATE INDEX idx_latest_assessments_server ON latest_assessments_view(server_id);
CREATE INDEX idx_latest_assessments_trust_score ON latest_assessments_view(trust_score DESC);
CREATE INDEX idx_latest_assessments_tier ON latest_assessments_view(tier);

-- Rankings Cache
CREATE TABLE rankings_cache (
    cache_id SERIAL PRIMARY KEY,
    "window" VARCHAR(10) NOT NULL, -- '24h', '7d', '30d'
    filters_hash VARCHAR(64) NOT NULL, -- Hash of filter params
    payload_json JSONB NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    UNIQUE("window", filters_hash)
);

CREATE INDEX idx_rankings_cache_expires ON rankings_cache(expires_at);
CREATE INDEX idx_rankings_cache_window ON rankings_cache("window");

-- ============================================================================
-- 2.3 Private Registry (Multi-tenant)
-- ============================================================================

-- Workspaces
CREATE TABLE workspaces (
    workspace_id VARCHAR(16) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL, -- Entra tenant ID
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_workspaces_tenant ON workspaces(tenant_id);

-- Workspace Members
CREATE TABLE workspace_members (
    member_id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL, -- Entra user ID (subject)
    role VARCHAR(50) NOT NULL CHECK (role IN (
        'RegistryAdmin', 'PolicyApprover', 'EvidenceValidator', 'Viewer', 'AutomationOperator'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);

-- Registry Inventory
CREATE TABLE registry_inventory (
    inventory_id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    owner VARCHAR(255),
    purpose TEXT,
    environment VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Deprecated', 'Removed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, server_id)
);

CREATE INDEX idx_registry_inventory_workspace ON registry_inventory(workspace_id);
CREATE INDEX idx_registry_inventory_server ON registry_inventory(server_id);

-- Policies
CREATE TABLE policies (
    policy_id VARCHAR(16) PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    scope_json JSONB NOT NULL, -- {type: 'server'|'tool'|'category', value: string}
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('Allow', 'Deny', 'RequireApproval')),
    conditions_json JSONB, -- {env, dataClass, toolAgency, evidenceConfidence}
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_policies_workspace ON policies(workspace_id);
CREATE INDEX idx_policies_scope ON policies USING GIN(scope_json);
CREATE INDEX idx_policies_expires ON policies(expires_at);

-- Approvals
CREATE TABLE approvals (
    approval_id VARCHAR(16) PRIMARY KEY,
    policy_id VARCHAR(16) NOT NULL REFERENCES policies(policy_id) ON DELETE CASCADE,
    approved_by VARCHAR(255) NOT NULL, -- User ID
    approved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('Approved', 'Denied', 'Deferred')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_approvals_policy ON approvals(policy_id);
CREATE INDEX idx_approvals_approved_by ON approvals(approved_by);

-- Evidence Packs (Private Uploads)
CREATE TABLE evidence_packs (
    pack_id VARCHAR(16) PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    blob_ref TEXT NOT NULL, -- Azure Storage path
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'Validated', 'Rejected')),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    validated_at TIMESTAMPTZ,
    validated_by VARCHAR(255),
    confidence INTEGER CHECK (confidence >= 1 AND confidence <= 3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_packs_workspace ON evidence_packs(workspace_id);
CREATE INDEX idx_evidence_packs_server ON evidence_packs(server_id);
CREATE INDEX idx_evidence_packs_status ON evidence_packs(status);

-- Exports (Audit Packs)
CREATE TABLE exports (
    export_id VARCHAR(16) PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'Queued' CHECK (status IN ('Queued', 'Processing', 'Completed', 'Failed')),
    blob_ref TEXT, -- Azure Storage path to export file
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    request_json JSONB NOT NULL, -- Original request params
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_exports_workspace ON exports(workspace_id);
CREATE INDEX idx_exports_status ON exports(status);
CREATE INDEX idx_exports_requested ON exports(requested_at DESC);

-- Outbox Items (Distribution Drafts)
CREATE TABLE outbox_items (
    outbox_id VARCHAR(16) PRIMARY KEY,
    date DATE NOT NULL,
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('x', 'linkedin', 'reddit', 'hn', 'mastodon', 'bluesky')),
    content TEXT NOT NULL,
    media_urls JSONB, -- Array of image URLs
    links JSONB NOT NULL, -- Array of links
    status VARCHAR(50) NOT NULL DEFAULT 'Queued' CHECK (status IN ('Queued', 'Sent', 'Failed')),
    scheduled_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outbox_items_date ON outbox_items(date DESC);
CREATE INDEX idx_outbox_items_channel ON outbox_items(channel);
CREATE INDEX idx_outbox_items_status ON outbox_items(status);

-- ============================================================================
-- Graph Snapshots (MVP: JSON in Postgres)
-- ============================================================================

CREATE TABLE server_graph_snapshots (
    snapshot_id VARCHAR(16) PRIMARY KEY,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    assessed_at TIMESTAMPTZ NOT NULL,
    graph_json JSONB NOT NULL, -- {nodes: [], edges: []}
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_graph_snapshots_server ON server_graph_snapshots(server_id);
CREATE INDEX idx_graph_snapshots_assessed ON server_graph_snapshots(assessed_at DESC);

-- ============================================================================
-- Pipeline Run Logs
-- ============================================================================

CREATE TABLE pipeline_runs (
    run_id VARCHAR(50) PRIMARY KEY, -- YYYY-MM-DD + source version hashes
    date DATE NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'Running' CHECK (status IN ('Running', 'Completed', 'Failed', 'Partial')),
    stages_json JSONB NOT NULL, -- Array of stage statuses
    deliverables_json JSONB NOT NULL, -- {rankingsUpdated: bool, ...}
    errors_json JSONB, -- Array of error messages
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pipeline_runs_date ON pipeline_runs(date DESC);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);
