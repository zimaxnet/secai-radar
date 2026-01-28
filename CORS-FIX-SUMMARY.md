# CORS & Database Connection Fix - Summary

## Problem Statement

The SecAI Radar public API was returning CORS errors to the frontend:

```
CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource
GET https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status - 400 Bad Request
```

This prevented the frontend at `https://secairadar.cloud` from accessing:
- `/api/v1/public/status`
- `/api/v1/public/mcp/rankings`
- `/api/v1/public/mcp/summary`

## Root Cause Analysis

### Primary Issue: Missing Database Connection String

The Azure Container Apps deployment was missing a properly configured `DATABASE_URL` environment variable:

**Problem:**
- Bicep infrastructure file (`mcp-infrastructure.bicep`) had hardcoded placeholder: `'postgresql://...'`
- No actual PostgreSQL connection string was being passed to container apps
- Database connections failed, returning 500/400 errors

**Result:**
- API endpoints returned errors
- CORS headers were not being set in error responses (default behavior)
- Browser blocked all requests due to missing CORS headers

### Secondary Issue: Missing Exception Handlers

Even with CORS middleware configured, unhandled exceptions weren't returning CORS headers because:
- Exception responses bypassed the CORS middleware
- No global error handler existed to ensure CORS headers on all responses

## Solution Overview

### 1. Application Layer Fix (`apps/public-api/main.py`)

**Added:**
- Global exception handler that catches all unhandled exceptions
- Ensures CORS headers are included in all error responses
- Restricted HTTP methods to `["GET", "POST", "OPTIONS"]`
- Added `expose_headers=["*"]` to expose all headers to client

**Result:** Browser can now see error details even when database is unavailable

### 2. Infrastructure Layer Fix (`infra/mcp-infrastructure.bicep`)

**Added:**
```bicep
@description('PostgreSQL admin password (should be provided at deployment time)')
@secure()
param postgresAdminPassword string
```

**Updated all Container App database secrets:**
```bicep
value: 'postgresql://secairadar:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/secairadar'
```

**Components Updated:**
1. Public API Container App
2. Registry API Container App  
3. Scout Worker Job (pipeline)
4. PostgreSQL Server configuration

**Result:** All services now receive the correct database connection string from environment variables

### 3. Parameter Configuration (`infra/parameters/dev.bicepparam`)

**Added:**
```bicep
param postgresAdminPassword = 'SecureP@ssw0rd2024!'
```

**For Production:**
Should use Azure Key Vault:
```bicep
param postgresAdminPassword = keyVault.getSecret('postgresAdminPassword')
```

## Files Modified

```
secai-radar/
├── apps/public-api/main.py                    [MODIFIED] - Added CORS error handlers
├── infra/mcp-infrastructure.bicep             [MODIFIED] - Fixed database connection strings
├── infra/parameters/dev.bicepparam            [MODIFIED] - Added postgresAdminPassword
├── CORS-AND-DATABASE-FIX.md                   [NEW]      - Detailed technical explanation
└── DEPLOYMENT-CHECKLIST-CORS-FIX.md           [NEW]      - Step-by-step deployment guide
```

## How the Fix Works

### Request Flow - Now Fixed

```
Browser Request to: https://secai-radar-public-api.../api/v1/public/status
                              ↓
                    FastAPI CORS Middleware
                              ↓
                    Route Handler (get_status)
                              ↓
                    Database Dependency (get_db)
                              ↓
                    ✓ Database Connection Succeeds
                              ↓
                    Return Data with CORS Headers
                              ↓
                    Browser Allows Response (200 OK)
```

### Error Flow - Now Fixed

```
Browser Request to: https://secai-radar-public-api.../api/v1/public/status
                              ↓
                    FastAPI CORS Middleware
                              ↓
                    Route Handler (get_status)
                              ↓
                    Database Dependency (get_db)
                              ↓
                    ✗ Database Connection Fails
                              ↓
                    Exception Raised (Connection Error)
                              ↓
                    Global Exception Handler
                              ↓
                    Return Error with CORS Headers (500)
                              ↓
                    Browser Can Display Error (CORS allows it)
```

## Deployment Impact

### What Gets Deployed

1. **Code Changes** (apps/public-api/main.py)
   - Requires rebuilding Docker image
   - `docker build -t zimaxnet/secai-radar-public-api:prod-latest apps/public-api/`
   - `docker push zimaxnet/secai-radar-public-api:prod-latest`

2. **Infrastructure Changes** (infra/mcp-infrastructure.bicep)
   - Creates/updates PostgreSQL server with proper configuration
   - Updates all Container Apps with correct environment variables
   - No data loss - just updates connections

3. **Configuration** (infra/parameters/dev.bicepparam)
   - Passes secure PostgreSQL password to deployment
   - Must be updated before deployment

### Zero-Downtime Deployment

The fix allows for zero-downtime deployment:
1. New container replicas start with correct DATABASE_URL
2. Old replicas continue serving requests
3. Traffic gradually shifts to new replicas (Container Apps handles this)
4. Old replicas are terminated

## Testing Checklist

After deployment, verify:

- [ ] Container App environment variables include DATABASE_URL
- [ ] PostgreSQL server is accessible from Container Apps
- [ ] `/health` endpoint returns 200 OK
- [ ] `/api/v1/public/status` returns 200 OK with data
- [ ] CORS preflight OPTIONS request succeeds
- [ ] Frontend at secairadar.cloud loads without console errors
- [ ] All data displays correctly on frontend
- [ ] Network tab shows all API requests succeeding

## Security Notes

⚠️ **Important Security Considerations:**

1. **Password Management**
   - Dev password in this fix is for testing only
   - Use Azure Key Vault for production secrets
   - Never commit real passwords to git

2. **Secrets Handling**
   - Container App secrets are encrypted at rest
   - Use managed identities when possible
   - Rotate passwords regularly

3. **Network Security**
   - PostgreSQL should be on private subnet (not public)
   - Use firewall rules to restrict Container Apps only
   - Enable SSL/TLS for database connections

## Rollback Plan

If issues occur after deployment:

```bash
# Revert to previous Bicep deployment
az deployment group create \
  --resource-group secai-radar-prod-rg \
  --template-file mcp-infrastructure.bicep \
  --parameters <previous-parameters-file>

# Or rollback code to previous image
az containerapp update \
  --resource-group secai-radar-prod-rg \
  --name secai-radar-prod-public-api \
  --image zimaxnet/secai-radar-public-api:prod-previous
```

## Success Criteria

✅ **Fix is Successful When:**

1. API returns 200 OK with data
2. Error responses include CORS headers
3. Frontend loads without console errors
4. No CORS policy blocks appear in browser console
5. All endpoints return proper JSON responses
6. Database connection is working

## Next Steps

1. Review changes in CORS-AND-DATABASE-FIX.md
2. Update parameter files with production credentials/Key Vault refs
3. Follow DEPLOYMENT-CHECKLIST-CORS-FIX.md for deployment
4. Test thoroughly in dev/staging before production
5. Monitor logs after production deployment

## Contact & Support

For deployment issues:
1. Check logs: `az containerapp logs show --name secai-radar-prod-public-api`
2. Verify database: `az postgres flexible-server show --name secai-radar-prod-postgres`
3. Review DEPLOYMENT-CHECKLIST-CORS-FIX.md troubleshooting section

---

**Last Updated:** 2024-01-28  
**Version:** 1.0  
**Status:** Ready for Deployment
