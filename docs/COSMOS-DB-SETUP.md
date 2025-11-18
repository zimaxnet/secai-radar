# Azure Cosmos DB Setup for State Persistence

## Overview

The multi-agent orchestration system uses Azure Cosmos DB to persist assessment state across agent handoffs and workflow phases. This enables:
- State recovery after failures
- Long-running assessments
- State inspection and debugging
- Multi-instance deployment support

## Prerequisites

1. Azure subscription with Cosmos DB access
2. Azure Cosmos DB account (SQL API)
3. Connection string or endpoint/key credentials

## Setup Steps

### 1. Create Cosmos DB Account with Free Tier

**IMPORTANT**: Enable Free Tier at account creation (cannot be changed later)

**Option A: Use the provided script (Recommended)**
```bash
./scripts/create-cosmos-db.sh
```

**Option B: Manual creation with Free Tier**
```bash
# Create resource group (if needed)
az group create --name secai-radar-rg --location eastus

# Create Cosmos DB account WITH FREE TIER ENABLED
az cosmosdb create \
  --name secai-radar-cosmos \
  --resource-group secai-radar-rg \
  --default-consistency-level Session \
  --locations regionName=eastus failoverPriority=0 \
  --enable-free-tier true
```

**Free Tier Benefits:**
- ✅ **1,000 RU/s** free (shared across all containers)
- ✅ **25 GB storage** free
- ✅ Valid for **12 months** from account creation
- ✅ **$0/month** cost (as long as within limits)

### 2. Get Connection Information

```bash
# Get endpoint
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name secai-radar-cosmos \
  --resource-group secai-radar-rg \
  --query documentEndpoint -o tsv)

# Get key
COSMOS_KEY=$(az cosmosdb keys list \
  --name secai-radar-cosmos \
  --resource-group secai-radar-rg \
  --query primaryMasterKey -o tsv)
```

### 3. Configure Environment Variables

Set the following environment variables:

```bash
export COSMOS_ENDPOINT="https://secai-radar-cosmos.documents.azure.com:443/"
export COSMOS_KEY="<your-primary-key>"
```

Or in Azure Functions/App Service, add to Application Settings:
- `COSMOS_ENDPOINT`
- `COSMOS_KEY`

### 4. Initialize Persistence in Code

```python
from src.orchestrator import StateManager, CosmosStatePersistence

# Create Cosmos DB persistence
cosmos_persistence = CosmosStatePersistence(
    cosmos_endpoint=os.getenv("COSMOS_ENDPOINT"),
    cosmos_key=os.getenv("COSMOS_KEY"),
    database_name="secai_radar",
    container_name="assessment_states"
)

# Create state manager with persistence
state_manager = StateManager(cosmos_persistence=cosmos_persistence)
```

## Database and Container Structure

### Database: `secai_radar`
- Contains all assessment state data

### Container: `assessment_states`
- **Partition Key**: `/assessment_id`
- **Throughput**: 400 RU/s (adjustable based on load)

### Document Schema

Each document represents an assessment state:

```json
{
  "id": "assessment-001",
  "assessment_id": "assessment-001",
  "tenant_id": "tenant-alpha",
  "phase": "assessment",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "budget": 100000.0,
  "budget_remaining": 95000.0,
  "critical_risks": [],
  "agent_contexts": {},
  "findings": [],
  "events": [],
  ...
}
```

## Usage Examples

### Persist State

```python
# After state updates
await state_manager.persist_state(state)
```

### Load State

```python
# Load existing assessment
state = await state_manager.load_state("assessment-001")
```

### List Assessments

```python
# List all assessments for a tenant
assessments = await cosmos_persistence.list_assessments(tenant_id="tenant-alpha")
```

### Delete State

```python
# Delete assessment state
await cosmos_persistence.delete_state("assessment-001")
```

## Performance Considerations

### Throughput (RU/s)
- **Development**: 400 RU/s (minimum)
- **Production**: 1000-4000 RU/s (based on assessment volume)
- Adjust based on:
  - Number of concurrent assessments
  - State update frequency
  - Document size

### Partitioning
- Partition key is `assessment_id`
- Each assessment is isolated in its own partition
- Enables efficient queries and scaling

### Indexing
- Cosmos DB automatically indexes all properties
- No manual index configuration needed for basic queries

## Monitoring

### Check Costs and Usage

**Use the provided script:**
```bash
./scripts/check-cosmos-costs.sh
```

This script shows:
- Free Tier status and expiration date
- Current throughput configuration
- Storage usage
- Cost estimation
- Links to Azure Portal cost views

### Metrics to Monitor
- Request units consumed (stay under 1,000 RU/s for free tier)
- Request rate (requests/second)
- Data size (stay under 25 GB for free tier)
- Latency (P50, P99)

### Query Performance
```python
# Enable query metrics
query = "SELECT * FROM c WHERE c.tenant_id = 'tenant-alpha'"
items = container.query_items(
    query=query,
    enable_cross_partition_query=True,
    populate_query_metrics=True
)
```

### View Costs in Azure Portal

1. **Cost Analysis (Recommended)**:
   - Navigate to: Cost Management + Billing
   - Select your subscription
   - View "Cost by resource"
   - Filter by "Cosmos DB" or resource name

2. **Direct Resource Cost**:
   - Go to Cosmos DB account in portal
   - Click "Cost analysis" in left menu
   - View current month costs

3. **Azure CLI**:
   ```bash
   az consumption usage list \
     --start-date $(date -u -d 'first day of this month' +%Y-%m-%d) \
     --end-date $(date -u +%Y-%m-%d) \
     --query "[?instanceName=='secai-radar-cosmos']"
   ```

## Cost Optimization

1. **Use provisioned throughput** for predictable workloads
2. **Enable autoscale** for variable workloads
3. **Archive old assessments** to reduce storage costs (see cost analysis)
4. **Use change feed** for real-time updates (if needed)
5. **Consider Reserved Capacity** for 30-65% discount on production workloads
6. **Use Free Tier** for development (1,000 RU/s + 25 GB free for 12 months)

**For detailed cost analysis, see [COSMOS-DB-COST-ANALYSIS.md](./COSMOS-DB-COST-ANALYSIS.md)**

## Troubleshooting

### Connection Issues
- Verify `COSMOS_ENDPOINT` and `COSMOS_KEY` are set correctly
- Check firewall rules if using IP restrictions
- Verify network connectivity

### Performance Issues
- Increase throughput (RU/s) if throttled
- Check partition key distribution
- Review query patterns

### Data Issues
- Verify state serialization/deserialization
- Check for schema mismatches
- Review error logs

## Security

1. **Use Managed Identity** when possible (instead of keys)
2. **Enable firewall rules** to restrict access
3. **Use private endpoints** for production
4. **Rotate keys** regularly
5. **Enable diagnostic logs** for auditing

## Backup and Recovery

Cosmos DB provides:
- **Automatic backups**: Continuous backup (7-30 days retention)
- **Point-in-time restore**: Restore to any point in retention period
- **Manual backups**: Export to JSON

```bash
# Export assessment states
az cosmosdb sql container export \
  --account-name secai-radar-cosmos \
  --database-name secai_radar \
  --container-name assessment_states \
  --output-folder ./backup
```

