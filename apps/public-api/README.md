# Public API

FastAPI service for public read-only endpoints at secairadar.cloud/api/v1/public/*

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL

## Development
```bash
uvicorn main:app --reload --port 8000
```

## Endpoints
- `GET /api/v1/public/health` - Health check
- `GET /api/v1/public/mcp/summary` - Overview KPIs
- `GET /api/v1/public/mcp/rankings` - Rankings with filters
- `GET /api/v1/public/mcp/servers/{idOrSlug}` - Server detail
- `GET /api/v1/public/mcp/servers/{idOrSlug}/evidence` - Evidence list
- `GET /api/v1/public/mcp/servers/{idOrSlug}/drift` - Drift timeline
- `GET /api/v1/public/mcp/daily/{date}` - Daily brief
- `GET /mcp/feed.xml` - RSS feed
- `GET /mcp/feed.json` - JSON Feed
