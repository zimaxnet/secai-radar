
# SecAI Radar API (Azure Functions - Python) — Extended

## New endpoints
- `POST /api/tenant/{tenantId}/import`  
  Accepts **CSV** (raw body) or **JSON array** to upsert controls into Table Storage.
- `GET|POST /api/tenant/{tenantId}/tools`  
  Manage tenant tool inventory (Enabled/ConfigScore).
- `GET /api/tenant/{tenantId}/gaps`  
  Capability-based coverage & gap analysis using:
  - `seeds_tool_capabilities.json` (catalog)
  - `seeds_control_requirements.json` (framework)

## Local dev
1. Start Azurite (UseDevelopmentStorage=true) for Tables/Blobs.
2. Ensure Python 3.12+ is installed
3. `python -m venv .venv && . .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `func start`

## Data model (Tables)
- Controls: PartitionKey=`{tenant}|{domain}`, RowKey=`ControlID`
- TenantTools: PartitionKey=`{tenant}`, RowKey=`vendorToolId`

## Notes
- Extend `seeds/control_requirements.json` as you research the framework.
- Tune `seeds/tool_capabilities.json` strengths per vendor capability.
