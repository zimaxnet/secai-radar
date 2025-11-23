# SecAI Radar Project Structure

## Root Directory Structure

```
SecAI/
├── README.md                    # Project root README
├── .github/                     # GitHub workflows and templates
├── docs/                        # All documentation
│   ├── README.md               # Documentation index
│   ├── wiki/                   # Wiki documentation (for gh-pages)
│   ├── summaries/              # Implementation summaries
│   └── guides/                 # Comprehensive guides
├── analysis/                    # Analysis scripts and outputs
│   └── security_domains/       # Security domain analysis
├── sanitized/                   # Sanitized templates and reports
└── secai-radar/                 # Main application repository
```

## SecAI Radar Application Structure

```
secai-radar/
├── README.md                    # Application README
├── .gitignore                   # Git ignore rules
├── .cursorrules                 # Cursor AI rules
├── backend/                     # FastAPI backend
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   └── src/
│       ├── agents/             # AI agent implementations
│       ├── integrations/       # External service integrations
│       ├── routes/             # API route handlers
│       ├── services/           # Business logic services
│       └── orchestrator.py     # Agent orchestrator
├── frontend/                    # React frontend
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── src/
│       ├── components/         # React components
│       ├── pages/              # Page components
│       ├── services/           # API client services
│       └── data/               # Static data
├── docs/                        # Application documentation
│   ├── wiki/                   # Wiki pages
│   ├── summaries/              # Implementation summaries
│   └── ... (other docs)
├── scripts/                     # Utility scripts
├── infra/                       # Infrastructure as code
│   ├── main.bicep              # Bicep templates
│   └── parameters/             # Bicep parameters
├── seeds/                       # Seed data
│   ├── control_requirements.json
│   ├── tool_capabilities.json
│   └── vendor_tools.json
├── config/                      # Configuration files
│   ├── agent_personas.yaml
│   └── rag.yaml
├── archive_v1/                  # Archived v1 code
│   ├── api/                    # Azure Functions (v1)
│   ├── web/                    # Old frontend (v1)
│   └── docs/                   # Archived documentation
└── src/                         # Shared source (if any)
    ├── models/
    ├── orchestrator/
    ├── rag/
    └── visualization/
```

## File Organization Rules

### Root Directory
- **ONLY** `README.md` should be in root
- All other files should be in appropriate subdirectories

### Documentation
- **Wiki documentation**: `docs/wiki/` (for GitHub Pages)
- **Implementation summaries**: `docs/summaries/`
- **Comprehensive guides**: `docs/guides/`
- **Application docs**: `secai-radar/docs/`

### Code
- **Backend code**: `secai-radar/backend/`
- **Frontend code**: `secai-radar/frontend/`
- **Archived code**: `secai-radar/archive_v1/`

### Configuration
- **Infrastructure**: `secai-radar/infra/`
- **Config files**: `secai-radar/config/`
- **Seed data**: `secai-radar/seeds/`
- **Scripts**: `secai-radar/scripts/`

## Writing Guidelines

When creating new files:
1. ✅ Write to appropriate subdirectories
2. ❌ Never write to root directory (except README.md)
3. ✅ Use `docs/` for all documentation
4. ✅ Use `secai-radar/backend/` for backend code
5. ✅ Use `secai-radar/frontend/` for frontend code

---

**Last Updated**: 2025-01-15

