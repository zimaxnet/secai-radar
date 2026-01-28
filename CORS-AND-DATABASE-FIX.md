# CORS and Database Connection Fix

## Issue Summary

The public API at `https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io` was returning 400 Bad Request errors to requests from `https://secairadar.cloud` with the following errors:

```
CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
GET https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status net::ERR_FAILED 400 (Bad Request)
```

Affected endpoints:
- `/api/v1/public/status`
- `/api/v1/public/mcp/rankings`
- `/api/v1/public/mcp/summary`

## Root Causes

1. **Database Connection Failure**: The `DATABASE_URL` environment variable was not properly configured in the Azure Container Apps deployment. The Bicep infrastructure file had a hardcoded placeholder (`'postgresql://...'`) instead of constructing the actual PostgreSQL connection string.

2. **Missing CORS Error Handlers**: While CORS middleware was configured, unhandled exceptions (like database connection failures) were not returning CORS headers, preventing the browser from displaying proper error messages.

## Changes Made

### 1. Updated FastAPI Application (`apps/public-api/main.py`)

**Changes:**
- Imported `Request` and `RequestValidationError` for exception handling
- Restricted HTTP methods to `["GET", "POST", "OPTIONS"]` for better security
- Added `expose_headers=["*"]` to ensure all headers are exposed to the client
- Added a global exception handler that ensures CORS headers are included in error responses

**Impact:** Now all error responses (including database connection errors) will include proper CORS headers, allowing the browser to display meaningful error messages.

### 2. Fixed Infrastructure as Code (`infra/mcp-infrastructure.bicep`)

**Changes:**

#### Added PostgreSQL Password Parameter
```bicep
@description('PostgreSQL admin password (should be provided at deployment time)')
@secure()
param postgresAdminPassword string
```

#### Updated PostgreSQL Server Configuration
Changed from:
```bicep
administratorLoginPassword: '@secureString()' // Placeholder
```

To:
```bicep
administratorLoginPassword: postgresAdminPassword
```

#### Fixed Database Connection Strings

**Public API Container App:**
```bicep
value: 'postgresql://secairadar:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/secairadar'
```

**Registry API Container App:**
```bicep
value: 'postgresql://secairadar:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/secairadar'
```

**Scout Worker Job:**
```bicep
value: 'postgresql://secairadar:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/secairadar'
```

#### How It Works
- Uses Bicep reference to the PostgreSQL server: `postgresServer.properties.fullyQualifiedDomainName`
- Constructs the full connection string with the admin password
- Stores it as a secret in the Container App's configuration
- References it via `secretRef` in the `DATABASE_URL` environment variable

### 3. Updated Parameter File (`infra/parameters/dev.bicepparam`)

**Added:**
```bicep
param postgresAdminPassword = 'SecureP@ssw0rd2024!'
```

**Important Note:** The default password in the dev parameter file should be changed for production deployments. Use Azure Key Vault references instead:

```bicep
param postgresAdminPassword = keyVault.getSecret('postgresAdminPassword')
```

## Deployment Instructions

### Step 1: Update Parameter File

Before deploying, update the `postgresAdminPassword` parameter in your parameter files:

**For Development:**
```bash
# Update: infra/parameters/dev.bicepparam
param postgresAdminPassword = 'YourSecurePassword2024!'
```

**For Production (using Key Vault):**
```bash
# Create/store password in Azure Key Vault
az keyvault secret set --vault-name <KeyVaultName> --name postgresAdminPassword --value '<SecurePassword>'

# Then use in bicepparam file:
param postgresAdminPassword = keyVault.getSecret('postgresAdminPassword')
```

### Step 2: Deploy Infrastructure

```bash
cd infra

# Deploy with parameters
az deployment group create \
  --resource-group secai-radar-prod-rg \
  --template-file mcp-infrastructure.bicep \
  --parameters parameters/prod.bicepparam \
  --parameters postgresAdminPassword='<your-secure-password>'
```

### Step 3: Verify Database Connection

After deployment, the Container Apps should have the correct `DATABASE_URL` environment variable. Verify by:

```bash
# Check container app environment variables
az containerapp show \
  --resource-group secai-radar-prod-rg \
  --name secai-radar-prod-public-api \
  --query "properties.template.containers[0].env"
```

## Testing

### Test CORS Headers
```bash
curl -i -X OPTIONS \
  -H "Origin: https://secairadar.cloud" \
  -H "Access-Control-Request-Method: GET" \
  https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status
```

Expected response should include:
```
Access-Control-Allow-Origin: https://secairadar.cloud
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

### Test API Endpoint
```bash
curl https://secai-radar-public-api.lemonriver-a8b248dc.centralus.azurecontainerapps.io/api/v1/public/status
```

Should return:
```json
{
  "status": "operational",
  "lastSuccessfulRun": null,
  "currentRun": null,
  "timestamp": "2024-01-28T..."
}
```

## Files Modified

1. **apps/public-api/main.py**
   - Added exception handlers for CORS compliance
   - Updated middleware configuration

2. **infra/mcp-infrastructure.bicep**
   - Added `postgresAdminPassword` parameter
   - Fixed database connection strings for all container apps and jobs
   - Updated PostgreSQL server to use the parameter

3. **infra/parameters/dev.bicepparam**
   - Added `postgresAdminPassword` parameter value

## Security Considerations

⚠️ **Important:** 
- The password in `dev.bicepparam` is for development only
- For production, use Azure Key Vault to manage secrets
- Never commit real passwords to version control
- Rotate passwords regularly
- Use managed identities where possible instead of hardcoded credentials

## Next Steps

1. Update production parameter files with actual secure passwords or Key Vault references
2. Re-deploy the infrastructure
3. Test the API endpoints from the frontend
4. Monitor logs for any connection issues:
   ```bash
   az containerapp logs show \
     --name secai-radar-prod-public-api \
     --resource-group secai-radar-prod-rg
   ```
