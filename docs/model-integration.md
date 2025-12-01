# SecAI Radar — Model Layer Integration Guide

> Guide for integrating AI models into the SecAI Radar Model Layer according to the blueprint architecture.

---

## Overview

The Model Layer provides **role-based access** to AI models, not brand-based. This allows models to be swapped without changing orchestrator code. Models are configured in `config/models.yaml` and accessed by role:

- **`reasoning_model`**: Multi-step security analysis and orchestration
- **`classification_model`**: Maps evidence to controls/domains
- **`generation_model`**: Generates human-readable reports

---

## Architecture Integration

### Model Layer in the 5-Layer Architecture

According to the blueprint, the Model Layer sits between the Infrastructure Layer and the Orchestration Layer:

```
Infrastructure Layer (API + Worker)
    ↓
Model Layer ← You are here (role-based model access)
    ↓
Orchestration Layer (uses models by role)
    ↓
Data Layer (Bronze/Silver/Gold)
    ↓
Application Layer (Web UI)
```

### Role-Based Design

Models are **not** accessed by brand/provider name. Instead, they are accessed by **role**:

```python
# ❌ Bad: Brand-based access
model = AzureOpenAI("gpt-5-chat")

# ✅ Good: Role-based access
model = get_model("reasoning_model")
```

This allows:
- **Swappability**: Change models without changing orchestrator code
- **Flexibility**: Use different models for different roles
- **Testing**: Easily swap in test models or fallbacks

---

## GPT-5-Chat Integration

### Configuration

The GPT-5-chat model is configured in `config/models.yaml`:

```yaml
roles:
  reasoning_model:
    provider: "azure_openai"
    deployment: "gpt-5-chat"
    account: "zimax"
    # ... other config
```

### Deployment Details

From the Azure OpenAI deployment:
- **Deployment**: `gpt-5-chat`
- **Account**: `zimax`
- **Resource Group**: `zimax-ai`
- **Subscription**: `23f4e2c5-0667-4514-8e2e-f02ca7880c95`
- **Endpoint**: `https://zimax.openai.azure.com`

### Role Assignments

GPT-5-chat can be assigned to one or more roles:

1. **All Roles** (Recommended for MVP):
   - Same model, different prompts/parameters
   - Cost-effective for MVP
   - Consistent behavior across roles

2. **Specific Roles**:
   - Different models for different roles
   - Optimize for specific tasks
   - More complex configuration

For MVP, we assign GPT-5-chat to **all three roles** with role-specific prompts and parameters.

---

## Usage Patterns

### 1. Direct Model Access

```python
from models import get_model

# Get model by role
reasoning_model = get_model("reasoning_model")
classification_model = get_model("classification_model")
generation_model = get_model("generation_model")
```

### 2. Model Layer Abstraction

```python
from models import get_model_layer

model_layer = get_model_layer()

# Use role-based methods
result = await model_layer.reasoning(
    prompt="Analyze security posture",
    context={"evidence": [...]}
)

classification = await model_layer.classify(
    evidence={"resource_type": "nsg", ...}
)

content = await model_layer.generate(
    section_type="executive_summary",
    data={"findings": [...]}
)
```

### 3. Orchestrator Integration

```python
from models import get_model_layer

async def run_assessment():
    model_layer = get_model_layer()
    
    # Step 1: Plan (reasoning)
    plan = await model_layer.reasoning(
        prompt="Plan assessment for network security",
        context={"scope": ["network"]}
    )
    
    # Step 2: Classify evidence (classification)
    classification = await model_layer.classify(evidence)
    
    # Step 3: Generate report (generation)
    report = await model_layer.generate(
        section_type="findings",
        data={"controls": [...]}
    )
    
    return report
```

---

## Authentication

### Azure AD (Recommended)

The Model Layer supports Azure AD authentication via `DefaultAzureCredential`:

