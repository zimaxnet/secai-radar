# Roles Configuration for Static Web App

## Current Configuration

**Role assignments API path**: `staticwebapp.json` (file-based roles)

This means roles are defined in a `staticwebapp.json` file in your deployment.

## Options for Role Management

### Option 1: File-Based Roles (Current Setup)

Roles are defined in a `staticwebapp.json` file that should be placed in the `web` directory and deployed with your app.

**Location**: `web/staticwebapp.json`

**Format**:
```json
{
  "roles": [
    {
      "name": "authenticated",
      "members": ["*"]
    },
    {
      "name": "admin",
      "members": ["user1@domain.com", "user2@domain.com"]
    },
    {
      "name": "consultant",
      "members": ["consultant1@domain.com"]
    }
  ]
}
```

**Note**: The `"authenticated"` role with `"*"` means all authenticated users get that role.

### Option 2: API-Based Roles

If you want to use an API endpoint to return roles dynamically, you need to:

1. **Change the configuration** in Azure Portal:
   - Go to: Authentication → Role assignments API path
   - Change from: `staticwebapp.json`
   - To: `/api/roles` (or your custom endpoint)

2. **Create a roles API endpoint** in your Function App:
   - Create: `api/roles/function.json`
   - Create: `api/roles/__init__.py`
   - Return JSON with user roles based on user identity

**Example API Response**:
```json
{
  "roles": ["authenticated", "consultant"]
}
```

## Recommended Approach

For now, **file-based roles** (`staticwebapp.json`) is simpler and works well for most cases. You can migrate to API-based roles later if you need dynamic role assignment.

## Creating staticwebapp.json

Create `web/staticwebapp.json`:

```json
{
  "roles": [
    {
      "name": "authenticated",
      "members": ["*"]
    }
  ]
}
```

This gives all authenticated users the `authenticated` role, which matches your current route protection in `staticwebapp.config.json`.

## Advanced: Custom Roles

If you need role-based access (e.g., admin, consultant, viewer):

```json
{
  "roles": [
    {
      "name": "authenticated",
      "members": ["*"]
    },
    {
      "name": "admin",
      "members": [
        "admin@zimax.net",
        "derek@zimax.net"
      ]
    },
    {
      "name": "consultant",
      "members": [
        "consultant1@zimax.net",
        "consultant2@zimax.net"
      ]
    }
  ]
}
```

Then update `staticwebapp.config.json` routes:

```json
{
  "routes": [
    { "route": "/", "serve": "/index.html" },
    { "route": "/tenant/*", "allowedRoles": ["authenticated"] },
    { "route": "/admin/*", "allowedRoles": ["admin"] }
  ]
}
```

## Current Setup

Your `staticwebapp.config.json` uses:
```json
{
  "auth": { 
    "rolesSource": "staticwebapp.json"
  }
}
```

This expects a `staticwebapp.json` file in your web directory. If you don't have one yet, create it with the basic authenticated role.

## Next Steps

1. **Create `web/staticwebapp.json`** with authenticated role
2. **Deploy** (will be included in next Static Web App deployment)
3. **Test** authentication flow
4. **Add custom roles** as needed

---

**Note**: The `staticwebapp.json` file must be in the `web` directory and will be deployed with your app automatically.

