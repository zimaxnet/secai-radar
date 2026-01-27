-- Private Registry tables (Phase 3). From docs/implementation/database-schema.sql §2.3.
-- Run after 001/002/003. Requires workspaces and mcp_servers (from main schema).

-- Workspaces
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id VARCHAR(16) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

CREATE INDEX IF NOT EXISTS idx_workspaces_tenant ON workspaces(tenant_id);

-- Workspace Members
CREATE TABLE IF NOT EXISTS workspace_members (
    member_id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN (
        'RegistryAdmin', 'PolicyApprover', 'EvidenceValidator', 'Viewer', 'AutomationOperator'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user ON workspace_members(user_id);

-- Registry Inventory
CREATE TABLE IF NOT EXISTS registry_inventory (
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

CREATE INDEX IF NOT EXISTS idx_registry_inventory_workspace ON registry_inventory(workspace_id);
CREATE INDEX IF NOT EXISTS idx_registry_inventory_server ON registry_inventory(server_id);

-- Policies
CREATE TABLE IF NOT EXISTS policies (
    policy_id VARCHAR(16) PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    scope_json JSONB NOT NULL,
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('Allow', 'Deny', 'RequireApproval')),
    conditions_json JSONB,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policies_workspace ON policies(workspace_id);
CREATE INDEX IF NOT EXISTS idx_policies_scope ON policies USING GIN(scope_json);
CREATE INDEX IF NOT EXISTS idx_policies_expires ON policies(expires_at);

-- Approvals
CREATE TABLE IF NOT EXISTS approvals (
    approval_id VARCHAR(16) PRIMARY KEY,
    policy_id VARCHAR(16) NOT NULL REFERENCES policies(policy_id) ON DELETE CASCADE,
    approved_by VARCHAR(255) NOT NULL,
    approved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('Approved', 'Denied', 'Deferred')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approvals_policy ON approvals(policy_id);
CREATE INDEX IF NOT EXISTS idx_approvals_approved_by ON approvals(approved_by);

-- Evidence Packs (Private Uploads)
CREATE TABLE IF NOT EXISTS evidence_packs (
    pack_id VARCHAR(16) PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    server_id VARCHAR(16) NOT NULL REFERENCES mcp_servers(server_id) ON DELETE CASCADE,
    blob_ref TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'Validated', 'Rejected')),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    validated_at TIMESTAMPTZ,
    validated_by VARCHAR(255),
    confidence INTEGER CHECK (confidence >= 1 AND confidence <= 3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_packs_workspace ON evidence_packs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_evidence_packs_server ON evidence_packs(server_id);
CREATE INDEX IF NOT EXISTS idx_evidence_packs_status ON evidence_packs(status);

-- Exports (Audit Packs)
CREATE TABLE IF NOT EXISTS exports (
    export_id VARCHAR(16) PRIMARY KEY,
    workspace_id VARCHAR(16) NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'Queued' CHECK (status IN ('Queued', 'Processing', 'Completed', 'Failed')),
    blob_ref TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    request_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exports_workspace ON exports(workspace_id);
CREATE INDEX IF NOT EXISTS idx_exports_status ON exports(status);
CREATE INDEX IF NOT EXISTS idx_exports_requested ON exports(requested_at DESC);
