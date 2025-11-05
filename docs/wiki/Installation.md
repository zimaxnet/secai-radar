# Installation Guide

Complete installation guide for SecAI Radar.

---

## Prerequisites

Before installing SecAI Radar, ensure you have:

- **Node.js** 20+ (for web UI)
- **Python** 3.12+ (for API)
- **Docker** (optional, for containerized deployment)
- **Azure Account** (for cloud deployment)
- **Azure OpenAI** (for AI features)

---

## Installation Methods

### Option 1: Local Development

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/secai-radar.git
cd secai-radar
```

#### 2. Install Web UI Dependencies

```bash
cd web
npm install
```

#### 3. Install API Dependencies

```bash
cd ../api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. Configure Environment

Create `.env` file or configure environment variables:

```bash
# Web UI
VITE_API_BASE=/api
VITE_DEFAULT_TENANT=tenant-alpha

# API
AZURE_OPENAI_API_KEY=your-key
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-secret
AZURE_TENANT_ID=your-tenant-id
```

#### 5. Configure Models

Copy and configure model configuration:

```bash
cp config/models.yaml.example config/models.yaml
# Edit config/models.yaml with your Azure OpenAI details
```

#### 6. Start Services

**Web UI**:
```bash
cd web
npm run dev
```

**API**:
```bash
cd api
func start
```

---

### Option 2: Docker Deployment

#### 1. Build Containers

```bash
docker-compose build
```

#### 2. Configure Environment

Edit `.env` file or set environment variables.

#### 3. Start Services

```bash
docker-compose up -d
```

---

### Option 3: Azure Deployment

#### 1. Azure Static Web Apps (UI)

1. Create Azure Static Web App
2. Configure build settings
3. Deploy from GitHub Actions or manually

#### 2. Azure Functions (API)

1. Create Azure Function App
2. Configure deployment settings
3. Deploy from GitHub Actions or manually

#### 3. Azure Storage (Data)

1. Create Azure Storage Account
2. Configure Table Storage
3. Configure Blob Storage
4. Set up connection strings

#### 4. Azure OpenAI (AI)

1. Create Azure OpenAI resource
2. Deploy GPT-5-chat model
3. Configure in `config/models.yaml`
4. Set up authentication

---

## Configuration

### Model Configuration

Edit `config/models.yaml`:

```yaml
roles:
  reasoning_model:
    provider: "azure_openai"
    deployment: "gpt-5-chat"
    account: "your-account"
    # ... other config
```

### Framework Configuration

Edit `config/frameworks.yaml`:

```yaml
- id: GEN-IAM-001
  domain: "Identity & Access Management"
  title: "Centralize identity and authentication"
  severity: high
```

### Environment Variables

Required environment variables:

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-account.openai.azure.com

# Azure AD (if using)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-secret
AZURE_TENANT_ID=your-tenant-id

# Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
```

See [Configuration](/wiki/Configuration) for detailed configuration options.

---

## Verification

### Check Web UI

1. Open browser to `http://localhost:5173` (or your deployment URL)
2. Verify home page loads
3. Check API connection

### Check API

1. Test health endpoint: `GET /api/health`
2. Test domains endpoint: `GET /api/domains`
3. Verify authentication

### Check AI Models

1. Test model configuration: Check `config/models.yaml`
2. Test model connection: Verify Azure OpenAI access
3. Test role-based access: Use Model Layer

---

## Troubleshooting

### Common Issues

**Web UI not loading**:
- Check Node.js version (20+)
- Check dependencies: `npm install`
- Check port availability

**API not starting**:
- Check Python version (3.12+)
- Check dependencies: `pip install -r requirements.txt`
- Check Azure Functions Core Tools

**Model errors**:
- Check Azure OpenAI configuration
- Verify API keys
- Check deployment status

See [Troubleshooting](/wiki/Troubleshooting) for detailed troubleshooting.

---

## Next Steps

After installation:

1. **Configure Models**: Set up AI models (see [Configuration](/wiki/Configuration))
2. **Set Up Data**: Configure storage and data layers
3. **Import Controls**: Import security controls (see [Controls Guide](/wiki/Controls-Guide))
4. **Configure Tools**: Set up security tools (see [Tools Guide](/wiki/Tools-Guide))
5. **Run Assessment**: Start your first assessment

See [Getting Started](/wiki/Getting-Started) for quick start guide.

---

## Support

For installation issues:
- Check [Troubleshooting](/wiki/Troubleshooting) guide
- Review [FAQ](/wiki/FAQ) for common questions
- Open an issue on GitHub

---

**Related**: [Configuration](/wiki/Configuration) | [Getting Started](/wiki/Getting-Started)

