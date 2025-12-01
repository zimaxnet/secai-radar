# Azure Cosmos DB Cost Analysis for SecAI Radar

## Overview

This document analyzes the cost implications of using Azure Cosmos DB for state persistence in the SecAI Radar multi-agent orchestration system.

## Pricing Models

Azure Cosmos DB offers three pricing models:

### 1. Provisioned Throughput (Standard)
- **Best for**: Predictable, consistent workloads
- **Pricing**: ~$0.008 per hour per 100 RU/s
- **Minimum**: 400 RU/s (~$0.032/hour = ~$23/month)
- **Billing**: Hourly based on maximum provisioned throughput

### 2. Autoscale Provisioned Throughput
- **Best for**: Variable workloads with predictable peaks
- **Pricing**: ~$0.012 per hour per 100 RU/s (50% premium)
- **Scales**: Automatically between 10% and 100% of max RU/s
- **Billing**: Based on highest RU/s used each hour

### 3. Serverless
- **Best for**: Intermittent, unpredictable workloads
- **Pricing**: $0.25 per million RU consumed
- **No minimum**: Pay only for what you use
- **Limits**: Max 5,000 RU/s per operation, 50 GB storage

## Cost Components

### 1. Throughput (RU/s) Costs

**Request Unit (RU) Calculation:**
- **Read 1 KB item**: ~1 RU
- **Write 1 KB item**: ~5 RU
- **Query**: ~3-10 RU (depends on complexity)
- **Upsert**: ~5-10 RU

**SecAI Radar Usage Estimates:**

| Operation | Frequency | RU per Op | Total RU/s |
|-----------|-----------|-----------|------------|
| State Persist (upsert) | Every agent handoff (~50/assessment) | ~10 RU | ~0.5 RU/s |
| State Load (read) | Every agent start (~50/assessment) | ~1 RU | ~0.05 RU/s |
| List Assessments (query) | 10/day | ~5 RU | ~0.001 RU/s |
| **Total Estimated** | | | **~0.55 RU/s** |

**Note**: These are per-assessment estimates. Multiply by concurrent assessments.

### 2. Storage Costs

**Storage Pricing**: $0.25 per GB per month

**Document Size Estimates:**
- Average assessment state: ~50-100 KB (JSON)
- With events/findings: ~200-500 KB (growing over time)
- Maximum (completed assessment): ~1-2 MB

**Storage Projections:**

| Scenario | Assessments | Avg Size | Total Storage | Monthly Cost |
|----------|-------------|----------|--------------|--------------|
| Development | 10 | 100 KB | 1 MB | $0.00025 |
| Small Production | 100 | 200 KB | 20 MB | $0.005 |
| Medium Production | 1,000 | 300 KB | 300 MB | $0.075 |
| Large Production | 10,000 | 500 KB | 5 GB | $1.25 |

### 3. Data Transfer Costs

- **Ingress (Data In)**: FREE
- **Egress (Data Out)**: 
  - First 5 GB/month: FREE
  - Additional: $0.05 per GB
- **Cross-region**: Additional charges apply

**SecAI Radar Impact**: Minimal (state data is small, mostly within Azure)

## Cost Scenarios

### Scenario 1: Development/Testing
- **Throughput**: 400 RU/s (minimum provisioned)
- **Storage**: <1 GB
- **Assessments**: <10 concurrent
- **Monthly Cost**: ~$23-25/month

### Scenario 2: Small Production (Startup)
- **Throughput**: 400 RU/s (provisioned) or Serverless
- **Storage**: ~100 MB
- **Assessments**: 10-50 concurrent
- **Monthly Cost**: 
  - Provisioned: ~$23-25/month
  - Serverless: ~$5-10/month (if intermittent)

### Scenario 3: Medium Production
- **Throughput**: 1,000 RU/s (provisioned) or Autoscale (400-4,000)
- **Storage**: ~1 GB
- **Assessments**: 50-200 concurrent
- **Monthly Cost**:
  - Provisioned: ~$58/month
  - Autoscale: ~$87/month (if scaling frequently)
  - Serverless: ~$20-40/month (if intermittent)

### Scenario 4: Large Production
- **Throughput**: 4,000 RU/s (provisioned) or Autoscale
- **Storage**: ~10 GB
- **Assessments**: 200-1,000 concurrent
- **Monthly Cost**:
  - Provisioned: ~$230/month
  - Autoscale: ~$345/month
  - Serverless: ~$100-200/month (if intermittent)

## Cost Optimization Strategies

### 1. Use Free Tier (Development)
- **1,000 RU/s** and **25 GB storage** free for first 12 months
- Perfect for development and testing
- **Savings**: ~$23/month

### 2. Choose Right Pricing Model

**Use Serverless if:**
- Workload is intermittent (<50% utilization)
- Unpredictable traffic patterns
- Development/testing environments
- **Savings**: 50-80% vs provisioned for low utilization

**Use Provisioned if:**
- Consistent, predictable workload
- >50% utilization
- Need guaranteed performance
- **Best for**: Production with steady load

**Use Autoscale if:**
- Variable but predictable peaks
- Want automatic scaling
- **Trade-off**: 50% premium but better than over-provisioning

### 3. Optimize RU Consumption

**Reduce Write Operations:**
- Batch state updates instead of per-handoff
- Only persist on significant state changes
- **Savings**: 50-70% RU reduction

**Optimize Queries:**
- Use partition key in queries (assessment_id)
- Limit query results
- Use point reads instead of queries when possible
- **Savings**: 30-50% RU reduction

