# Entra ID app registration for Registry API (T-090)

The Registry API validates JWTs from Microsoft Entra ID (Azure AD). Configure an app registration and set `ENTRA_ID_JWKS_URL` and `ENTRA_ID_AUDIENCE` so all `/api/v1/private/*` routes require a valid token.

## 1. App registration

1. Open [Microsoft Entra Admin Center](https://entra.microsoft.com) and select your tenant.
2. Go to **Applications** → **App registrations** → **New registration**.
3. **Name**: e.g. `SecAI Radar Registry API`.
4. **Supported account types**: as needed (single tenant or multitenant).
5. **Redirect URI**: leave blank for API-only.
6. Click **Register**.

## 2. Expose an API (audience)

1. In the app, open **Expose an API**.
2. Click **Add** next to “Application ID URI” and accept the default (e.g. `api://<client-id>`) or set a custom value. This URI is the **audience** the API will require in the token.
3. Under **Scopes**, add a scope if you use scope-based checks (e.g. `Registry.Access`). For audience-only validation, the Application ID URI is enough.

## 3. JWKS / issuer

Tokens must be signed with keys published at a JWKS URL. For Entra:

- **Issuer**: `https://login.microsoftonline.com/{tenant-id}/v2.0`
- **JWKS**: `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys`

Use your **tenant ID** (Directory (tenant) ID on the app’s Overview blade).

## 4. Client apps (optional)

To obtain tokens for calling the Registry API, create a separate “client” app (e.g. SPA or backend), grant it **API permissions** to the Registry API app (e.g. the `api://<client-id>/Registry.Access` scope or “Access as user” if applicable). Configure that app for web/SPA or client credentials as needed.

## 5. Environment variables

Set these for the Registry API process:

| Variable | Example | Description |
|----------|---------|-------------|
| **ENTRA_ID_JWKS_URL** | `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys` | JWKS endpoint used to verify token signature. |
| **ENTRA_ID_AUDIENCE** | `api://<registry-api-client-id>` | Required `aud` claim in the JWT (typically the Registry API’s Application ID URI). |

The middleware in `apps/registry-api/src/middleware/auth.py` uses these to validate the Bearer token on each request. If either variable is unset, protected routes return 503.

## 6. Token claims used by the API

- **aud** – Must match `ENTRA_ID_AUDIENCE`.
- **sub** – Treated as `user_id` for workspace membership (RBAC).
- **roles** (or app-specific claim) – Optional; map to RegistryAdmin, PolicyApprover, EvidenceValidator, Viewer, AutomationOperator for RBAC. If your token uses a different claim (e.g. `http://schemas.../roles`), the RBAC middleware must be wired to read it.

## References

- [Entra ID tokens](https://learn.microsoft.com/en-us/entra/identity-platform/security-tokens)
- [Validating tokens](https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens#validating-tokens)
- Registry API auth code: `apps/registry-api/src/middleware/auth.py`
