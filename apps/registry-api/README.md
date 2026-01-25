# Registry API

Private API service for Trust Registry at secairadar.cloud/api/v1/private/*

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Entra ID OIDC

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