```python
# Automatically uses:
# 1. Managed Identity (if running in Azure)
# 2. Service Principal (if env vars set)
# 3. Azure CLI credentials (if logged in locally)
```

**Environment Variables** (if using Service Principal):
```bash
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
```

### API Key (Alternative)

For local development or testing:

```bash
AZURE_OPENAI_API_KEY=...
```

Set `auth_method: "api_key"` in `config/models.yaml`.

---

## Model Parameters

Each role has role-specific parameters:

### Reasoning Model
- **Temperature**: 0.3 (lower for analytical reasoning)
- **Max Tokens**: 4000
- **Use Case**: Multi-step security analysis, planning, review

### Classification Model
- **Temperature**: 0.1 (very low for consistency)
- **Max Tokens**: 2000
- **Use Case**: Evidence classification, control mapping

### Generation Model
- **Temperature**: 0.7 (higher for natural language)
- **Max Tokens**: 8000
- **Use Case**: Report generation, narrative writing

---

## Error Handling and Fallbacks

### Fallback Models

Configure fallback models in `config/models.yaml`:

```yaml
fallbacks:
  reasoning_model:
    provider: "azure_openai"
    deployment: "gpt-4"
    # ... config
```

### Error Handling

```python
from models import get_model_layer

model_layer = get_model_layer()

try:
    result = await model_layer.reasoning(prompt="...")
except Exception as e:
    # Handle error (retry, fallback, etc.)
    print(f"Model error: {e}")
```

---

## Best Practices

### 1. Use Roles, Not Brands

```python
# ❌ Don't access models by brand
model = get_gpt5_model()

# ✅ Access models by role
model = get_model("reasoning_model")
```

### 2. Use Model Layer Methods

```python
# ❌ Don't call providers directly
provider = AzureOpenAIProvider(...)
result = await provider.chat_completion(...)

# ✅ Use Model Layer abstraction
model_layer = get_model_layer()
result = await model_layer.reasoning(...)
```

### 3. Provide Context

```python
# ✅ Good: Provide context
result = await model_layer.reasoning(
    prompt="Analyze security posture",
    context={
        "evidence": [...],
        "findings": [...],
        "scope": [...]
    }
)
```

### 4. Handle Errors Gracefully

```python
try:
    result = await model_layer.classify(evidence)
    if result["classification"]:
        # Use classification
        pass
    else:
        # Handle classification failure
        pass
except Exception as e:
    # Log error and handle gracefully
    logger.error(f"Classification failed: {e}")
```

---

## Testing

### Mock Models

For testing, you can create mock providers:

```python
from models.providers import ModelProvider

class MockProvider(ModelProvider):
    async def chat_completion(self, messages, system_prompt, parameters, **kwargs):
        return {
            "content": "Mock response",
            "model": "mock",
            "usage": {"total_tokens": 100}
        }
```

### Unit Tests

```python
import pytest
from models import get_model_layer

@pytest.mark.asyncio
async def test_reasoning():
    model_layer = get_model_layer()
    result = await model_layer.reasoning(
        prompt="Test prompt",
        context={"test": "data"}
    )
    assert "content" in result
```

---

## Monitoring and Observability

### Usage Tracking

The Model Layer returns usage information:

```python
result = await model_layer.reasoning(...)
usage = result["usage"]
print(f"Tokens used: {usage['total_tokens']}")
```

### Logging

Log model calls for observability:

```python
import logging

logger = logging.getLogger("models")

async def reasoning_with_logging(prompt, context):
    logger.info(f"Reasoning call: {prompt[:100]}")
    result = await model_layer.reasoning(prompt, context)
    logger.info(f"Tokens used: {result['usage']['total_tokens']}")
    return result
```

---

## References

- `blueprint.md` — Architecture overview
- `config/models.yaml` — Model configuration
- `src/models/` — Model Layer implementation
- `src/orchestrator/example_usage.py` — Usage examples

