# SecAI Radar - Monthly Cost Estimation

> **Last Updated:** 2025-01-XX  
> **Purpose:** Estimate monthly infrastructure costs for SecAI Radar deployment

---

## Infrastructure Components

Based on the current architecture (ADR 0001), the following Azure services are deployed:

1. **Azure Static Web Apps** (Free tier)
2. **Azure Functions** (Consumption plan)
3. **Azure Storage Account** (Standard_LRS)
   - Table Storage (Controls, TenantTools, Evidence metadata)
   - Blob Storage (Evidence files, CSVs, exports)
4. **Azure OpenAI** (Optional - AI features)
5. **Azure Key Vault** (Optional - if used for secrets)

---

## Cost Breakdown (Monthly Estimates)

### 1. Azure Static Web Apps - **FREE** ✅

**Current Setup:** Free tier

**Included in Free Tier:**
- 100 GB bandwidth per month
- Unlimited custom domains
- Built-in SSL certificates
- Entra ID authentication integration
- 100 GB storage

**Cost:** **$0/month**

**Notes:**
- Free tier is sufficient for MVP and moderate usage
- Standard tier ($9/month + usage) only needed if you exceed:
  - 100 GB bandwidth
  - Need custom authentication providers
  - Need staging environments

---

### 2. Azure Functions (Consumption Plan) - **~$5-15/month** 💰

**Current Setup:** Consumption plan (pay-per-execution)

**Pricing Model:**
- **Execution Time:** $0.000016 per GB-second
- **Requests:** First 1 million requests/month free, then $0.20 per million
- **Memory:** Charged based on memory allocated and execution time

**Assumptions for Estimation:**
- **Average execution time:** 1-2 seconds per function call
- **Memory allocation:** 1 GB per execution (default)
- **Monthly executions:** 10,000-50,000 (conservative estimate)
- **Average requests per day:** 300-1,500

**Cost Calculation:**
- **Execution Time:**
  - 30,000 executions × 1.5s × 1GB = 45,000 GB-seconds
  - 45,000 × $0.000016 = **$0.72/month**
- **Requests:**
  - First 1M free, so likely **$0/month** for requests
- **Total:** **~$1-5/month** (very conservative)

**Actual Usage Scenarios:**
- **Light Usage** (1-2 consultants, occasional): $1-3/month
- **Moderate Usage** (5-10 consultants, regular): $5-10/month
- **Heavy Usage** (20+ consultants, frequent AI calls): $15-30/month

**Cost Optimization:**
- ✅ Functions are serverless - only pay for execution time
- ✅ No idle costs
- ✅ Automatic scaling
- ⚠️ AI-powered endpoints (recommendations, classification) increase execution time
- ⚠️ Consider caching AI responses to reduce calls

---

### 3. Azure Storage Account (Standard_LRS) - **~$5-10/month** 💰

**Current Setup:** Standard_LRS storage account

**Components:**
- **Table Storage** (Controls, TenantTools, Evidence metadata)
- **Blob Storage** (Evidence files, CSVs, exports)

**Pricing Model:**
- **Storage:** $0.0184 per GB/month (first 50 TB)
- **Transactions:** $0.004 per 10,000 transactions
- **Data Transfer:** Outbound data transfer (first 5 GB free, then $0.087/GB)

**Assumptions for Estimation:**
- **Table Storage:**
  - Controls: ~1,000 controls × 2KB = ~2 MB
  - TenantTools: ~100 tools × 1KB = ~100 KB
  - Evidence metadata: ~500 records × 1KB = ~500 KB
  - **Total:** ~3 MB
- **Blob Storage:**
  - Evidence files: ~500 files × 2 MB average = ~1 GB
  - CSV exports: ~50 files × 1 MB = ~50 MB
  - **Total:** ~1.1 GB
- **Total Storage:** ~1.1 GB
- **Monthly Transactions:** 50,000 (reads/writes)