**Reduce Document Size:**
- Archive old events/findings to separate storage
- Compress large artifacts
- **Savings**: Lower storage costs, faster operations

### 4. Reserved Capacity (Production)

**1-Year Commitment**: ~30% discount
**3-Year Commitment**: ~65% discount

**Example**:
- 1,000 RU/s provisioned: $58/month → $20/month (3-year)
- **Savings**: $38/month = $456/year

### 5. Archive Old Assessments

**Strategy**: Move completed assessments to Azure Blob Storage (cheaper)

**Cost Comparison**:
- Cosmos DB: $0.25/GB/month
- Blob Storage: $0.0184/GB/month (Hot tier)
- **Savings**: 93% reduction for archived data

**Implementation**:
```python
# Archive assessments older than 90 days
if assessment_age > 90_days:
    archive_to_blob(assessment_state)
    delete_from_cosmos(assessment_id)
```

### 6. Monitor and Adjust

**Key Metrics**:
- RU/s utilization (target: 60-80%)
- Storage growth rate
- Request patterns

**Actions**:
- Scale down if consistently <30% utilization
- Switch to serverless if utilization is low
- Archive old data regularly

## Cost Comparison with Alternatives

### Alternative 1: Azure Table Storage
- **Pricing**: $0.054 per 10,000 transactions + $0.063/GB storage
- **Pros**: Much cheaper for simple key-value storage
- **Cons**: No complex queries, eventual consistency
- **Cost**: ~$5-10/month for similar workload
- **Trade-off**: Less flexible, but 70-80% cheaper

### Alternative 2: Azure SQL Database
- **Pricing**: $5/month (Basic tier) to $15/month (S0)
- **Pros**: SQL queries, ACID transactions
- **Cons**: Less scalable, more complex setup
- **Cost**: ~$5-15/month
- **Trade-off**: Good for structured data, but less scalable

### Alternative 3: In-Memory (Redis Cache)
- **Pricing**: $15/month (Basic C0) to $55/month (Standard C1)
- **Pros**: Very fast, good for caching
- **Cons**: Not persistent (needs backup), limited querying
- **Cost**: ~$15-55/month
- **Trade-off**: Fast but requires backup strategy

### Alternative 4: Azure Blob Storage (JSON files)
- **Pricing**: $0.0184/GB/month (Hot tier)
- **Pros**: Very cheap, simple
- **Cons**: No querying, manual state management
- **Cost**: ~$0.50-2/month
- **Trade-off**: Cheapest but requires custom implementation

## Recommendations

### For Development/Testing
✅ **Use Free Tier** (1,000 RU/s + 25 GB free)
- Cost: $0/month
- Sufficient for development

### For Small Production (<50 concurrent assessments)
✅ **Use Serverless** or **400 RU/s Provisioned**
- Serverless: ~$5-10/month (if intermittent)
- Provisioned: ~$23/month (if consistent)
- Storage: <$1/month

### For Medium Production (50-200 concurrent)
✅ **Use 1,000 RU/s Provisioned** or **Autoscale (400-2,000)**
- Provisioned: ~$58/month
- Autoscale: ~$87/month (if variable)
- Consider Reserved Capacity for 30-65% discount

### For Large Production (>200 concurrent)
✅ **Use 4,000+ RU/s Provisioned** with **Reserved Capacity**
- Provisioned: ~$230/month
- 3-Year Reserved: ~$80/month (65% discount)
- Archive old assessments to Blob Storage

## Cost Monitoring

### Azure Cost Management
1. Set up budget alerts
2. Monitor RU/s utilization
3. Track storage growth
4. Review monthly costs

### Recommended Alerts
- **RU/s utilization >80%**: Scale up warning
- **RU/s utilization <30%**: Consider scaling down or serverless
- **Storage >10 GB**: Consider archiving
- **Monthly cost >$100**: Review optimization opportunities

## Example Monthly Cost Breakdown

### Small Production Scenario
```
Component              | Cost
-----------------------|--------
Provisioned Throughput | $23.00
(400 RU/s)             |
Storage (100 MB)       | $0.03
Data Transfer          | $0.00
-----------------------|--------
Total                  | $23.03/month
```

### Medium Production Scenario (with optimization)
```
Component                    | Cost
-----------------------------|--------
Provisioned Throughput       | $58.00
(1,000 RU/s)                 |
Storage (1 GB)                | $0.25
Data Transfer                 | $0.00
Archived Data (Blob Storage)  | $0.18
(10 GB)                       |
-----------------------------|--------
Total                        | $58.43/month
```

### With 3-Year Reserved Capacity
```
Component                    | Cost
-----------------------------|--------
Reserved Throughput          | $20.00
(1,000 RU/s, 65% discount)    |
Storage (1 GB)                | $0.25
Archived Data (Blob Storage)  | $0.18
-----------------------------|--------
Total                        | $20.43/month
Savings vs Pay-as-you-go     | $38.00/month
```

## Conclusion

**For SecAI Radar multi-agent system:**

1. **Development**: Use Free Tier ($0/month)
2. **Small Production**: Serverless or 400 RU/s (~$5-25/month)
3. **Medium Production**: 1,000 RU/s with Reserved Capacity (~$20-60/month)
4. **Large Production**: 4,000+ RU/s with Reserved + Archiving (~$80-200/month)

**Key Optimization**: Archive completed assessments to Blob Storage for 93% storage cost reduction.

**Total Cost Range**: $0 (dev) to $200/month (large production with optimizations)

