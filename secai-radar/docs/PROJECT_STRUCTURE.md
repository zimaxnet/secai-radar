# SecAI Radar Project Structure

## Directory Organization

This document describes the proper organization of files in the SecAI Radar project.

## Root Directory (`/`)

**ONLY** these files should be in root:
- `README.md` - Project README
- `.gitignore` - Git ignore rules
- `.cursorrules` - Cursor AI rules

**All other files should be in appropriate subdirectories.**

## Application Root (`secai-radar/`)

```
secai-radar/
├── README.md                    # Application README (ONLY this file in root)
├── .gitignore                   # Git ignore rules
├── .cursorrules                 # Cursor AI rules
├── backend/                     # FastAPI backend
│   ├── main.py                  # Application entry point
│   ├── requirements.txt         # Python dependencies
│   └── src/
│       ├── agents/              # AI agent implementations
│       ├── integrations/        # External integrations
│       ├── routes/              # API routes
│       ├── services/            # Business logic services
│       └── orchestrator.py      # Agent orchestrator
├── frontend/                    # React frontend
│   ├── package.json             # Node dependencies
│   └── src/
│       ├── components/          # React components
│       ├── pages/               # Page components
│       ├── services/            # API clients
│       └── data/                # Static data
├── docs/                        # All documentation
│   ├── wiki/                    # Wiki documentation (for gh-pages)
│   ├── summaries/               # Implementation summaries
│   └── ... (other docs)
├── scripts/                     # Utility scripts
├── infra/                       # Infrastructure as code
├── seeds/                       # Seed data
├── config/                      # Configuration files
└── archive_v1/                  # Archived v1 code
```

## Writing Guidelines

**When creating files:**
1. ✅ Write to appropriate subdirectories
2. ❌ NEVER write to root directory (except README.md)
3. ✅ Use `secai-radar/backend/` for backend code
4. ✅ Use `secai-radar/frontend/` for frontend code
5. ✅ Use `secai-radar/docs/` for documentation
6. ✅ Use `docs/` (root docs) for root-level documentation

**File Locations:**
- Backend code → `secai-radar/backend/`
- Frontend code → `secai-radar/frontend/`
- Documentation → `secai-radar/docs/` or `docs/`
- Scripts → `secai-radar/scripts/`
- Config → `secai-radar/config/`

---

**Last Updated**: 2025-01-15

