# ✅ Authentication Enabled - Quick Reference

## 🎉 Status: Authentication is Now Configured!

Entra ID authentication has been successfully enabled for the Static Web App.

## 🔗 Deployment URLs

### Production Environment
- **Main URL**: https://purple-moss-0942f9e10.3.azurestaticapps.net
- **Custom Domain** (when ready): https://secai-radar.zimax.net

## 🔐 Authentication Endpoints

### Entra ID (Azure AD) Authentication

- **Login**: https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad
- **Logout**: https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/logout
- **User Info**: https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/me

### GitHub Authentication (Optional)

- **Login**: https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/github
- **Logout**: https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/logout

## 🛡️ Protected Routes

Routes that require authentication:
- `/tenant/*` - Tenant dashboard and management

Public routes:
- `/` - Homepage

## 🔧 Adding Login/Logout to Your App

### React Example

```tsx
// Login link
<a href="/.auth/login/aad">Login with Microsoft</a>

// Logout link
<a href="/.auth/logout">Logout</a>

// Check authentication status
const checkAuth = async () => {
  const response = await fetch('/.auth/me');
  const user = await response.json();
  if (user.clientPrincipal) {
    console.log('Authenticated:', user.clientPrincipal);
  }
};
```

### User Information

After login, user info is available via:
```javascript
const response = await fetch('/.auth/me');
const { clientPrincipal } = await response.json();

// clientPrincipal contains:
// - identityProvider: "aad"
// - userId: user's object ID
// - userDetails: user's email/name
// - userRoles: array of roles
```

## 📋 Configuration Details

### Environment
- **Environment**: Production
- **Mode**: Role assignments via API
- **Roles API Path**: `/api/roles` (can be configured)

### Provider
- **Entra ID**: Enabled
- **App Registration**: `secai-radar-auth` (ID: `1cd314e6-933a-4bf9-b889-ffe04a815b98`)

## 🧪 Testing Authentication

### Test Login Flow

1. **Visit protected route**:
   ```
   https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
   ```

2. **Should redirect to Microsoft login**

3. **After login, should redirect back to `/tenant`**

### Test User Info

```bash
# After logging in, check user info:
curl https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/me
```

Should return:
```json
{
  "clientPrincipal": {
    "identityProvider": "aad",
    "userId": "...",
    "userDetails": "user@domain.com",
    "userRoles": ["authenticated"]
  }
}
```

## 🔗 Quick Links

- **Main App**: https://purple-moss-0942f9e10.3.azurestaticapps.net
- **Login**: https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad
- **Protected Route**: https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
- **Azure Portal**: https://portal.azure.com/#@zimax.net/resource/subscriptions/23f4e2c5-0667-4514-8e2e-f02ca7880c95/resourceGroups/secai-radar-rg/providers/Microsoft.Web/staticSites/secai-radar/authentication

---

**Status**: ✅ Authentication is enabled and ready to use! 🚀

