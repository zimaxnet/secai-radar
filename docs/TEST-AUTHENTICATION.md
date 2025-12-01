# Testing Authentication

## Quick Test Commands

### 1. Test Protected Route (Should Redirect to Login)

```bash
curl -L https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
```

**Expected**: Redirects to Microsoft login page

### 2. Test Login Endpoint

```bash
curl -I https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/login/aad
```

**Expected**: `Location` header pointing to Microsoft login

### 3. Test User Info (Unauthenticated)

```bash
curl https://purple-moss-0942f9e10.3.azurestaticapps.net/.auth/me
```

**Expected**: `{"clientPrincipal": null}` (when not logged in)

### 4. Test Public Route

```bash
curl https://purple-moss-0942f9e10.3.azurestaticapps.net
```

**Expected**: Returns homepage HTML (no redirect)

## Browser Testing

### Test Login Flow

1. **Open browser**: https://purple-moss-0942f9e10.3.azurestaticapps.net
2. **Navigate to protected route**: https://purple-moss-0942f9e10.3.azurestaticapps.net/tenant
3. **Expected**: Redirects to Microsoft login
4. **After login**: Should redirect back to `/tenant` route

### Test User Info After Login

1. **Open browser console** (F12)
2. **Run**:
   ```javascript
   fetch('/.auth/me')
     .then(r => r.json())
     .then(data => console.log(data))
   ```
3. **Expected**: Should return user info with `clientPrincipal` object

## Verification Checklist

- [ ] Protected route redirects to login
- [ ] Login endpoint works
- [ ] Public route accessible without login
- [ ] User info endpoint returns `null` when not authenticated
- [ ] After login, user info endpoint returns user data
- [ ] After login, protected routes are accessible

## Troubleshooting

### If Protected Route Returns 401 Instead of Redirect

- Check `responseOverrides` in `staticwebapp.config.json`
- Verify authentication is enabled in Azure Portal
- Wait 2-3 minutes after configuration changes

### If Login Doesn't Work

- Verify app registration is configured correctly
- Check redirect URIs in app registration
- Verify authentication provider is enabled in Portal

---

**Status**: Ready for testing! 🚀

