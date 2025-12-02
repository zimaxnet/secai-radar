---
layout: default
title: Configuration
---

# Configuration Guide

Complete configuration guide for SecAI Radar.

---

## Overview

SecAI Radar is configured through:
- **Configuration Files**: YAML files in `config/` directory
- **Environment Variables**: Environment-specific settings
- **Runtime Configuration**: Application-level settings

---

## Configuration Files

### Model Configuration

**File**: `config/models.yaml`

Configure AI models and their roles:

```yaml
roles:
  reasoning_model:
    provider: "azure_openai"
    deployment: "gpt-5-chat"
    account: "your-account"
    resource_group: "your-resource-group"
    subscription_id: "your-subscription-id"
    tenant_id: "your-tenant-id"
    parameters:
      temperature: 0.3
      max_tokens: 4000
    system_prompt: |
      You are a security analysis expert...
```

**Key Settings**:
- `provider`: Model provider (e.g., "azure_openai")
- `deployment`: Model deployment name
- `account`: Azure OpenAI account name
- `parameters`: Model-specific parameters
- `system_prompt`: System prompt for the model

See [Model Integration](../model-integration.md) for detailed configuration.

### Framework Configuration

**File**: `config/frameworks.yaml`

Define security control frameworks:

```yaml
- id: GEN-IAM-001
  domain: "Identity & Access Management"
  title: "Centralize identity and authentication"
  severity: high
  description: "Ensure identity and authentication are centralized"
  
- id: GEN-LM-001
  domain: "Logging & Monitoring"
  title: "Enable audit and diagnostic logging"
  severity: high
  description: "Enable comprehensive logging"
```

**Key Settings**:
- `id`: Control identifier (e.g., "GEN-IAM-001")
- `domain`: Security domain
- `title`: Control title
- `severity`: Control severity (high, medium, low)
- `description`: Control description

---

## Environment Variables

### Azure OpenAI

```bash
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-account.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Azure AD Authentication

```bash
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### Storage

```bash
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_ACCOUNT_NAME=your-account-name
AZURE_STORAGE_ACCOUNT_KEY=your-account-key
```

### Application

```bash
# Web UI
VITE_API_BASE=/api
VITE_DEFAULT_TENANT=tenant-alpha

# API
API_BASE_URL=http://localhost:7071
LOG_LEVEL=INFO
```

---

## Runtime Configuration

### API Configuration

**File**: `api/local.settings.json` (local development)

```json
{
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  },
  "Host": {
    "LocalHttpPort": 7071
  }
}
```

### Web UI Configuration

**File**: `web/.env` (local development)

```bash
VITE_API_BASE=/api
VITE_DEFAULT_TENANT=tenant-alpha
```

---

## Authentication Configuration

### Azure AD Authentication

1. **Create App Registration**:
   - Register application in Azure AD
   - Configure redirect URIs
   - Set up API permissions

2. **Configure Secrets**:
   - Create client secret
   - Set environment variables
   - Configure in application

3. **Configure Roles**:
   - Define application roles
   - Assign roles to users/groups
   - Use roles in application

### API Key Authentication

1. **Generate API Key**:
   - Create API key in Azure OpenAI
   - Store securely
   - Set environment variable

2. **Configure Application**:
   - Set `AZURE_OPENAI_API_KEY`
   - Configure in `config/models.yaml`
   - Test connection

---

## Storage Configuration

### Azure Table Storage

**Configuration**:
- Create Azure Storage Account
- Create Table Storage
- Configure connection string

**Tables**:
- `Controls`: Security controls
- `TenantTools`: Tool configurations
- `AssessmentRuns`: Assessment runs

### Azure Blob Storage

**Configuration**:
- Create Azure Storage Account
- Create Blob Containers
- Configure connection string

**Containers**:
- `bronze`: Raw evidence
- `evidence`: Evidence files
- `reports`: Generated reports

---

## Model Configuration

### Azure OpenAI Configuration

1. **Create Resource**:
   - Create Azure OpenAI resource
   - Deploy GPT-5-chat model
   - Note deployment name

2. **Configure in `config/models.yaml`**:
   ```yaml
   roles:
     reasoning_model:
       provider: "azure_openai"
       deployment: "gpt-5-chat"
       account: "your-account"
   ```

3. **Set Authentication**:
   - API key or Azure AD
   - Configure in environment variables
   - Test connection

### Model Roles

Configure three model roles:

1. **Reasoning Model**: Multi-step security analysis
2. **Classification Model**: Evidence classification
3. **Generation Model**: Report generation

Each role can use the same model with different prompts and parameters.

---

## Best Practices

### 1. Environment Separation

- **Development**: Use local settings
- **Staging**: Use staging environment variables
- **Production**: Use secure key vault

### 2. Secrets Management

- **Never commit secrets**: Use environment variables
- **Use Key Vault**: Store secrets in Azure Key Vault
- **Rotate regularly**: Rotate secrets regularly

### 3. Configuration Validation

- **Validate on startup**: Check configuration on startup
- **Fail fast**: Fail early if configuration invalid
- **Log errors**: Log configuration errors

### 4. Documentation

- **Document settings**: Document all configuration options
- **Provide examples**: Include example configurations
- **Keep updated**: Keep documentation current

---

## Troubleshooting

### Configuration Issues

**Model not working**:
- Check Azure OpenAI configuration
- Verify API keys
- Check deployment status

**Storage errors**:
- Check connection strings
- Verify storage account exists
- Check permissions

**Authentication failures**:
- Check Azure AD configuration
- Verify client secrets
- Check permissions

See [Troubleshooting](/wiki/Troubleshooting) for detailed troubleshooting.

---

## Examples

### Complete Configuration Example

See example configurations in:
- `config/models.yaml.example`
- `config/frameworks.yaml.example`
- `.env.example`

---

**Related**: [Installation](/wiki/Installation) | [Model Integration](../model-integration.md)
