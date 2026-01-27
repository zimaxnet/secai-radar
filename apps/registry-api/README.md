# Registry API

Private API service for Trust Registry at secairadar.cloud/api/v1/private/*

All `/api/v1/private/*` routes require a valid Entra ID (Azure AD) JWT bearer token. See [Auth](#auth) and [Entra app registration](../../docs/setup/REGISTRY-API-ENTRA.md).

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Entra ID OIDC

## Auth

- **ENTRA_ID_JWKS_URL** – JWKS endpoint for token verification (e.g. `https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys?appid={client_id}` or your tenant’s OpenID Config `jwks_uri`).
- **ENTRA_ID_AUDIENCE** – Required audience in the JWT (e.g. API “Application ID URI” or client ID of the registry API app).

If either is unset, the API returns 503 for protected routes. Entra app-registration steps: [REGISTRY-API-ENTRA.md](../../docs/setup/REGISTRY-API-ENTRA.md).

## Development
```bash
uvicorn main:app --reload --port 8001
```

## Endpoints
- `GET /api/v1/private/registry/servers` - List workspace inventory
- `POST /api/v1/private/registry/servers` - Add server to inventory
- `GET /api/v1/private/registry/policies` - List workspace policies
- `POST /api/v1/private/registry/policies` - Create policy
- `POST /api/v1/private/registry/evidence-packs` - Upload evidence pack
- `POST /api/v1/private/registry/exports/audit-pack` - Create audit pack export
