# Fix Roles Source Configuration

## Issue

Error: `"staticwebapp.json" is not a valid roles source. Valid values are "DEFAULT" or an api path (starts with "/api/").`

## Solution

Changed `rolesSource` from `"staticwebapp.json"` to `"DEFAULT"` in `staticwebapp.config.json`.

## What Changed

**Before:**
```json
{
  "auth": { 
    "rolesSource": "staticwebapp.json"
  }
}
```

**After:**
```json
{
  "auth": { 
    "rolesSource": "DEFAULT"
  }
}
```

## What "DEFAULT" Means

When `rolesSource` is set to `"DEFAULT"`:
- All authenticated users automatically get the `"authenticated"` role
- No need for a `staticwebapp.json` file
- Routes with `"allowedRoles": ["authenticated"]` will work automatically

## Alternative: API-Based Roles

If you need custom roles (admin, consultant, etc.), you can:

1. **Create an API endpoint**: `/api/roles`
2. **Change rolesSource** to: `"/api/roles"`
3. **Implement the endpoint** to return user roles based on user identity

Example API endpoint:
```python
# api/roles/__init__.py
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Get user from request headers
    user_id = req.headers.get('x-ms-client-principal-id')
    
    # Determine roles based on user
    roles = ["authenticated"]
    if user_id == "admin-user-id":
        roles.append("admin")
    
    return func.HttpResponse(
        json.dumps({"roles": roles}),
        mimetype="application/json"
    )
```

## Current Configuration

- **rolesSource**: `"DEFAULT"` ✅
- **Routes**: Protected with `"allowedRoles": ["authenticated"]`
- **Behavior**: All authenticated users can access protected routes

## Note on staticwebapp.json

The `staticwebapp.json` file is no longer needed with `"DEFAULT"` roles source. You can delete it if you want, but it won't cause issues if it remains.

---

**Status**: ✅ Fixed! Changed to `"DEFAULT"` which is the correct value for basic authenticated role assignment. 🚀

