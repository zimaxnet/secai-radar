# SecAI Radar Verified MCP - Security Model

**Based on:** Step 5 Reference Implementation Plan  
**Scope:** Multi-tenant RBAC, public/private separation

## Public API Security

### Authentication
- **No authentication required** - Public endpoints are read-only
- All endpoints are publicly accessible

### Rate Limiting
- Implement rate limiting at API gateway/edge level
- Recommended limits:
  - General endpoints: 100 requests/minute per IP
  - Search/rankings: 50 requests/minute per IP
  - Feeds: 10 requests/minute per IP

### Caching
- All public endpoints support ETag and Cache-Control headers
- Rankings cache: 5 minutes (max-age=300)
- Methodology: 1 hour (max-age=3600)
- Server detail: 5 minutes (max-age=300)

### WAF (Web Application Firewall)
- Deploy Azure Front Door with WAF
- Rules:
  - SQL injection protection
  - XSS protection
  - Rate limiting
  - Geographic restrictions (if needed)

### Data Redaction
- **Public redaction policy enforced in API layer**
- Never expose:
  - Private evidence artifacts (blobRef)
  - Workspace-specific data
  - Internal metadata
  - Raw internal artifacts

### Content Security
- All public responses include:
  - `X-Methodology-Version` header
  - `X-Generated-At` header
  - "Not a certification" disclaimer in responses
  - Evidence Confidence labels

## Private Registry API Security

### Authentication
- **OIDC (Entra ID) JWT validation**
- All requests require valid JWT bearer token
- Token validation:
  - Signature verification
  - Expiration check
  - Audience validation
  - Issuer validation

### Authorization (RBAC)

#### Roles
1. **RegistryAdmin**
   - Manage workspace settings
   - Manage workspace members
   - Create/edit/delete policies
   - Full access to all workspace resources

2. **PolicyApprover**
   - Approve/deny policies
   - View all policies
   - View inventory
   - Cannot modify workspace settings

3. **EvidenceValidator**
   - Validate evidence packs
   - Upload evidence packs
   - View evidence packs
   - Cannot approve policies

4. **Viewer**
   - Read-only access to:
     - Inventory
     - Policies
     - Evidence packs (metadata only)
     - Exports (status only)
   - Cannot modify anything

5. **AutomationOperator**
   - Trigger agent runs
   - View run logs
   - Configure schedules
   - Cannot modify workspace data

### Workspace Isolation

#### Row-Level Security (RLS)
- Every table keyed by `workspaceId`
- Enforce workspace isolation:
  ```sql
  -- Example RLS policy
  CREATE POLICY workspace_isolation ON registry_inventory
    FOR ALL
    USING (workspace_id = current_setting('app.current_workspace_id')::VARCHAR);
  ```

#### API-Level Enforcement
- Extract `workspaceId` from JWT claims or request context
- Validate user has access to workspace
- Filter all queries by `workspaceId`
- Never return data from other workspaces

### Audit Logging

#### What to Log
- Every policy change (create, update, delete)
- Every approval action (approve, deny, defer)
- Evidence pack access (upload, view, validate)
- Export generation
- Agent run triggers
- Workspace membership changes

#### Log Format
```json
{
  "timestamp": "2026-01-23T10:30:00Z",
  "workspaceId": "ws_123",
  "userId": "user_456",
  "action": "policy.approved",
  "resourceId": "policy_789",
  "metadata": {
    "policyId": "policy_789",
    "decision": "approved",
    "notes": "Complies with security policy"
  }
}
```

#### Storage
- Store audit logs in separate table: `audit_logs`
- Append-only (never delete)
- Retention: 7 years (compliance requirement)
- Encrypted at rest

## Service-to-Service Authentication

### Managed Identities
- All Azure services use **Managed Identities**
- No shared secrets or connection strings
- Automatic token rotation
- Least privilege access

### Key Vault Integration
- Store secrets in Azure Key Vault:
  - Database credentials (if not using MI)
  - External API keys
  - Signing keys for tokens
  - Entra ID app registration secrets

### Access Patterns
```
Container App (Managed Identity)
  → Key Vault (Get Secret)
  → PostgreSQL (Managed Identity or Secret)
  → Storage Account (Managed Identity)
```

## Data Protection

### Encryption
- **Encryption at rest**: Enabled by default (Azure Storage, PostgreSQL)
- **Encryption in transit**: TLS 1.2+ for all connections
- Database connections: SSL required

### Storage Isolation
- **Separate containers** for public vs private:
  - `evidence-private` - Private evidence packs (no public access)
  - `public-assets` - Public images/assets (blob access)
  - `exports-private` - Audit pack exports (no public access)

### Export Security
- Export artifacts are **time-limited signed URLs**
- URLs expire after 24 hours
- URLs are single-use (tracked in database)
- Access logged for audit

### PII Minimization
- **Do not store user PII** beyond required identity claims
- Store only:
  - User ID (subject from JWT)
  - Email (if required for notifications)
  - Role assignments
- Never store:
  - Full names
  - Phone numbers
  - Addresses
  - Other PII

## Network Security

### Public Endpoints
- Public web/API accessible via:
  - `secairadar.cloud` → Front Door → Container Apps
  - Direct Container App endpoints (for development)

### Private Endpoints
- Database: Private endpoint (recommended for production)
- Key Vault: Private endpoint (recommended for production)
- Storage: Private endpoint (recommended for production)

### Network Isolation
- Consider separate Container App environments:
  - Public environment (public-web, public-api)
  - Private environment (registry-api, workers)

## Secrets Management

### Key Vault Setup
1. Create Key Vault with private endpoint
2. Grant Managed Identity access:
   - Container Apps (read secrets)
   - Workers (read secrets)
3. Store secrets:
   - Database connection strings
   - Entra ID secrets
   - External API keys
   - Signing keys

### Secret Rotation
- Implement secret rotation policy
- Use Key Vault automatic rotation where possible
- Update services to refresh secrets periodically

## Compliance Considerations

### Audit Requirements
- All access to private data logged
- Policy changes tracked
- Evidence pack access tracked
- Export generation tracked

### Data Retention
- Audit logs: 7 years
- Score snapshots: Append-only (permanent)
- Drift events: Append-only (permanent)
- Evidence packs: Per workspace retention policy
- Exports: 90 days (configurable)

### Right to Respond
- Providers can submit evidence packs
- Evidence validation workflow
- Public display of provider response status
- Fairness controls (no defamation risk)

## Security Checklist

### Public API
- [ ] Rate limiting configured
- [ ] WAF rules active
- [ ] Caching headers set
- [ ] ETag support implemented
- [ ] Error messages don't leak sensitive info
- [ ] CORS configured correctly
- [ ] No private data in responses

### Private API
- [ ] OIDC JWT validation working
- [ ] RBAC roles enforced
- [ ] Workspace isolation tested
- [ ] Audit logging enabled
- [ ] Row-level security configured
- [ ] Private endpoints configured
- [ ] Key Vault integration working

### Infrastructure
- [ ] Managed Identities configured
- [ ] Key Vault access policies set
- [ ] Network security groups configured
- [ ] Private endpoints enabled (production)
- [ ] Encryption at rest enabled
- [ ] TLS 1.2+ enforced
- [ ] Monitoring and alerts configured