**Cost Calculation:**
- **Storage:** 1.1 GB × $0.0184 = **$0.02/month**
- **Transactions:** 50,000 ÷ 10,000 × $0.004 = **$0.02/month**
- **Data Transfer:** Assuming 2 GB/month outbound = 2 GB × $0.087 = **$0.17/month** (after first 5 GB free)
- **Total:** **~$0.20-1/month** (very conservative)

**Actual Usage Scenarios:**
- **Light Usage:** $1-2/month (1-2 GB storage, 20K transactions)
- **Moderate Usage:** $3-5/month (5 GB storage, 100K transactions)
- **Heavy Usage:** $8-15/month (20 GB storage, 500K transactions, evidence files)

**Cost Optimization:**
- ✅ Evidence files can be large - consider lifecycle policies to archive old evidence
- ✅ Enable blob soft delete for 30 days (minimal cost)
- ✅ Consider using Cool tier for old evidence (50% cheaper storage)

---

### 4. Azure OpenAI (Optional) - **~$0-50/month** 💰💰

**Current Setup:** Optional - only used when AI features are enabled

**Pricing Model:**
- **GPT-4 Turbo:** $0.01 per 1K input tokens, $0.03 per 1K output tokens
- **GPT-3.5 Turbo:** $0.0015 per 1K input tokens, $0.002 per 1K output tokens
- **GPT-4o:** $0.005 per 1K input tokens, $0.015 per 1K output tokens (recommended)

**Assumptions for Estimation:**
- Using **GPT-4o** (best cost/performance)
- **Average AI calls per month:**
  - Recommendations: 500 calls × 2K tokens input + 1K tokens output = 1.5M tokens
  - Evidence classification: 200 calls × 1K tokens input + 500 tokens output = 300K tokens
  - Report summaries: 50 calls × 5K tokens input + 2K tokens output = 350K tokens
  - **Total:** ~2.15M tokens/month

**Cost Calculation:**
- **Input:** 1.35M tokens × $0.005/1K = **$6.75/month**
- **Output:** 800K tokens × $0.015/1K = **$12.00/month**
- **Total:** **~$18.75/month**

**Actual Usage Scenarios:**
- **Light Usage** (AI disabled or minimal): **$0/month**
- **Moderate Usage** (AI enabled, occasional): **$10-25/month**
- **Heavy Usage** (AI enabled, frequent): **$50-100/month**

**Cost Optimization:**
- ⚠️ **AI is the biggest variable cost** - can be 0 if disabled
- ✅ Cache AI recommendations to avoid regenerating
- ✅ Use GPT-4o instead of GPT-4 Turbo (50% cheaper)
- ✅ Consider rate limiting AI endpoints
- ✅ Make AI features opt-in (already implemented with `?ai=true`)

---

### 5. Azure Key Vault (Optional) - **~$0-1/month** 💰

**Current Setup:** Optional - only if using Key Vault for secrets

**Pricing Model:**
- **Standard tier:** $0.03 per 10,000 operations
- **Premium tier:** $0.15 per 10,000 operations (includes HSM)

**Assumptions:**
- Using Standard tier
- 10,000 operations/month (secret reads)

**Cost Calculation:**
- 10,000 operations × $0.03/10,000 = **$0.03/month**

**Cost:** **~$0-1/month** (negligible)

---

## Total Monthly Cost Summary

### Scenario 1: Minimal Usage (AI Disabled) - **$1-5/month** ✅

| Component | Cost |
|-----------|------|
| Static Web Apps (Free) | $0 |
| Azure Functions | $1-3 |
| Storage Account | $1-2 |
| Azure OpenAI | $0 |
| Key Vault | $0 |
| **Total** | **$2-5/month** |

### Scenario 2: Moderate Usage (AI Enabled) - **$15-35/month** 💰

| Component | Cost |
|-----------|------|
| Static Web Apps (Free) | $0 |
| Azure Functions | $5-10 |
| Storage Account | $3-5 |
| Azure OpenAI | $10-25 |
| Key Vault | $0-1 |
| **Total** | **$18-41/month** |

