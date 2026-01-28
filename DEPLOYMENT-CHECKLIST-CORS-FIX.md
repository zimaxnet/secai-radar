# Deployment Checklist: CORS & Database Fix

## Pre-Deployment

- [ ] Review changes in [CORS-AND-DATABASE-FIX.md](./CORS-AND-DATABASE-FIX.md)
- [ ] Create secure PostgreSQL password (minimum 12 characters, mixed case, numbers, symbols)
- [ ] Update `infra/parameters/dev.bicepparam` with secure password
- [ ] Create additional parameter files if needed (staging, prod):
  ```bash
  cp infra/parameters/dev.bicepparam infra/parameters/staging.bicepparam
  cp infra/parameters/dev.bicepparam infra/parameters/prod.bicepparam
  ```
- [ ] Update all parameter files with environment-specific passwords or Key Vault references

## Validate Bicep Files

```bash
cd secai-radar/infra

# Check for syntax errors
az bicep build --file mcp-infrastructure.bicep

# Validate against Azure subscription
az deployment group validate \
  --resource-group secai-radar-prod-rg \
  --template-file mcp-infrastructure.bicep \
  --parameters parameters/prod.bicepparam \
  --parameters postgresAdminPassword='<your-password>'
```

## Deployment

```bash
# For development environment
az deployment group create \
  --resource-group secai-radar-dev-rg \
  --template-file mcp-infrastructure.bicep \
  --parameters parameters/dev.bicepparam \
  --parameters postgresAdminPassword='<dev-password>'

# For production environment
az deployment group create \
  --resource-group secai-radar-prod-rg \
  --template-file mcp-infrastructure.bicep \
  --parameters parameters/prod.bicepparam \
  --parameters postgresAdminPassword='<prod-password>'
```

## Post-Deployment Verification

### 1. Check Container App Environment Variables

```bash
# Verify PUBLIC API
az containerapp show \
  --resource-group secai-radar-prod-rg \
  --name secai-radar-prod-public-api \
  --query "properties.template.containers[0].env" -o json

# Verify REGISTRY API
az containerapp show \
  --resource-group secai-radar-prod-rg \
  --name secai-radar-prod-registry-api \
  --query "properties.template.containers[0].env" -o json
```

Expected output includes:
```json
[
  {
    "name": "DATABASE_URL",
    "secretRef": "database-connection"
  },
  {
    "name": "ENVIRONMENT",
    "value": "prod"
  }
]
```

### 2. Test Database Connectivity

Check logs for database connection errors:

```bash
# Get recent logs from public API
az containerapp logs show \
  --name secai-radar-prod-public-api \
  --resource-group secai-radar-prod-rg \
  --follow

# Look for successful connections or connection errors
```

### 3. Test API Endpoints

```bash
# Test health endpoint (should work without database)
curl -i https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/health

# Test public API endpoint (requires database)
curl -i https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status

# Test CORS headers
curl -i -X OPTIONS \
  -H "Origin: https://secairadar.cloud" \
  -H "Access-Control-Request-Method: GET" \
  https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status
```

### 4. Test from Frontend

1. Open browser DevTools → Console
2. Navigate to https://secairadar.cloud
3. Verify no CORS errors appear
4. Verify data loads from the public API endpoints

Expected Network requests should succeed with 200 status codes.

## Troubleshooting

### Issue: Still Getting Database Connection Errors

**Check:**
1. PostgreSQL server is running and accessible
2. Firewall rules allow Container Apps to reach PostgreSQL
3. Database credentials are correct
4. `DATABASE_URL` format is valid

**Logs:**
```bash
az containerapp logs show \
  --name secai-radar-prod-public-api \
  --resource-group secai-radar-prod-rg \
  --tail 50
```

### Issue: CORS Errors Still Appearing

**Check:**
1. Main.py has been updated with exception handlers
2. Container app is using latest image with the updated code
3. Rebuild and redeploy the container image

**Redeploy code:**
```bash
cd apps/public-api

# Build Docker image
docker build -t zimaxnet/secai-radar-public-api:prod-latest .

# Push to registry
docker push zimaxnet/secai-radar-public-api:prod-latest

# Restart container app
az containerapp update \
  --resource-group secai-radar-prod-rg \
  --name secai-radar-prod-public-api \
  --image zimaxnet/secai-radar-public-api:prod-latest
```

### Issue: PostgreSQL Server Not Found

**Check:**
1. PostgreSQL server exists in Azure
2. Server name in connection string matches actual server

**List servers:**
```bash
az postgres flexible-server list --resource-group secai-radar-prod-rg
```

## Rollback Instructions

If deployment fails, rollback to previous version:

```bash
# Get previous deployment
az deployment group list \
  --resource-group secai-radar-prod-rg \
  --query "[0:5].[name,timestamp]" -o table

# Deploy previous version
az deployment group create \
  --resource-group secai-radar-prod-rg \
  --template-file mcp-infrastructure.bicep \
  --parameters <previous-parameters-file>
```

## Success Criteria

- [ ] All Container Apps show `DATABASE_URL` environment variable with correct format
- [ ] No database connection errors in Container App logs
- [ ] API endpoints return 200 status with valid JSON responses
- [ ] CORS headers present in responses
- [ ] Frontend loads without console errors
- [ ] Data displays correctly on https://secairadar.cloud

## Monitoring

Set up alerts for:

1. Container App HTTP error rates (4xx, 5xx)
2. PostgreSQL connection failures
3. Container App restarts

```bash
# Example: Alert on 500 errors
az monitor metrics list \
  --resource /subscriptions/<subscription-id>/resourceGroups/secai-radar-prod-rg/providers/Microsoft.App/containerApps/secai-radar-prod-public-api \
  --metric Http5xx \
  --start-time 2024-01-28T00:00:00 \
  --interval PT5M
```
