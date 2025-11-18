# RAG Integration Status

## Overview

The SecAI Radar multi-agent system is **fully integrated** with Google File Search for RAG (Retrieval-Augmented Generation). Agents can query the knowledge base to retrieve relevant information from Azure CAF, MCA guides, and security best practices.

## Integration Status: ✅ COMPLETE

### Components Implemented

1. **✅ Google File Search Retriever** (`src/rag/google_file_search.py`)
   - Fully managed RAG using Gemini API
   - Automatic chunking, embeddings, and vector search
   - File store management

2. **✅ Agentic Retrieval** (`src/rag/agentic_retrieval.py`)
   - Agents decide when to search
   - Agents generate their own queries
   - Relevance evaluation

3. **✅ RAG Factory** (`src/rag/factory.py`)
   - Auto-configuration from `config/rag.yaml`
   - Environment variable support
   - Easy initialization

4. **✅ Agent Integration**
   - All agents accept `rag_retriever` parameter
   - BaseAgent has `query_rag()` method
   - Agents use RAG in their workflows (e.g., Aris Thorne queries CAF)

5. **✅ Orchestrator Integration**
   - LangGraphConfig accepts `rag_retriever`
   - Graph passes RAG to all agents
   - Initialize helper function available

## Current Usage

### Agents Using RAG

**Dr. Aris Thorne** (Principal Architect) uses RAG to:
- Query CAF knowledge base for assessment checklists
- Retrieve Azure Landing Zone guidance
- Access security best practices

**Leo Vance** (Security Architect - IAM) uses RAG to:
- Query MCA billing hierarchy documentation
- Retrieve Entra ID best practices

### Example Agent RAG Usage

```python
# In Aris Thorne's _query_caf_knowledge method:
caf_query = "Azure Cloud Adoption Framework security assessment checklist"
rag_context = await self.query_rag(caf_query, {
    "phase": "assessment",
    "tenant_id": state.get("tenant_id")
})
```

## Setup Required

### 1. Environment Variables

```bash
export GOOGLE_API_KEY="your-google-api-key"
export GOOGLE_FILE_STORE_ID="your-file-store-id"  # Optional
```

### 2. Configuration

The system reads from `config/rag.yaml`:
- Provider: `google_file_search` (default)
- Agentic retrieval: Enabled by default
- Auto query generation: Enabled

### 3. Initialize RAG

**Option A: Auto-initialization (Recommended)**
```python
from src.orchestrator.initialize import initialize_orchestrator

# Automatically initializes RAG from config
graph = initialize_orchestrator()
```

**Option B: Manual initialization**
```python
from src.rag.factory import get_rag_retriever
from src.models import get_model_layer

model_layer = get_model_layer()
rag_retriever = get_rag_retriever(model_layer=model_layer)

# Pass to orchestrator
from src.orchestrator import LangGraphConfig, StateManager
config = LangGraphConfig(
    model_layer=model_layer,
    state_manager=StateManager(),
    rag_retriever=rag_retriever
)
```

## Knowledge Base Setup

### Upload Documents to Google File Search

Documents need to be uploaded to the Google File Search file store before agents can query them.

**Recommended Documents:**
1. Azure Cloud Adoption Framework (CAF)
2. Azure Well-Architected Framework (WAF)
3. Microsoft Customer Agreement (MCA) guides
4. Azure Security Best Practices

**Upload Script Example:**
```python
from src.rag import GoogleFileSearchRetriever

retriever = GoogleFileSearchRetriever()

# Upload a document
await retriever.upload_document(
    document_path="./docs/caf-guide.pdf",
    metadata={"display_name": "Azure CAF Guide", "type": "caf"}
)

# Or upload text directly
await retriever.upload_text(
    text="Azure CAF content...",
    display_name="CAF Security Checklist"
)
```

## How It Works

### Agentic RAG Flow

1. **Agent decides to search**: Agent determines if knowledge base query is needed
2. **Query generation**: Agent (or model) generates search query from task context
3. **Retrieval**: Google File Search retrieves relevant documents
4. **Relevance evaluation**: Agent evaluates if retrieved content is relevant
5. **Context injection**: Relevant content is injected into agent's prompt

### Example Flow

```
Aris Thorne: "I need to design a Landing Zone"
    ↓
AgenticRetriever.should_retrieve() → True
    ↓
AgenticRetriever.generate_query() → "Azure Landing Zone architecture Zero Trust"
    ↓
GoogleFileSearchRetriever.retrieve() → CAF documentation chunks
    ↓
AgenticRetriever.evaluate_relevance() → True
    ↓
Content injected into Aris's prompt
    ↓
Aris generates architecture design with CAF guidance
```

## Verification

### Check if RAG is Working

1. **Check initialization**:
   ```python
   from src.rag.factory import get_rag_retriever
   retriever = get_rag_retriever()
   if retriever:
       print("✅ RAG initialized")
   else:
       print("❌ RAG not available (check GOOGLE_API_KEY)")
   ```

2. **Test retrieval**:
   ```python
   result = await retriever.retrieve("Azure CAF security")
   print(result)  # Should return relevant content
   ```

3. **Check agent usage**:
   - Look for `query_rag()` calls in agent code
   - Check logs for RAG retrieval events
   - Verify agents are receiving context

## Troubleshooting

### RAG Not Available

**Symptom**: Agents don't retrieve knowledge base content

**Solutions**:
1. Check `GOOGLE_API_KEY` is set
2. Verify `config/rag.yaml` exists and `provider: "google_file_search"`
3. Check file store has documents uploaded
4. Review error logs for RAG initialization errors

### No Results Returned

**Symptom**: `query_rag()` returns `None`

**Solutions**:
1. Verify documents are uploaded to file store
2. Check file store ID matches `GOOGLE_FILE_STORE_ID`
3. Try broader search queries
4. Check Google API quotas/limits

### Agentic Retrieval Not Working

**Symptom**: Agents don't decide to search

**Solutions**:
1. Check `agentic_retrieval.enabled: true` in `config/rag.yaml`
2. Verify Model Layer is available (needed for query generation)
3. Review agent prompts to ensure they trigger retrieval

## Next Steps

1. **Upload Knowledge Base Documents**:
   - Create script to ingest CAF/MCA documentation
   - Upload to Google File Search file store
   - Verify documents are searchable

2. **Test Agent RAG Usage**:
   - Run assessment workflow
   - Verify Aris queries CAF knowledge base
   - Check retrieved context is used in responses

3. **Monitor RAG Performance**:
   - Track retrieval success rate
   - Measure query latency
   - Review relevance of retrieved content

## Configuration Reference

See `config/rag.yaml` for full configuration options:
- Provider selection (Google File Search vs Azure AI Search)
- Agentic retrieval settings
- Document ingestion configuration