### Scenario 3: Heavy Usage (AI Enabled, High Volume) - **$40-100/month** 💰💰

| Component | Cost |
|-----------|------|
| Static Web Apps (Free) | $0 |
| Azure Functions | $15-30 |
| Storage Account | $8-15 |
| Azure OpenAI | $50-100 |
| Key Vault | $1 |
| **Total** | **$74-146/month** |

---

## Cost Optimization Recommendations

### ✅ Already Optimized (Current Architecture)

1. **Serverless Functions** - Only pay for execution time, no idle costs
2. **Free Static Web Apps** - No hosting costs
3. **Standard_LRS Storage** - Most cost-effective tier
4. **Consumption-based pricing** - Scales with usage
5. **AI features are optional** - Can be disabled to save costs

### 🎯 Additional Optimizations

1. **AI Cost Management:**
   - ✅ Cache AI recommendations (already implemented)
   - ⚠️ Consider rate limiting AI endpoints
   - ⚠️ Use GPT-4o instead of GPT-4 Turbo
   - ⚠️ Batch AI requests when possible

2. **Storage Optimization:**
   - ⚠️ Implement lifecycle policies for evidence (move old files to Cool tier)
   - ⚠️ Archive evidence older than 180 days (per ADR 0005)
   - ⚠️ Compress CSV exports before storage

3. **Function Optimization:**
   - ⚠️ Reduce function execution time (optimize code)
   - ⚠️ Use appropriate memory allocation (1 GB is default)
   - ⚠️ Cache frequently accessed data (seeds, catalogs)

4. **Monitoring:**
   - ⚠️ Set up Azure Cost Alerts
   - ⚠️ Monitor AI token usage
   - ⚠️ Track storage growth

---

## Comparison with Alternatives

### Current Architecture (SWA + Functions + Storage)
**Cost:** $2-35/month (minimal to moderate usage)

### Alternative: App Service + Cosmos DB
**Estimated Cost:** $50-200/month
- App Service Basic: $13/month
- Cosmos DB Serverless: $25-100/month
- Storage: $5-10/month

### Alternative: AKS + Managed Postgres
**Estimated Cost:** $200-500/month
- AKS cluster: $100-200/month
- Managed Postgres: $50-150/month
- Load balancer: $20-50/month

**✅ Current architecture is ~10-20x cheaper than alternatives**

---

## Cost Monitoring Setup

### Recommended Azure Cost Alerts

1. **Total Monthly Cost Alert:** > $50/month
2. **AI/OpenAI Cost Alert:** > $30/month
3. **Storage Cost Alert:** > $10/month
4. **Function Cost Alert:** > $20/month

### Azure Cost Management Dashboard

1. Go to Azure Portal → Cost Management + Billing
2. Create a budget for the resource group
3. Set up email alerts
4. Review cost analysis weekly

---

## Conclusion

**Current architecture is highly cost-optimized** ✅

- **Minimal usage (no AI):** $2-5/month
- **Moderate usage (with AI):** $15-35/month
- **Heavy usage:** $40-100/month

**Key Cost Drivers:**
1. **Azure OpenAI** (if used) - 50-70% of total cost
2. **Azure Functions** - 20-30% of total cost
3. **Storage** - 10-20% of total cost

**Recommendations:**
1. ✅ Current architecture is already the most economical approach
2. ✅ Monitor AI usage and costs closely
3. ✅ Consider implementing caching for AI responses
4. ✅ Set up cost alerts to track spending
5. ✅ Archive old evidence to reduce storage costs

---

## Next Steps

1. **Set up Azure Cost Management** budget and alerts
2. **Monitor first month** to establish baseline costs
3. **Implement caching** for AI recommendations
4. **Review storage lifecycle** policies after 3 months
5. **Optimize function execution time** if costs exceed $20/month

---

**Note:** All prices are estimates based on Azure pricing as of 2025. Actual costs may vary based on:
- Usage patterns
- Data volume
- Geographic region
- Azure pricing changes
- Discounts or enterprise agreements

